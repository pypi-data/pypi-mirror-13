##############################################################################
# MDTraj: A Python Library for Loading, Saving, and Manipulating
#         Molecular Dynamics Trajectories.
# Copyright 2012-2015 Stanford University and the Authors
#
# Authors: Robert McGibbon
# Contributors: Kyle A Beauchamp, Jason Swails
#
# MDTraj is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with MDTraj. If not, see <http://www.gnu.org/licenses/>.
##############################################################################


##############################################################################
# Imports
##############################################################################

from __future__ import print_function, division
import numpy as np
from mdtraj.utils import ensure_type
from mdtraj.utils.six.moves import range
from mdtraj.geometry import _geometry


__all__ = ['compute_distances', 'compute_displacements',
           'compute_center_of_mass']

##############################################################################
# Functions
##############################################################################


def compute_distances(traj, atom_pairs, periodic=True, opt=True):
    """Compute the distances between pairs of atoms in each frame.

    Parameters
    ----------
    traj : Trajectory
        An mtraj trajectory.
    atom_pairs : np.ndarray, shape=(num_pairs, 2), dtype=int
        Each row gives the indices of two atoms involved in the interaction.
    periodic : bool, default=True
        If `periodic` is True and the trajectory contains unitcell
        information, we will compute distances under the minimum image
        convention.
    opt : bool, default=True
        Use an optimized native library to calculate distances. Our optimized
        SSE minimum image convention calculation implementation is over 1000x
        faster than the naive numpy implementation.

    Returns
    -------
    distances : np.ndarray, shape=(n_frames, num_pairs), dtype=float
        The distance, in each frame, between each pair of atoms.
    """
    xyz = ensure_type(traj.xyz, dtype=np.float32, ndim=3, name='traj.xyz', shape=(None, None, 3), warn_on_cast=False)
    pairs = ensure_type(atom_pairs, dtype=np.int32, ndim=2, name='atom_pairs', shape=(None, 2), warn_on_cast=False)
    if not np.all(np.logical_and(pairs < traj.n_atoms, pairs >= 0)):
        raise ValueError('atom_pairs must be between 0 and %d' % traj.n_atoms)

    if len(pairs) == 0:
        return np.zeros((len(xyz), 0), dtype=np.float32)

    if periodic and traj._have_unitcell:
        box = ensure_type(traj.unitcell_vectors, dtype=np.float32, ndim=3, name='unitcell_vectors', shape=(len(xyz), 3, 3),
                          warn_on_cast=False)
        orthogonal = np.allclose(traj.unitcell_angles, 90)
        if opt:
            out = np.empty((xyz.shape[0], pairs.shape[0]), dtype=np.float32)
            _geometry._dist_mic(xyz, pairs, box.transpose(0, 2, 1).copy(), out, orthogonal)
            return out
        else:
            return _distance_mic(xyz, pairs, box.transpose(0, 2, 1), orthogonal)

    # either there are no unitcell vectors or they dont want to use them
    if opt:
        out = np.empty((xyz.shape[0], pairs.shape[0]), dtype=np.float32)
        _geometry._dist(xyz, pairs, out)
        return out
    else:
        return _distance(xyz, pairs)


def compute_displacements(traj, atom_pairs, periodic=True, opt=True):
    """Compute the displacement vector between pairs of atoms in each frame of a trajectory.

    Parameters
    ----------
    traj : Trajectory
        Trajectory to compute distances in
    atom_pairs : np.ndarray, shape[num_pairs, 2], dtype=int
        Each row gives the indices of two atoms.
    periodic : bool, default=True
        If `periodic` is True and the trajectory contains unitcell
        information, we will compute distances under the minimum image
        convention.
    opt : bool, default=True
        Use an optimized native library to calculate distances. Our
        optimized minimum image convention calculation implementation is
        over 1000x faster than the naive numpy implementation.

    Returns
    -------
    displacements : np.ndarray, shape=[n_frames, n_pairs, 3], dtype=float32
         The displacememt vector, in each frame, between each pair of atoms.
    """
    xyz = ensure_type(traj.xyz, dtype=np.float32, ndim=3, name='traj.xyz', shape=(None, None, 3), warn_on_cast=False)
    pairs = ensure_type(np.asarray(atom_pairs), dtype=np.int32, ndim=2, name='atom_pairs', shape=(None, 2), warn_on_cast=False)
    if not np.all(np.logical_and(pairs < traj.n_atoms, pairs >= 0)):
        raise ValueError('atom_pairs must be between 0 and %d' % traj.n_atoms)

    if periodic and traj._have_unitcell:
        box = ensure_type(traj.unitcell_vectors, dtype=np.float32, ndim=3, name='unitcell_vectors', shape=(len(xyz), 3, 3),
                          warn_on_cast=False)
        orthogonal = np.allclose(traj.unitcell_angles, 90)
        if opt:
            out = np.empty((xyz.shape[0], pairs.shape[0], 3), dtype=np.float32)
            _geometry._dist_mic_displacement(xyz, pairs, box.transpose(0, 2, 1).copy(), out, orthogonal)
            return out
        else:
            return _displacement_mic(xyz, pairs, box.transpose(0, 2, 1), orthogonal)

    # either there are no unitcell vectors or they dont want to use them
    if opt:
        out = np.empty((xyz.shape[0], pairs.shape[0], 3), dtype=np.float32)
        _geometry._dist_displacement(xyz, pairs, out)
        return out
    return _displacement(xyz, pairs)


def compute_center_of_mass(traj):
    """Compute the center of mass for each frame.

    Parameters
    ----------
    traj : Trajectory
        Trajectory to compute center of mass for

    Returns
    -------
    com : np.ndarray, shape=(n_frames, 3)
         Coordinates of the center of mass for each frame
    """

    com = np.zeros((traj.n_frames, 3))
    masses = np.array([a.element.mass for a in traj.top.atoms])
    masses /= masses.sum()

    for i, x in enumerate(traj.xyz):
        com[i, :] = x.astype('float64').T.dot(masses)
    return com


##############################################################################
# pure python implementation of the core routines
##############################################################################


def _distance(xyz, pairs):
    "Distance between pairs of points in each frame"
    delta = np.diff(xyz[:, pairs], axis=2)[:, :, 0]
    return (delta ** 2.).sum(-1) ** 0.5


def _displacement(xyz, pairs):
    "Displacement vector between pairs of points in each frame"
    value = np.diff(xyz[:, pairs], axis=2)[:, :, 0]
    assert value.shape == (xyz.shape[0], pairs.shape[0], 3), 'v.shape %s, xyz.shape %s, pairs.shape %s' % (str(value.shape), str(xyz.shape), str(pairs.shape))
    return value


def _distance_mic(xyz, pairs, box_vectors, orthogonal):
    """Distance between pairs of points in each frame under the minimum image
    convention for periodic boundary conditions.

    The computation follows scheme B.9 in Tukerman, M. "Statistical
    Mechanics: Theory and Molecular Simulation", 2010.

    This is a slow pure python implementation, mostly for testing.
    """
    out = np.empty((xyz.shape[0], pairs.shape[0]), dtype=np.float32)
    for i in range(len(xyz)):
        hinv = np.linalg.inv(box_vectors[i])
        bv1, bv2, bv3 = box_vectors[i].T

        for j, (a,b) in enumerate(pairs):
            s1 = np.dot(hinv, xyz[i,a,:])
            s2 = np.dot(hinv, xyz[i,b,:])
            s12 = s2 - s1

            s12 = s12 - np.round(s12)
            r12 = np.dot(box_vectors[i], s12)
            dist = np.linalg.norm(r12)
            if not orthogonal:
                for ii in range(-1, 2):
                    v1 = bv1*ii
                    for jj in range(-1, 2):
                        v12 = bv2*jj + v1
                        for kk in range(-1, 2):
                            new_r12 = r12 + v12 + bv3*kk
                            dist = min(dist, np.linalg.norm(new_r12))
            out[i, j] = dist
    return out


def _displacement_mic(xyz, pairs, box_vectors, orthogonal):
    """Displacement vector between pairs of points in each frame under the
    minimum image convention for periodic boundary conditions.

    The computation follows scheme B.9 in Tukerman, M. "Statistical
    Mechanics: Theory and Molecular Simulation", 2010.

    This is a very slow pure python implementation, mostly for testing.
    """
    out = np.empty((xyz.shape[0], pairs.shape[0], 3), dtype=np.float32)
    for i in range(len(xyz)):
        hinv = np.linalg.inv(box_vectors[i])
        bv1, bv2, bv3 = box_vectors[i].T

        for j, (a,b) in enumerate(pairs):
            s1 = np.dot(hinv, xyz[i,a,:])
            s2 = np.dot(hinv, xyz[i,b,:])
            s12 = s2 - s1
            s12 = s12 - np.round(s12)
            disp = np.dot(box_vectors[i], s12)
            min_disp = disp
            dist2 = (disp*disp).sum()
            if not orthogonal:
                for ii in range(-1, 2):
                    v1 = bv1*ii
                    for jj in range(-1, 2):
                        v12 = bv2*jj+v1
                        for kk in range(-1, 2):
                            tmp = disp + v12 + bv3*kk
                            new_dist2 = (tmp*tmp).sum()
                            if new_dist2 < dist2:
                                dist2 = new_dist2
                                min_disp = tmp
            out[i, j] = min_disp

    return out
