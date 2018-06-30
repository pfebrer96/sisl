"""PHonon related functions and classes
=======================================

.. module:: sisl.physics.phonon
   :noindex:

In sisl phonon calculations are relying on routines
specific for phonons. For instance density of states calculations from
phonon eigenvalues and other quantities.

This module implements the necessary tools required for calculating
DOS, PDOS, group-velocities and real-space displacements.

.. autosummary::
   :toctree:

   DOS
   PDOS
   velocity
   displacement


Supporting classes
------------------

Certain classes aid in the usage of the above methods by implementing them
using automatic arguments.

.. autosummary::
   :toctree:

   CoefficientPhonon
   ModePhonon
   ModeCPhonon
   EigenfrequencyPhonon
   EigenvectorPhonon
   EigenmodePhonon

"""
from __future__ import print_function, division

import numpy as np
from numpy import conj

import sisl._array as _a
from sisl.unit import unit_convert
from sisl.linalg import eig_destroy, eigh_destroy
from sisl.messages import info, warn, SislError, tqdm_eta
from sisl._help import dtype_complex_to_real
from .distribution import get_distribution
from .sparse import SparseOrbitalBZ
from .state import Coefficient, State, StateC

from .electron import DOS as electron_DOS
from .electron import PDOS as electron_PDOS


__all__ = ['DOS', 'PDOS', 'velocity', 'displacement']
__all__ += ['CoefficientPhonon', 'ModePhonon', 'ModeCPhonon']
__all__ += ['EigenvaluePhonon', 'EigenvectorPhonon', 'EigenmodePhonon']


def DOS(E, hw, distribution='gaussian'):
    r""" Calculate the density of modes (DOS) for a set of energies, `E`, with a distribution function

    The :math:`\mathrm{DOS}(E)` is calculated as:

    .. math::
       \mathrm{DOS}(E) = \sum_i D(E-\hbar\omega_i) \approx\delta(E-\hbar\omega_i)

    where :math:`D(\Delta E)` is the distribution function used. Note that the distribution function
    used may be a user-defined function. Alternatively a distribution function may
    be retrieved from `~sisl.physics.distribution`.

    Parameters
    ----------
    E : array_like
       energies to calculate the DOS at
    hw : array_like
       phonon eigenvalues
    distribution : func or str, optional
       a function that accepts :math:`E` as argument and calculates the
       distribution function.

    See Also
    --------
    sisl.physics.distribution : a selected set of implemented distribution functions
    PDOS : projected DOS (same as this, but projected onto each direction)

    Returns
    -------
    numpy.ndarray : DOS calculated at energies, has same length as `E`
    """
    return electron_DOS(E, hw, distribution)


def PDOS(E, mode, hw, distribution='gaussian'):
    r""" Calculate the projected density of modes (PDOS) onto each each atom and direction for a set of energies, `E`, with a distribution function

    The :math:`\mathrm{PDOS}(E)` is calculated as:

    .. math::
       \mathrm{PDOS}_\alpha(E) = \sum_i \epsilon^*_{i,\alpha} \epsilon_{i,\alpha} D(E-\hbar\omega_i)

    where :math:`D(\Delta E)` is the distribution function used. Note that the distribution function
    used may be a user-defined function. Alternatively a distribution function may
    be aquired from `~sisl.physics.distribution`.

    .. math::
       \mathrm{DOS}(E) = \sum_\alpha\mathrm{PDOS}_\alpha(E)

    Parameters
    ----------
    E : array_like
       energies to calculate the projected-DOS from
    mode : array_like
       eigenvectors
    hw : array_like
       eigenvalues
    distribution : func or str, optional
       a function that accepts :math:`E-\epsilon` as argument and calculates the
       distribution function.

    See Also
    --------
    sisl.physics.distribution : a selected set of implemented distribution functions
    DOS : total DOS (same as summing over atoms and directions)

    Returns
    -------
    numpy.ndarray
        projected DOS calculated at energies, has dimension ``(mode.shape[1], len(E))``.
    """
    return electron_PDOS(E, hw, mode, distribution=distribution)


def velocity(mode, hw, dDk, degenerate=None):
    r""" Calculate the velocity of a set of modes

    These are calculated using the analytic expression (:math:`\alpha` corresponding to the Cartesian directions):

    .. math::

       \mathbf{v}_{i\alpha} = \frac1{2\hbar\omega} \langle \epsilon_i |
                \frac{\partial}{\partial\mathbf k}_\alpha \mathbf D(\mathbf k) | \epsilon_i \rangle

    Parameters
    ----------
    mode : array_like
       vectors describing the phonon modes, 2nd dimension contains the modes. In case of degenerate
       modes the vectors *may* be rotated upon return.
    hw : array_like
       frequencies of the modes, for any negative frequency the velocity will be set to 0.
    dDk : list of array_like
       Dynamical matrix derivative with respect to :math:`\mathbf k`. This needs to be a tuple or
       list of the dynamical matrix derivative along the 3 Cartesian directions.
    degenerate: list of array_like, optional
       a list containing the indices of degenerate modes. In that case a prior diagonalization
       is required to decouple them. This is done 3 times along each of the Cartesian directions.

    Returns
    -------
    numpy.ndarray
        velocities per mode with final dimension ``(mode.shape[0], 3)``, the velocity unit is Ang/ps
        Units *may* change in future releases.
    """
    if mode.ndim == 1:
        return velocity(mode.reshape(1, -1), hw, dDk, degenerate).ravel()

    return _velocity(mode, hw, dDk, degenerate)


# We return velocity units in Ang/ps
#   hbar in eV.s = 6.582119514e-16
# and dDk is already in Ang * eV ** 2.
#   1e-12 ps / s
_velocity_const = 1 / 6.582119514e-16 * 1e-12


def _velocity(mode, hw, dDk, degenerate):
    r""" For modes in an orthogonal basis """

    # Along all directions
    v = np.empty([mode.shape[0], 3], dtype=dtype_complex_to_real(mode.dtype))

    # Decouple the degenerate modes
    if not degenerate is None:
        for deg in degenerate:
            # Now diagonalize to find the contributions from individual modes
            # then re-construct the seperated degenerate modes
            # Since we do this for all directions we should decouple them all
            vv = conj(mode[deg, :]).dot(dDk[0].dot(mode[deg, :].T))
            S = eigh_destroy(vv)[1].T.dot(mode[deg, :])
            vv = conj(S).dot((dDk[1]).dot(S.T))
            S = eigh_destroy(vv)[1].T.dot(S)
            vv = conj(S).dot((dDk[2]).dot(S.T))
            mode[deg, :] = eigh_destroy(vv)[1].T.dot(S)

    v[:, 0] = (conj(mode.T) * dDk[0].dot(mode.T)).sum(0).real
    v[:, 1] = (conj(mode.T) * dDk[1].dot(mode.T)).sum(0).real
    v[:, 2] = (conj(mode.T) * dDk[2].dot(mode.T)).sum(0).real

    # Set everything to zero for the negative frequencies
    v[hw < 0, :] = 0

    return v * _velocity_const / (2 * hw.reshape(-1, 1))


def displacement(mode, hw, mass):
    r""" Calculate the real-space displacements for a given mode (in units of the characteristic length)

    The displacements per mode may be written as:

    .. math::

       \mathbf{u}_{i\alpha} = \frac{\epsilon_{i\alpha}}{m_i \hbar\omega}

    where :math:`i` is the atomic index.

    Parameters
    ----------
    mode : array_like
       vectors describing the phonon modes, 2nd dimension contains the modes. In case of degenerate
       modes the vectors *may* be rotated upon return.
    hw : array_like
       frequencies of the modes, for any negative frequency the returned displacement will be 0.
    mass : array_like
       masses for the atoms (has to have length ``mode.shape[1] // 3``

    Returns
    -------
    numpy.ndarray
        displacements per mode with final dimension ``(mode.shape[0], 3)``, the displacements are in Ang
    """
    if mode.ndim == 1:
        return displacement(mode.reshape(1, -1), hw, mass).reshape(-1, 3)

    return _displacement(mode, hw, mass)


# Electron rest mass in units of proton mass (the units we use for the atoms)
_me_in_mp = 5.485799090e-4
_displacement_const = (2 * unit_convert('Ry', 'eV') * _me_in_mp) ** 0.5 * unit_convert('Bohr', 'Ang')


def _displacement(mode, hw, mass):
    """ Real space displacements """
    idx = (hw < 0).nonzero()[0]
    U = mode.copy()
    U[idx, :] = 0.

    # Now create the remaining displacements
    idx = np.delete(_a.arangei(mode.shape[0]), idx)

    # Generate displacement factor
    factor = _displacement_const / hw[idx].reshape(-1, 1) ** 0.5

    U.shape = (mode.shape[0], -1, 3)
    U[idx, :, :] = (mode[idx, :] * factor).reshape(-1, mass.shape[0], 3) / mass.reshape(1, -1, 1) ** 0.5

    return U


class _phonon_Mode(object):
    __slots__ = []

    @property
    def mode(self):
        return self.state


class CoefficientPhonon(Coefficient):
    """ Coefficients describing some physical quantity related to phonons """
    __slots__ = []


class ModePhonon(_phonon_Mode, State):
    """ A mode describing a physical quantity related to phonons """
    __slots__ = []


class ModeCPhonon(_phonon_Mode, StateC):
    """ A mode describing a physical quantity related to phonons, with associated coefficients of the mode """
    __slots__ = []


class EigenvaluePhonon(CoefficientPhonon):
    """ Eigenvalues of phononic states, no eigenmodes retained

    This holds routines that enable the calculation of density of states.
    """
    __slots__ = []

    @property
    def hw(self):
        return self.c

    def DOS(self, E, distribution='gaussian'):
        r""" Calculate DOS for provided energies, `E`.

        This routine calls `sisl.physics.phonon.DOS` with appropriate arguments
        and returns the DOS.

        See `~sisl.physics.phonon.DOS` for argument details.
        """
        return DOS(E, self.hw, distribution)


class EigenvectorPhonon(ModePhonon):
    """ Eigenvectors of phonon modes, no eigenvalues retained """
    __slots__ = []


class EigenmodePhonon(ModeCPhonon):
    """ Eigenmodes of phonons with eigenvectors and eigenvalues.

    This holds routines that enable the calculation of (projected) density of states.
    """
    __slots__ = []

    @property
    def hw(self):
        return self.c

    def DOS(self, E, distribution='gaussian'):
        r""" Calculate DOS for provided energies, `E`.

        This routine calls `sisl.physics.phonon.DOS` with appropriate arguments
        and returns the DOS.

        See `~sisl.physics.phonon.DOS` for argument details.
        """
        return DOS(E, self.hw, distribution)

    def PDOS(self, E, distribution='gaussian'):
        r""" Calculate PDOS for provided energies, `E`.

        This routine calls `~sisl.physics.phonon.PDOS` with appropriate arguments
        and returns the PDOS.

        See `~sisl.physics.phonon.PDOS` for argument details.
        """
        return PDOS(E, self.mode, self.hw, distribution)

    def velocity(self, eps=1e-7):
        r""" Calculate velocity for the modes

        This routine calls `~sisl.physics.phonon.velocity` with appropriate arguments
        and returns the velocity for the modes.

        Note that the coefficients associated with the `ModeCPhonon` *must* correspond
        to the energies of the modes.

        See `~sisl.physics.phonon.velocity` for details.

        Notes
        -----
        The eigenvectors for the modes *may* have changed after calling this routine.
        This is because of the velocity un-folding for degenerate modes. I.e. calling
        `displacement` and/or `PDOS` after this method *may* change the result.

        Parameters
        ----------
        eps : float, optional
           precision used to find degenerate modes.
        """
        opt = {'k': self.info.get('k', (0, 0, 0))}
        gauge = self.info.get('gauge', None)
        if not gauge is None:
            opt['gauge'] = gauge

        deg = self.degenerate(eps)
        return velocity(self.mode, self.hw, self.parent.dDk(**opt), degenerate=deg)

    def displacement(self):
        r""" Calculate displacements for the modes

        This routine calls `~sisl.physics.phonon.displacements` with appropriate arguments
        and returns the real space displacements for the modes.

        Note that the coefficients associated with the `ModeCPhonon` *must* correspond
        to the frequencies of the modes.

        See `~sisl.physics.phonon.displacement` for details.
        """
        return displacement(self.mode, self.hw, self.parent.mass)