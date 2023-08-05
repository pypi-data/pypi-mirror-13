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

from ltfat cimport ltfatInt, dgt_phasetype, dgt_long_cd, dgt_long_d
from ltfat cimport dgt_fb_cd, dgt_fb_d
from ltfatpy.comp.ltfat cimport TIMEINV, FREQINV


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_dgt_long_cd(const double complex[:] f,
                                        const double complex[:] g,
                                        const ltfatInt L, const int W,
                                        const ltfatInt a, const ltfatInt M,
                                        const dgt_phasetype ptype):
    """ Internal function, do not use it """
    cdef ltfatInt size_long_cd = M * W * (L // a)
    cdef double complex * res_long_cd
    res_long_cd = < double complex * > malloc(sizeof(double complex) *
                                              size_long_cd)
    dgt_long_cd(&f[0], &g[0], L, W, a, M, ptype, res_long_cd)
    return < double complex[:size_long_cd] > res_long_cd


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_dgt_long_d(const double[:] f, const double[:] g,
                                       const ltfatInt L, const ltfatInt W,
                                       const ltfatInt a, const ltfatInt M,
                                       const dgt_phasetype ptype):
    """ Internal function, do not use it """
    cdef ltfatInt size_long_d = M * W * (L // a)
    cdef double complex * res_long_d
    res_long_d = < double complex * > malloc(sizeof(double complex) *
                                             size_long_d)
    dgt_long_d(&f[0], &g[0], L, W, a, M, ptype, res_long_d)
    return < double complex[:size_long_d] > res_long_d


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_dgt_fb_d(const double[:] f, const double[:] g,
                                     const ltfatInt L, const ltfatInt gl,
                                     const ltfatInt W, const ltfatInt a,
                                     const ltfatInt M,
                                     const dgt_phasetype ptype):
    """ Internal function, do not use it """
    cdef ltfatInt size_fb_d = M * W * (L // a)
    cdef double complex * res_fb_d
    res_fb_d = < double complex * > malloc(sizeof(double complex) * size_fb_d)
    dgt_fb_d(&f[0], &g[0], L, gl, W, a, M, ptype, res_fb_d)
    return < double complex[:size_fb_d] > res_fb_d


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_dgt_fb_cd(const double complex[:] f,
                                      const double complex[:] g,
                                      const ltfatInt L, const ltfatInt gl,
                                      const ltfatInt W, const ltfatInt a,
                                      const ltfatInt M, const dgt_phasetype
                                      ptype):
    """ Internal function, do not use it """
    cdef ltfatInt size_fb_cd = M * W * (L // a)
    cdef double complex * res_fb_cd
    res_fb_cd = < double complex * > malloc(sizeof(double complex) *
                                            size_fb_cd)
    dgt_fb_cd(&f[0], &g[0], L, gl, W, a, M, ptype, res_fb_cd)
    return < double complex[:size_fb_cd] > res_fb_cd


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cpdef comp_sepdgt(f, g, a, M, pt):
    """Function that computes separable dgt

    This is a computational subroutine, do not call it directly, use
    :func:`~ltfatpy.gabor.dgt.dgt` instead.
    """
    cdef ltfatInt L, W
    if (f.dtype.type != np.float64) and (f.dtype.type != np.complex128):
        raise TypeError("f data should be numpy.float64 or complex128")
    if (g.dtype.type != np.float64) and (g.dtype.type != np.complex128):
        raise TypeError("g data should be numpy.float64 or complex128")
    if (f.dtype.type != g.dtype.type):
        if f.dtype.type == np.float64:
            f = f.astype(np.complex128)
        if g.dtype.type == np.float64:
            g = g.astype(np.complex128)
    if pt != FREQINV and pt != TIMEINV:
        raise TypeError("pt should be 0 (FREQINV) or 1 (TIMEINV)")

    if f.ndim > 1:
        if f.ndim > 2:
            f = np.squeeze(f, axis=range(2, f.ndim-1))
        L = f.shape[0]
        W = f.shape[1]
        f_combined = f.reshape(L * W, order='F')
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

    cdef ltfatInt N = L//a

    if gl < L:
        if f.dtype.type == np.float64:
            res = np.asarray(comp_dgt_fb_d(f_combined, g_combined, L, gl, W, a,
                                           M, pt))
        else:
            res = np.asarray(comp_dgt_fb_cd(f_combined, g_combined, L, gl, W,
                                            a, M, pt))
    else:
        if f.dtype.type == np.float64:
            res = np.asarray(comp_dgt_long_d(f_combined, g_combined, L, W, a,
                                             M, pt))
        else:
            res = np.asarray(comp_dgt_long_cd(f_combined, g_combined, L, W, a,
                                              M, pt))
    if W > 1:
        res = np.reshape(res, (M, N, W), order='F')
    else:
        res = np.reshape(res, (M, N), order='F')
    return res
