from __future__ import division, print_function
import unittest
import warnings
import types
import time
import cProfile as profile
# import profile

import sympy
import numpy as np
from scipy.optimize import curve_fit

from symfit import Variable, Parameter, Fit, FitResults, LinearLeastSquares, parameters, variables, NumericalLeastSquares, NonLinearLeastSquares, Model
from symfit.core.support import seperate_symbols, sympy_to_py
from symfit.distributions import Gaussian

t_data = np.array([1.4, 2.1, 2.6, 3.0, 3.3])
y_data = np.array([10, 20, 30, 40, 50])

sigma = 0.2
n = np.array([5, 3, 8, 15, 30])
sigma_t = sigma / np.sqrt(n)

# We now define our model
t, y = variables('t, y')
g = Parameter()
# sqrt_g_inv = Parameter() # sqrt_g_inv = sqrt(1/g). Currently needed to linearize.
t_model = {t: (2 * y / g)**0.5}
# t_model = {t: 2 * y**0.5 * sqrt_g_inv + b}

# Different sigma for every point
fit = NonLinearLeastSquares(t_model, y=y_data, t=t_data, sigma_t=sigma_t)
# tick = time.time()

# fit_result =
profile.run('fit.execute()')
# print(time.time() - tick)

# fit = NumericalLeastSquares(t_model, y=y_data, t=t_data, sigma_t=sigma_t)
# tick = time.time()
# num_result = fit.execute()
# print(time.time() - tick)