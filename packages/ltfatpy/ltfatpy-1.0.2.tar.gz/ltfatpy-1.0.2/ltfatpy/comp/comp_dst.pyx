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
versions of dst calculations.

.. moduleauthor:: Denis Arrivault
"""

from __future__ import print_function, division

import cython
from cython.view cimport array as cvarray
from libc.stdlib cimport malloc, free
import numpy as np

from ltfat cimport ltfatInt, dst_kind, dst_cd, dst_d
from ltfatpy.comp.ltfat cimport DSTI, DSTII, DSTIII, DSTIV


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_dst_cd(const double complex[:] f, const ltfatInt L,
                                   const ltfatInt W, const dst_kind kind):
    """ Internal function, do not use it """
    cdef ltfatInt size_cd = L * W
    cdef double complex * res_long_cd
    res_cd = < double complex * > malloc(sizeof(double complex) * size_cd)
    dst_cd(&f[0], L, W, res_cd, kind)
    return < double complex[:size_cd] > res_cd


# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double[:] comp_dst_d(const double[:] f, const ltfatInt L,
                          const ltfatInt W, const dst_kind kind):
    """ Internal function, do not use it """
    cdef ltfatInt size_d = L * W
    cdef double * res_d
    res_d = < double * > malloc(sizeof(double) * size_d)
    dst_d(&f[0], L, W, res_d, kind)
    return < double[:size_d] > res_d

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cpdef comp_dst(f, type):
    """Function that computes dst

    This is a computational subroutine, do not call it directly, use
    :func:`~ltfatpy.fourier.dst.dsti`, :func:`~ltfatpy.fourier.dst.dstii`,
    :func:`~ltfatpy.fourier.dst.dstiii` or func:`~ltfatpy.fourier.dst.dstiv`
    instead.
    """
    cdef ltfatInt L, W
    if (f.dtype.type != np.float64) and (f.dtype.type != np.complex128):
        raise TypeError("f data should be numpy.float64 or complex128")
    if type not in {1, 2, 3, 4}:
        raise TypeError("type should be 1, 2, 3 or 4")

    dst_type = {1: DSTI, 2: DSTII, 3: DSTIII, 4: DSTIV}

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

    if f.dtype.type == np.float64:
        res = np.asarray(comp_dst_d(f_combined, L, W, dst_type[type]))
    else:
        res = np.asarray(comp_dst_cd(f_combined, L, W, dst_type[type]))
    if W > 1:
        res = np.reshape(res, (L, W), order='F')
    return res
