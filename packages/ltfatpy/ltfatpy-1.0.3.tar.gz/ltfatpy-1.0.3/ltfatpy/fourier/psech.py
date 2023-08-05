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
""" Module of Sampled, periodized hyperbolic secant calculation

Ported from ltfat_2.1.0/fourier/psech.m

.. moduleauthor:: Denis Arrivault
"""

from __future__ import print_function, division

import numpy as np
import six


def psech(L, tfr=None, s=None, **kwargs):
    """Sampled, periodized hyperbolic secant

    - Usage:

        | ``(g, tfr) = psech(L)``
        | ``(g, tfr) = psech(L, tfr)``
        | ``(g, tfr) = psech(L, s=...)``

    - Input parameters:

    :param int L: length of vector.
    :param float tfr: ratio between time and frequency support.
    :param int s: number of samples (equivalent to :math:`tfr=s^2/L`)

    - Output parameters:

    :returns: ``(g, tfr)``
    :rtype: tuple
    :var numpy.ndarray g: periodized hyperbolic cosine
    :var float tfr: calculated ratio between time and frequency support

    ``psech(L,tfr)`` computes samples of a periodized hyperbolic secant.
    The function returns a regular sampling of the periodization
    of the function :math:`sech(\pi\cdot x)`

    The returned function has norm equal to 1.

    The parameter **tfr** determines the ratio between the effective support
    of **g** and the effective support of the DFT of **g**. If **tfr** > 1
    then **g** has a wider support than the DFT of **g**.

    ``psech(L)`` does the same setting than **tfr** = 1.

    ``psech(L,s)`` returns a hyperbolic secant with an effective support of
    **s** samples. This means that approx. 96% of the energy or 74% or the
    area under the graph is contained within **s** samples. This is
    equivalent to ``psech(L,s^2/L)``.

    ``(g,tfr) = psech( ... )`` returns the time-to-frequency support ratio.
    This is useful if you did not specify it (i.e. used the **s** input
    format).

    The function is whole-point even.  This implies that
    ``fft(psech(L,tfr))`` is real for any **L** and **tfr**.

    If this function is used to generate a window for a Gabor frame, then
    the window giving the smallest frame bound ratio is generated by
    ``psech(L,a*M/L)``.

    - Examples:

        This example creates a ``psech`` function, and demonstrates that it
        is its own Discrete Fourier Transform:

        >>> import numpy as np
        >>> import numpy.linalg as nla
        >>> g = psech(128)[0] # DFT invariance: Should be close to zero.
        >>> diff = nla.norm(g-np.fft.fft(g)/np.sqrt(128))
        >>> np.abs(diff) < 10e-10
        True

    .. seealso:: :func:`~ltfatpy.fourier.pgauss.pgauss`, :func:`pbspline`,
        :func:`pherm`

    - References:
        :cite:`jast02-1`
    """
    if not isinstance(L, six.integer_types):
        raise TypeError('L must be an integer')

    if s is not None:
        if not isinstance(s, six.integer_types):
            raise TypeError('s must be an integer')
        tfr = float(s**2 / L)
    elif tfr is None:
        tfr = 1

    safe = 12
    g = np.zeros(L)
    sqrtl = np.sqrt(L)
    w = tfr

    # Outside the interval [-safe,safe] then sech(pi*x) is numerically zero.
    nk = np.ceil(safe / np.sqrt(L / np.sqrt(w)))

    lr = np.arange(L)
    for k in np.arange(-nk, nk+1):
        g = g + (1 / np.cosh(np.pi * (lr / sqrtl - k * sqrtl) / np.sqrt(w)))

    # Normalize it.
    g = g * np.sqrt(np.pi / (2 * np.sqrt(L*w)))
    return(g, tfr)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
