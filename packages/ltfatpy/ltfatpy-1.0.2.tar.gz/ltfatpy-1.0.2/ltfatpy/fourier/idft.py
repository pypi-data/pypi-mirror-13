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
"""Module of inverse normalized discrete Fourier transform

Ported from ltfat_2.1.0/fourier/idft.m

.. moduleauthor:: Florent Jaillet
"""

from __future__ import print_function, division

import numpy as np

from ltfatpy.comp.assert_sigreshape_pre import assert_sigreshape_pre
from ltfatpy.comp.assert_sigreshape_post import assert_sigreshape_post


def idft(c, N=None, dim=0):
    """Inverse Normalized Discrete Fourier Transform

    - Usage:

        | ``f = idft(c)``
        | ``f = idft(c, N, dim)``

    - Input parameters:

    :param numpy.ndarray c: Normalized discrete Fourier coefficients of a
        signal
    :param int N: IDFT length
    :param int dim: Axis over which to compute the IDFT. By default the first
        axis is used.

    - Output parameters:

    :returns: Reconstructed signal
    :rtype: numpy.ndarray

    :func:`~ltfatpy.fourier.idft.idft` computes a normalized or unitary inverse
    discrete Fourier transform.
    The unitary inverse discrete Fourier transform is computed by

    ..                       L-1
        f(l+1) = 1/sqrt(L) * sum c(k+1)*exp(2*pi*i*k*l/L)
                             k=0

    .. math::

        f\\left(l+1\\right)=\\frac{1}{\\sqrt{L}}
        \\sum_{k=0}^{L-1}c\\left(k+1\\right)e^{2\\pi ikl/L}


    for :math:`l=0,\ldots,L-1`.

    The output of :func:`~ltfatpy.fourier.idft.idft` is a scaled version of the
    output from :func:`numpy.fft.ifft`. The function takes the same first three
    arguments as :func:`numpy.fft.ifft`. See the help on :func:`numpy.fft.ifft`
    for a thorough description.

    .. seealso:: :func:`~ltfatpy.fourier.dft.dft`

    """

    c, N, Ls, W, dim, permutedsize, order = assert_sigreshape_pre(c, N, dim)

    # Force ifft along dimension 0, since we have permuted the dimensions
    # manually
    f = np.fft.ifft(c, N, 0) * np.sqrt(N)

    f = assert_sigreshape_post(f, dim, permutedsize, order)

    return f
