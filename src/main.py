from astropy import units as u
from etc import ETC

filter = "H2"
mag = 20
dit = 10 * u.s
ndit = 60

etc = ETC()
etc.initialize_observing_conditions(moon_illumination=0.5, airmass=1.5)
ph = etc.photons_in_filter(filter, mag)
snr = etc.get_snr(filter, mag, dit, ndit)
print(snr)

ndit = etc.get_ndit(filter, 10, mag, dit)
print(ndit)
