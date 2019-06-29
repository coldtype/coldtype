from splipy import *
import numpy as np
from fractions import gcd
from math import pi


def lissajous(a, b, d):
    # request a,b integers, so we have closed, periodic curves
    n = np.gcd(a, b)
    N = (a/n) * (b/n)  # number of periods before looping

    # compute a set of interpolation points
    numb_pts = max(3*N, 100)  # using 3N interpolation points is decent enough
    t = np.linspace(0, 2*np.pi/n, numb_pts)
    x = np.array([np.sin(a*t + d), np.sin(b*t)])

    # do a cubic curve interpolation with periodic boundary conditions
    return curve_factory.cubic_curve(x.T, curve_factory.Boundary.PERIODIC)

print(lissajous(3, 4, pi/2))