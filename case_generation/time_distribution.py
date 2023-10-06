import numpy as np
import random
from scipy.integrate import quad


class DistributionCalculator:
    def __init__(self):
        self._normalization_constant = None
        self._cdf_values = None

    @staticmethod
    def pdf(x):
        general_peak = random.normalvariate(0.09, 0.025)
        morning_peak = np.exp(-(x - 9) ** 2 / 3)
        daily_peak = np.exp(-(x - 13.5) ** 2)
        evening_increase = np.exp(-(x - 18) ** 2 / 3)
        return min(1, general_peak + morning_peak + evening_increase + daily_peak)

    @property
    def normalization_constant(self):
        if self._normalization_constant is None:
            self._normalization_constant = quad(self.pdf, 0, 24)
        return self._normalization_constant

    def normalized_pdf(self, x):
        return self.pdf(x) / self.normalization_constant[0]

    def cdf(self, x):
        return quad(self.normalized_pdf, 0, x)[0]

    @property
    def cdf_values(self):
        if self._cdf_values is None:
            self._cdf_values = [self.cdf(x) for x in np.linspace(0, 24, 3600)]
        return self._cdf_values

    def inverse_cdf(self, u):
        return np.interp(u, self.cdf_values, np.linspace(0, 24, 3600))
