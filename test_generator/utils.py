import random
import numpy as np
from scipy.integrate import quad


def pdf(x):
    general_peak = random.normalvariate(0.09, 0.025)
    morning_peak = np.exp(-(x - 9) ** 2 / 3)
    daily_peak = np.exp(-(x - 13.5) ** 2)
    evening_increase = np.exp(-(x - 18) ** 2 / 3)
    return min(1, general_peak + morning_peak + evening_increase + daily_peak)


normalization_constant = quad(pdf, 0, 24)


def normalized_pdf(x):
    return pdf(x) / normalization_constant[0]


def cdf(x):
    return quad(normalized_pdf, 0, x)[0]


cdf_values = [cdf(x) for x in np.linspace(0, 24, 3600)]


def inverse_cdf(u):
    return np.interp(u, cdf_values, np.linspace(0, 24, 3600))
