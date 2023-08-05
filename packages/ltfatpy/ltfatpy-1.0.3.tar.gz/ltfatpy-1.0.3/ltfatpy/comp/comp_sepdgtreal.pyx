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
# * ltfatpy version = 1.0.3
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
versions of sepdgt calculations.

.. moduleauthor:: Denis Arrivault
"""

from __future__ import print_function, division

import cython
from cython.view cimport array as cvarray
from libc.stdlib cimport malloc, free
import numpy as np

from ltfat cimport ltfatInt, dgt_phasetype, dgtreal_fb_d, dgtreal_long_d
from ltfatpy.comp.ltfat cimport TIMEINV, FREQINV
from numpy import int64


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_dgtreal_long_d(const double[:] f,
                                           const double[:] g, const int L,
                                           const int W, const int a,
                                           const int M, const int M2,
                                           const dgt_phasetype ptype):
    """ Internal function, do not use it """
    cdef int size = M2 * W * (L // a)
    cdef double complex * cout
    cout = < double complex * > malloc(sizeof(double complex) * size)
    dgtreal_long_d(&f[0], &g[0], L, W, a, M, ptype, cout)
    return < double complex[:size] > cout


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_dgtreal_fb_d(const double[:] f,
                                         const double[:] g, const int L,
                                         const int gl, const int W,
                                         const int a, const int M,
                                         const int M2,
                                         const dgt_phasetype ptype):
    """ Internal function, do not use it """
    cdef int size_fb_d = M2 * W * (L // a)
    cdef double complex * res_fb_d
    res_fb_d = < double complex * > malloc(sizeof(double complex) * size_fb_d)
    dgtreal_fb_d(&f[0], &g[0], L, gl, W, a, M, ptype, res_fb_d)
    return < double complex[:size_fb_d] > res_fb_d


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cpdef comp_sepdgtreal(f, g, a, M, pt):
    """Function that computes separable dgt real

    This is a computational subroutine, do not call it directly, use
    :func:`~ltfatpy.gabor.dgtreal.dgtreal` instead.
    """
    cdef int L, W
    if f.dtype.type != np.float64:
        raise TypeError("f data should be numpy.float64")
    if g.dtype.type != np.float64:
        raise TypeError("g data should be numpy.float64")
    if pt != FREQINV and pt != TIMEINV:
        raise TypeError("pt should be 0 (FREQINV) or 1 (TIMEINV)")

    if f.ndim > 1:
        if f.ndim > 2:
            f = np.squeeze(f, axis=range(2, f.ndim-1))
        L = f.shape[0]
        W = f.shape[1]
        f_combined = f.reshape(L*W, order='F')
    else:
        L = f.shape[0]
        W = 1
        f_combined = f

    cdef ltfatInt gl = g.shape[0]
    if g.ndim > 1:
        if g.ndim > 2:
            g = np.squeeze(g, axis=range(2, g.ndim-1))
        if f.ndim == 2:
            gl = gl * g.shape[1]
        g_combined = g.reshape(gl, order='F')
    else:
        g_combined = g
    cdef int N = L//a
    cdef int M2 = M // 2 + 1
    if gl < L:
        res = np.asarray(comp_dgtreal_fb_d(f_combined, g_combined, L, gl, W,
                                           a, M, M2, pt))
    else:
        res = np.asarray(comp_dgtreal_long_d(f_combined, g_combined, L, W, a,
                                             M, M2, pt))
    if W > 1:
        res = np.reshape(res, (M2, N, W), order='F')
    else:
        res = np.reshape(res, (M2, N), order='F')

    return res
