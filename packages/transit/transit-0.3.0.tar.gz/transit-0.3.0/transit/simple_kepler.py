# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = []

import numpy as np


# Newton's constant in $R_\odot^3 M_\odot^{-1} {days}^{-2}$.
_G = 2945.462538537765


def get_time(t, t0, period, e, omega, Omega):
    f0 = 0.5 * np.pi - omega
    E0 = 2.*np.arctan2(np.sqrt(1-e)*np.tan(0.5*f0), np.sqrt(1+e))
    M0 = E0 - e*np.sin(E0)
    t1 = t0 - period * M0 / (2*np.pi)
    return t - t1


def get_period(a, m1, m2, _const=4.0*np.pi**2/_G):
    return np.sqrt(_const * a**3 / (m1 + m2))


def get_a(period, m1, m2, _const=4.0*np.pi**2/_G):
    return (period**2 * (m1 + m2) / _const) ** (1./3)


def get_mean_anomaly(t, period):
    return t * 2.0 * np.pi / period


def get_ecc_anomaly(M, e, maxiter=200, tol=1.48e-7):
    wt = M % (2. * np.pi)
    E0 = wt
    for _ in xrange(maxiter):
        f = E0 - e * np.sin(E0) - wt
        fp = 1. - e * np.cos(E0)
        fpp = e * np.sin(E0)
        E = E0 - 2.0 * f * fp / (2.0 * fp * fp - f * fpp)
        if np.abs((E - E0) / E) < tol:
            return E
        E0 = E
    raise RuntimeError("didn't converge")


def get_r(a, e, E):
    return a * (1. - e * np.cos(E))


def get_f(a, e, E):
    return 2. * np.arctan2(np.sqrt(1.+e) * np.tan(0.5*E), np.sqrt(1.-e))
    # f = 2.*atan(sqrt((1.+ecc)/(1.-ecc))*tan(E/2.));
    # arg = (a * (1. - e**2) / r - 1) / e
    # return np.sign(arg) * np.arccos(arg)


def get_xyz(t, a, e, m1, m2, t0, i, omega, Omega):
    # omega -= 0.5 * np.pi
    period = get_period(a, m1, m2)
    time = get_time(t, t0, period, e, omega, Omega)
    M = get_mean_anomaly(time, period)
    E = np.array([get_ecc_anomaly(M0, e) for M0 in M])
    r = get_r(a, e, E)
    f = get_f(a, e, E)
    swpf = np.sin(omega)*np.cos(f) + np.cos(omega)*np.sin(f)
    cwpf = np.cos(omega)*np.cos(f) - np.sin(omega)*np.sin(f)

    return (
        r * cwpf,
        r * swpf * np.cos(i),
        r * swpf * np.sin(i)
    )
