# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound
import os


def getversion():
    try:
        _dist = get_distribution('ltfatpy')
        # Normalize case for Windows systems
        dist_loc = os.path.normcase(_dist.location)
        here = os.path.normcase(__file__)
        if not here.startswith(os.path.join(dist_loc, 'ltfatpy')):
            # not installed, but there is another version that *is*
            raise DistributionNotFound
    except DistributionNotFound:
        return('Please install this project with setup.py')
    else:
        return(_dist.version)

__version__ = getversion()
