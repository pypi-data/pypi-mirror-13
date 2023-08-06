import numpy as np
from astroML.datasets import fetch_sdss_corrected_spectra
data = fetch_sdss_corrected_spectra()

spectra = data['spectra']
mask = data['mask']

weights = np.ones_like(spectra)
weights[mask] = 1E-6

from wpca import WPCA
pca = WPCA(20).fit(spectra, weights)
