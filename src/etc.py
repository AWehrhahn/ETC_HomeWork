from astropy import units as u
import hmbp
import numpy as np
from functools import lru_cache
from typing import List, Union

MagUnit = Union[float, u.Quantity]

class ETC:
    """
    Simple exposure time calculator class for the HAWK-I instrument 
    at the Paranal observatory
    """

    #:str: Name of this instrument
    instrument: str = "HAWKI"
    #:str: Name of the observatory
    observatory: str = "Paranal"
    # The NB0984 band is not available in hmbp for some reason?
    #:list[str]: available wavelength bands
    bands: List[str] = [
        "Ks",
        "Y",
        "J",
        "H",
        "CH4",
        "H2",
        "NB1060",
        "NB1190",
        "NB2090",
        "BrGamma",
    ]
    #:Quantity: Readout Noise in e-/pixel/DIT
    readout_noise: u.Quantity = 5 * (u.electron / u.pixel)
    #:Quantity: Dark Noise in e-/pixel/s
    dark_noise: u.Quantity = 0.01 * (u.electron / u.pixel / u.s)

    # The on-sky field of view is 7.5'x7.5', with a cross-shaped gap of 15"
    # between the four HAWAII 2RG 2048x2048 pixels detectors.
    # The pixel scale is of 0.106".
    pixel_scale = 0.1063 ** 2 * (1 / u.pixel)

    #:Quantity: area of the telescope mirror
    telescope_size = np.pi * (8 / 2 * u.m) ** 2

    # assumption: this is constant along all bands
    #:Quantity: efficieny of the detector in converting photons to electron
    quantum_efficiency = 0.8 * (u.electron / u.ph)

    #:Quantity: Detector linearity/flat-fielding limit
    linearity_limit = 100_000 * u.electron / u.pixel

    # Detector saturation limit
    saturation_limit = 120_000 * u.electron / u.pixel

    #:Quantity: seeing conditions in arcsec
    seeing: u.Quantity = 1 * u.arcsec

    #:float: airmass for the observation
    airmass: float = 1

    #:float: fraction of lunar illumination
    moon_illumination = 0.5

    def __init__(self):
        # No filter list available on SVO?
        # bands = tcu.download_svo_filter_list(self.observatory, self.instrument)
        pass

    @lru_cache()
    def photons_in_filter(self, band: str, mag: MagUnit) -> u.Quantity:
        """
        Determine the number of photons in this filter for an object of this magnitude
        adjusted for the size of the telescope and the pixels

        Parameters
        ----------
        filter : str
            Wavelength Filter
        mag : float | u.Quantity
            Magnitude of the target, if float assumes Vega Magnitudes

        Returns
        -------
        u.Quantity
            number of photons in this filter in units of ph/pixel/s

        Raises
        ------
        ValueError
            incorrect filter name
        """
        if band not in self.bands:
            raise ValueError(
                f"Unexpected filter name, received {band} but expected one of {self.bands}"
            )

        photons = hmbp.for_flux_in_filter(
            band, mag, instrument=self.instrument, observatory=self.observatory
        )
        photons *= self.telescope_size
        photons *= self.pixel_scale
        return photons

    @u.quantity_input(seeing=u.arcsec)
    def initialize_observing_conditions(
        self,
        seeing: u.Quantity = 1 * u.arcsec,
        moon_illumination: float = 0.5,
        airmass: float = 1,
    ):
        """
        Define the conditions for the observations

        Parameters
        ----------
        seeing : u.Quantity, optional
            seeing of the observation in arcsec, by default 1 arcsec
        moon_illumination : float, optional
            fraction of lunar illumination, by default 0.5
        airmass : float, optional
            airmass of the observation, by default 1
        """
        if not (0 <= moon_illumination <= 1):
            raise ValueError(
                f"moon_illumination must be between 0 and 1, but got {moon_illumination}"
            )

        #TODO: make these do something
        self.moon_illumination = moon_illumination
        self.airmass = airmass
        self.seeing = seeing

    @u.quantity_input(dit=u.s)
    def get_snr(
        self, band: str, mag: MagUnit, dit: u.Quantity, ndit: int
    ) -> float:
        """
        Calculate the Signal-to-Noise ratio for this observation

        Parameters
        ----------
        band : str
            the wavelength band to observe, should be one of the supported bands
        mag : Union[float, u.Quantity]
            the magnitude of the target star
        dit : u.Quantity
            integration time of one exposure in seconds
        ndit : int
            number of exposures

        Returns
        -------
        float
            signal to noise ratio
        """

        photons = self.photons_in_filter(band, mag)
        exposure_time = dit * ndit
        signal = photons * dit * self.quantum_efficiency

        if signal > self.linearity_limit:
            print("WARNING: Signal is above the linearity limit of the detector")
        if signal > self.saturation_limit:
            print("WARNING: Signal is above the saturation limit of the detector")
            signal = self.saturation_limit

        signal *= ndit

        readout_noise = self.readout_noise * ndit
        dark_noise = self.dark_noise * exposure_time
        photon_noise = np.sqrt(signal.to_value(u.electron / u.pixel))
        photon_noise *= u.electron / u.pixel
        # TODO: Sky Noise
        # TODO: other noise sources
        noise = readout_noise + dark_noise + photon_noise

        snr = (signal / noise).to_value(1)
        return snr

    @u.quantity_input(dit=u.s)
    def get_ndit(self, band:str, snr:float, mag: MagUnit, dit:u.Quantity) -> u.Quantity:
        """
        Calculate the number of exposures necessary to achieve the given signal-to-noise
        ratio for this target

        Parameters
        ----------
        band : str
            the wavelength band to observe, should be one of the supported bands
        snr : float
            signal to noise ratio
        mag : Union[float, u.Quantity]
            the magnitude of the target star
        dit : Quantity
            integration time in seconds

        Returns
        -------
        u.Quantity
            exposure time in seconds
        """
        if dit <= 0 * u.s:
            raise ValueError("DIT must be positive")
        
        # only emit the warning once
        is_warning = False
        # Start at one exposure and search for the next highest
        snr_n = 0
        ndit = 0
        while snr_n < snr:
            ndit += 1
            snr_n = self.get_snr(band, mag, dit, ndit)

            if ndit * dit >= 1 * u.hour and not is_warning:
                print("WARNING: total exposure time is longer than 1 hour")
                is_warning = True
            if ndit * dit >= 3 * u.hour:
                print("WARNING: The maximum exposure time of 3 hours was reached. Stopping the calculation.")
                break
                
        return ndit