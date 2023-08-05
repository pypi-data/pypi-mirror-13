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
versions of periodized Gaussian calculation.

.. moduleauthor:: Denis Arrivault
"""

from __future__ import print_function, division

import cython
from cython.view cimport array as cvarray
from libc.stdlib cimport malloc, free
import numpy as np

from ltfat cimport ltfatInt, pgauss_d, pgauss_cmplx_d

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double[:] comp_pgauss_real(ltfatInt L, double w, double c_t):
    """ Internal function, do not use it """
    cdef double * c_array = < double * > malloc(sizeof(double) * L)
    pgauss_d(L, w, c_t, c_array)
    return < double[:L] > c_array

# don’t check for out-of-bounds indexing.
@cython.boundscheck(False)
# assume no negative indexing.
@cython.wraparound(False)
cdef double complex[:] comp_pgauss_cplx(ltfatInt L, double w, double c_t,
                                        double c_f):
    """ Internal function, do not use it """
    cdef double complex * c_array = < double complex * > malloc(sizeof(double
                                                                complex) * L)
    pgauss_cmplx_d(L, w, c_t, c_f, c_array)
    return < double complex[:L] > c_array


cpdef comp_pgauss(L, w=1.0, c_t=0, c_f=0):
    """Return the computed sampled, periodized Gaussian.

    This is a computational subroutine, do not call it directly, use
    :func:`~ltfatpy.fourier.pgauss.pgauss` instead.
    """
    if c_f == 0:
        return np.asarray(comp_pgauss_real(L, w, c_t))
    return np.asarray(comp_pgauss_cplx(L, w, c_t, c_f))
