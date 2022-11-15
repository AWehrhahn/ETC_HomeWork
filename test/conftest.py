# -*- coding: utf-8 -*-
""" 
PyTest configuration initial setup
Includes all types of parameters to iterate over in the actual tests
"""

import pytest
from astropy import units as u

from src.etc import ETC


@pytest.fixture(params=ETC.bands, ids=ETC.bands)
def band(request):
    """ This provides valid bands to test the algorithms """
    return request.param


@pytest.fixture(params=[("A", ValueError)], ids=["band_ValueError"])
def band_error(request):
    """ provide invalid bands and error codes """
    return request.param


@pytest.fixture(params=[20, 0, -10], ids=["mag20", "mag0", "mag-10"])
def mag(request):
    """ Provide valid magnitudes, invalid magnitude values are seperate """
    return request.param


@pytest.fixture(params=[1], ids=["seeing1"])
def seeing(request):
    """ provide valid seeing values """
    return request.param * u.arcsec


@pytest.fixture(params=[0.5], ids=["moon0.5"])
def moon_illumination(request):
    """ provide valid moon illumination fractions """
    return request.param


@pytest.fixture(params=[0.5], ids=["airmass0.5"])
def airmass(request):
    """ provide valid airmass """
    return request.param


@pytest.fixture(params=[10], ids=["dit10"])
def dit(request):
    """ provide valid dit values """
    return request.param * u.s


@pytest.fixture(params=[10], ids=["ndit10"])
def ndit(request):
    """ provide valid ndit values """
    return request.param


@pytest.fixture(params=[7], ids=["snr7"])
def snr(request):
    """ provide valid snr values """
    return request.param
