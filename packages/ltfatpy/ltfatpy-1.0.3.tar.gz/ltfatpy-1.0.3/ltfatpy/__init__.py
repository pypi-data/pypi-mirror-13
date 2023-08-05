# -*- coding: utf-8 -*-
"""The **ltfatpy** package is a partial Python port of the
`Large Time/Frequency Analysis Toolbox (LTFAT)
<http://ltfat.sourceforge.net/>`_, a MATLAB®/Octave toolbox for working with
time-frequency analysis and synthesis.

It is intended both as an educational and a computational tool.

The package provides a large number of linear transforms including Gabor
transforms along with routines for constructing windows (filter prototypes)
and routines for manipulating coefficients.

The orginal LTFAT Toolbox for MATLAB®/Octave is developed at
`CAHR <http://www.dtu.dk/centre/cahr/English.aspx>`_, Technical
University of Denmark, `ARI <http://www.kfs.oeaw.ac.at>`_, Austrian Academy
of Sciences and `I2M <http://www.i2m.univ-amu.fr>`_, Aix-Marseille Université.

The Python port is developed at
`LabEx Archimède <http://labex-archimede.univ-amu.fr/>`_, as a
`LIF <http://www.lif.univ-mrs.fr/>`_ and `I2M <https://www.i2m.univ-amu.fr/>`_
project, Aix-Marseille Université.

This package, as well as the original LTFAT toolbox, is Free software, released
under the GNU General Public License (GPLv3).
"""

from ltfatpy.comp.arg_firwin import arg_firwin
from ltfatpy.comp.assert_groworder import assert_groworder
from ltfatpy.comp.assert_sigreshape_post import assert_sigreshape_post
from ltfatpy.comp.assert_sigreshape_pre import assert_sigreshape_pre
from ltfatpy.comp.comp_dct import comp_dct
from ltfatpy.comp.comp_dst import comp_dst
from ltfatpy.comp.comp_gabdual_long import comp_gabdual_long
from ltfatpy.comp.comp_gabtight_long import comp_gabtight_long
from ltfatpy.comp.comp_hermite import comp_hermite
from ltfatpy.comp.comp_hermite_all import comp_hermite_all
from ltfatpy.comp.comp_isepdgt import comp_isepdgt
from ltfatpy.comp.comp_isepdgtreal import comp_isepdgtreal
from ltfatpy.comp.comp_pgauss import comp_pgauss
from ltfatpy.comp.comp_sepdgt import comp_sepdgt
from ltfatpy.comp.comp_sepdgtreal import comp_sepdgtreal
from ltfatpy.comp.comp_sigreshape_post import comp_sigreshape_post
from ltfatpy.comp.comp_sigreshape_pre import comp_sigreshape_pre
from ltfatpy.comp.comp_window import comp_window
from ltfatpy.comp.gabpars_from_windowsignal import gabpars_from_windowsignal
from ltfatpy.fourier.dcti import dcti
from ltfatpy.fourier.dctii import dctii
from ltfatpy.fourier.dctiii import dctiii
from ltfatpy.fourier.dctiv import dctiv
from ltfatpy.fourier.dft import dft
from ltfatpy.fourier.dsti import dsti
from ltfatpy.fourier.dstii import dstii
from ltfatpy.fourier.dstiii import dstiii
from ltfatpy.fourier.dstiv import dstiv
from ltfatpy.fourier.fftindex import fftindex
from ltfatpy.fourier.fftreal import fftreal
from ltfatpy.fourier.fftresample import fftresample
from ltfatpy.fourier.idft import idft
from ltfatpy.fourier.ifftreal import ifftreal
from ltfatpy.fourier.isevenfunction import isevenfunction
from ltfatpy.fourier.middlepad import middlepad
from ltfatpy.fourier.pderiv import pderiv
from ltfatpy.fourier.pgauss import pgauss
from ltfatpy.fourier.pherm import pherm
from ltfatpy.fourier.psech import psech
from ltfatpy.gabor.dgt import dgt
from ltfatpy.gabor.dgtlength import dgtlength
from ltfatpy.gabor.dgtreal import dgtreal
from ltfatpy.gabor.gabdual import gabdual
from ltfatpy.gabor.gabframediag import gabframediag
from ltfatpy.gabor.gabimagepars import gabimagepars
from ltfatpy.gabor.gabphasegrad import gabphasegrad
from ltfatpy.gabor.gabtight import gabtight
from ltfatpy.gabor.gabwin import gabwin
from ltfatpy.gabor.idgt import idgt
from ltfatpy.gabor.idgtreal import idgtreal
from ltfatpy.gabor.instfreqplot import instfreqplot
from ltfatpy.gabor.phaselock import phaselock
from ltfatpy.gabor.phaseplot import phaseplot
from ltfatpy.gabor.phaseunlock import phaseunlock
from ltfatpy.gabor.plotdgt import plotdgt
from ltfatpy.gabor.plotdgtreal import plotdgtreal
from ltfatpy.gabor.s0norm import s0norm
from ltfatpy.gabor.sgram import sgram
from ltfatpy.gabor.tfplot import tfplot
from ltfatpy.signals.greasy import greasy
from ltfatpy.signals.gspi import gspi
from ltfatpy.signals.linus import linus
from ltfatpy.sigproc.fir2long import fir2long
from ltfatpy.sigproc.firkaiser import firkaiser
from ltfatpy.sigproc.firwin import firwin
from ltfatpy.sigproc.groupthresh import groupthresh
from ltfatpy.sigproc.largestn import largestn
from ltfatpy.sigproc.largestr import largestr
from ltfatpy.sigproc.long2fir import long2fir
from ltfatpy.sigproc.normalize import normalize
from ltfatpy.sigproc.rms import rms
from ltfatpy.sigproc.thresh import thresh
from ltfatpy.tools.lcm import lcm
from ltfatpy.tools.postpad import postpad

__all__ = ["arg_firwin", "assert_groworder", "assert_sigreshape_post",
           "assert_sigreshape_pre", "comp_dct", "comp_dst",
           "comp_gabdual_long", "comp_gabtight_long", "comp_hermite",
           "comp_hermite_all", "comp_isepdgt", "comp_isepdgtreal",
           "comp_pgauss", "comp_sepdgt", "comp_sepdgtreal",
           "comp_sigreshape_post", "comp_sigreshape_pre", "comp_window",
           "gabpars_from_windowsignal", "dcti", "dctii", "dctiii", "dctiv",
           "dft", "dsti", "dstii", "dstiii", "dstiv", "fftindex", "fftreal",
           "fftresample", "idft", "ifftreal", "isevenfunction", "middlepad",
           "pderiv", "pgauss", "pherm", "psech", "dgt", "dgtlength", "dgtreal",
           "gabdual", "gabframediag", "gabimagepars", "gabphasegrad",
           "gabtight", "gabwin", "idgt", "idgtreal", "instfreqplot",
           "phaselock", "phaseplot", "phaseunlock", "plotdgt", "plotdgtreal",
           "s0norm", "sgram", "tfplot", "greasy", "gspi", "linus", "fir2long",
           "firkaiser", "firwin", "groupthresh", "largestn", "largestr",
           "long2fir", "normalize", "rms", "thresh", "lcm", "postpad"]


__version__ = "1.0.3"
