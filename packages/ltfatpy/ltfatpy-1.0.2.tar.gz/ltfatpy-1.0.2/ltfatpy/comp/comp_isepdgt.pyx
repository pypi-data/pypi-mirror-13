# -*- coding: utf-8 -*-
# ######### COPYRIGHT #########
#
# Copyright(c) 2015:
# -----------------
#
# * LabEx Archimède: http://labex-archimede.univ-amu.fr/
# * Laboratoire d'Informatique Fondamentale : http://www.lif.univ-mrs.fr/
# * Institut de Mathématiques de Marseille : http://www.i2m.univ-amu.fr/
# * Université d'Aix-Marseille : http://www.univ-amu.fr/
#
# This software is a port from LTFAT 2.1.0 :
# Copyright (C) 2005-2015 Peter L. Soendergaard <peter@sonderport.dk>.
#
# Contributors:
# ------------
#
# * Denis Arrivault <contact.dev_AT_lif.univ-mrs.fr>
# * Florent Jaillet <contact.dev_AT_lif.univ-mrs.fr>
#
# Description:
# -----------
#
# ltfatpy is a partial Python port of the Large Time/Frequency Analysis Toolbox
# (http://ltfat.sourceforge.net/), a MATLAB®/Octave toolbox for working with
# time-frequency analysis and synthesis.
#
# Version:
# -------
#
# * ltfatpy version = 1.0.2
# * LTFAT version = 2.1.0
#
# Licence:
# -------
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ######### COPYRIGHT #########

"""This module contains interface functions for the LTFAT computed
versions of isepdgt calculations.

.. moduleauthor:: Denis Arrivault
"""

from __future__ import print_function, division

import cython
from cython.view cimport array as cvarray
from libc.stdlib cimport malloc, free
import numpy as np

from ltfat cimport ltfatInt, dgt_phasetype, idgt_fb_d, idgt_long_d
from ltfatpy.comp.ltfat cimport TIMEINV, FREQINV

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_idgt_long_d(const double complex[:] coef,
                                        const double complex[:] g,
                                        const int L, const int W,
                                        const int a, const int M,
                                        const dgt_phasetype ptype):
    """ Internal function, do not use it """
    cdef double complex * res_long_d
    cdef ltfatInt size_f = L * W
    res_long_d = < double complex * > malloc(sizeof(double complex) * size_f)

    idgt_long_d(& coef[0], & g[0], L, W, a, M, ptype, res_long_d)
    return < double complex[:size_f] > res_long_d

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_idgt_fb_d(const double complex[:] coef,
                                      const double complex[:] g,
                                      const int L, const int gl,
                                      const int W, const int a,
                                      const int M,
                                      const dgt_phasetype ptype):
    """ Internal function, do not use it """
    cdef double complex * res_fb_d
    cdef ltfatInt size_sig = L * W
    res_fb_d = < double complex * > malloc(sizeof(double complex) *
                                           size_sig)

    idgt_fb_d(& coef[0], & g[0], L, gl, W, a, M, ptype, res_fb_d)
    return < double complex[:size_sig] > res_fb_d

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cpdef comp_isepdgt(coef, g, a, pt):
    """Function that computes separable inverse dgt

    This is a computational subroutine, do not call it directly, use
    :func:`~ltfatpy.gabor.idgt.idgt` instead.
    
    .. seealso:: :func:`~ltfatpy.gabor.idgt.idgt`
    """
    if (coef.dtype.type != np.complex128):
        coef = coef.astype(np.complex128)
    if (g.dtype.type != np.complex128):
        g = g.astype(np.complex128)

    if pt != 0 and pt != 1:
        raise TypeError("pt should be 0 (FREQINV) or 1 (TIMEINV)")
    if coef.ndim <= 1 or coef.ndim > 3:
        raise TypeError("Dimensions of dgt coefficients array must be 2 or 3.")
    cdef ltfatInt N = coef.shape[1]
    cdef ltfatInt L = N * a
    cdef ltfatInt M = coef.shape[0]
    cdef ltfatInt W = coef.size // (M * N)
    if W > 1 and coef.ndim == 2:
        raise TypeError("Dimensions of dgt coefficients array do not fit.")
    if W == 1 and coef.ndim == 3:
        coef = np.squeeze(coef, axis=2)

    coef = coef.reshape(coef.size, order='F')

    cdef ltfatInt gl = g.shape[0]

    if g.ndim > 1:
        if g.ndim > 2:
            g = np.squeeze(g, axis=range(2, g.ndim-1))
        if g.ndim == 2:
            gl = gl * g.shape[1]
        g = g(gl, order='F')

    if gl < L:
        res = np.asarray(comp_idgt_fb_d(coef, g, L, gl, W, a, M, pt))
        if W > 1:
            return np.reshape(res, (L, W), order='F')
        return res

    res = np.asarray(comp_idgt_long_d(coef, g, L, W, a, M, pt))
    if W > 1:
        return np.reshape(res, (L, W), order='F')
    return res
