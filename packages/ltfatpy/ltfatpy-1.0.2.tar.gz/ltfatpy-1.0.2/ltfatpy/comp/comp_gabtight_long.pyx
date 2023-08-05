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
versions of tight gabor windows calculation.

.. moduleauthor:: Denis Arrivault
"""

from __future__ import print_function, division

import cython
from cython.view cimport array as cvarray
from libc.stdlib cimport malloc, free
import numpy as np

from ltfat cimport ltfatInt, gabtight_long_d, gabtight_long_cd

# cython: profile=True

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double[:] comp_gabtight_long_real(const double[:] g,
                                       const ltfatInt L, const ltfatInt R,
                                       const ltfatInt a, const ltfatInt M):
    """ Internal function, do not use it """
    cdef int gd_size = L * R
    cdef double * gd = < double * > malloc(sizeof(double) * gd_size)
    gabtight_long_d(&g[0], L, R, a, M, gd);
    return < double[:gd_size] > gd

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_gabtight_long_cmplx(const double complex[:] g,
                                                const ltfatInt L,
                                                const ltfatInt R,
                                                const ltfatInt a,
                                                const ltfatInt M):
    """ Internal function, do not use it """
    cdef int gd_size = L * R
    cdef double complex * gd
    gd = < double complex * > malloc(sizeof(double complex) * gd_size)
    gabtight_long_cd(&g[0], L, R, a, M, gd);
    return < double complex [:gd_size] > gd

cpdef comp_gabtight_long(g, a, M):
    """Compute tight window

    This is a computational subroutine, do not call it directly, use
    :func:`~ltfatpy.gabor.gabtight.gabtight` instead.

    .. seealso:: :func:`~ltfatpy.gabor.gabtight.gabtight`
    """
    cdef ltfatInt L = g.shape[0]
    cdef ltfatInt R = 1
    if g.ndim > 1:
        if g.ndim > 2:
            raise TypeError("g dimensions should be 1 or 2.")
        R = g.shape[1]
        g_combined = g.reshape(L*R, order='F')
    else:
        g_combined = g

    if np.issubdtype(g.dtype, np.float64):
        gd = np.asarray(comp_gabtight_long_real(g_combined, L, R, a, M))
    elif np.issubdtype(g.dtype, np.complex128):
        gd = np.asarray(comp_gabtight_long_cmplx(g_combined, L, R, a, M))
    else:
        raise TypeError("g data should be numpy.float64 or numpy.complex128")

    if R == 1:
        return gd
    else:
        return gd.reshape(R, L).transpose()
