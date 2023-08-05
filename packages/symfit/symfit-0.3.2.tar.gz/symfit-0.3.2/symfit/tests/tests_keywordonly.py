from __future__ import division, print_function
import unittest
import inspect
import sympy
import types
from sympy import init_printing, init_session
from sympy import symbols
import numpy as np
from symfit.core.support import sympy_to_scipy, sympy_to_py, RequiredKeywordError
try:

    from symfit.api import Variable, Parameter, Fit, FitResults, Maximize, Minimize, exp, Likelihood, ln, log, variables, parameters, Model, NumericalLeastSquares

    from symfit.distributions import Gaussian, Exp
    import scipy.stats
    from scipy.optimize import curve_fit

    import matplotlib.pyplot as plt
except RequiredKeywordError:
    pass

a, b, c = parameters('a, b, c')
a_i, b_i, c_i = variables('a_i, b_i, c_i')

model = {a_i: a, b_i: b, c_i: c}

xdata = np.array([
    [10.1, 9., 10.5, 11.2, 9.5, 9.6, 10.],
    [102.1, 101., 100.4, 100.8, 99.2, 100., 100.8],
    [71.6, 73.2, 69.5, 70.2, 70.8, 70.6, 70.1],
])

fit = NumericalLeastSquares(
    model=model,
    a_i=xdata[0],
    b_i=xdata[1],
    c_i=xdata[2],
)
fit_result = fit.execute()