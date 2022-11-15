# -*- coding: utf-8 -*-
"""
Test the main ETC functionality
"""

from astropy import units as u

from src.etc import ETC

# TODO: Test more invalid input parameters


def test_photons(band, mag):
    """
    Test that the photons in filter function can handle standard inputs

    Parameters
    ----------
    band : _type_
        _description_
    mag : _type_
        _description_
    """
    etc = ETC()
    photons = etc.photons_in_filter(band, mag)
    assert isinstance(photons, u.Quantity)
    assert photons.unit.is_equivalent(u.ph / u.pix / u.s)
    assert photons > 0 * u.ph / u.pix / u.s


def test_photons_band_error(band_error, mag):
    """ Test for the correct error message when using invalid band parameters """
    band, error = band_error
    etc = ETC()
    try:
        photons = etc.photons_in_filter(band, mag)
        assert False
    except error as e:
        assert isinstance(e, error)


def test_observing_conditions(seeing, moon_illumination, airmass):
    """ test the setting of observing conditions """
    etc = ETC()
    etc.initialize_observing_conditions(
        seeing=seeing, moon_illumination=moon_illumination, airmass=airmass,
    )


def test_snr(band, mag, dit, ndit, seeing, moon_illumination, airmass):
    """ test the signal to noise calculation """
    etc = ETC()
    etc.initialize_observing_conditions(
        seeing=seeing, moon_illumination=moon_illumination, airmass=airmass,
    )
    snr = etc.get_snr(band, mag, dit, ndit)

    assert isinstance(snr, float)
    assert snr > 0


def test_ndit(band, mag, dit, snr, seeing, moon_illumination, airmass):
    """ test the ndit estimation """
    etc = ETC()
    etc.initialize_observing_conditions(
        seeing=seeing, moon_illumination=moon_illumination, airmass=airmass,
    )
    ndit = etc.get_ndit(band, snr, mag, dit)

    assert isinstance(ndit, int)
    assert ndit > 0
