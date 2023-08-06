# -*- coding: utf-8 -*-

from __future__ import division, print_function

import fnmatch
import logging
import numpy as np
from ._transit import CythonSolver

__all__ = ["Central", "Body", "System"]

try:
    from itertools import izip, imap
except ImportError:
    izip, imap = zip, map


# Newton's constant in $R_\odot^3 M_\odot^{-1} {days}^{-2}$.
_G = 2945.4625385377644

# A constant to convert between solar radii per day and m/s.
_rvconv = 1.242271746944644082e-04

# Solar mass & radius in cgs units
_Msun = 1.9891e33
_Rsun = 6.95508e10


class Central(object):
    """
    The "central"---in this context---is the massive central body in a
    :class:`System`.

    :param mass:
        The mass of the body measured in Solar masses. (default: ``1.0``)

    :param radius:
        The radius of the body measured in Solar radii. (default: ``1.0``)

    :param flux:
        The un-occulted flux measured in whatever units you feel like using.
        (default: ``1.0``)

    **Limb darkening** can be specified using ``(mu1, mu2)`` or ``(q1, q2)``.
    TODO: explain.

    """

    def __init__(self, mass=1.0, radius=1.0, flux=1.0, dilution=0.0,
                 q1=None, q2=None, mu1=None, mu2=None):
        self.mass = mass
        self.radius = radius
        self.flux = flux
        if not 0.0 <= dilution <= 1.0:
            raise ValueError("'dilution' must be between 0 and 1")
        self.dilution = dilution

        # Allow different limb darkening parameters.
        if mu1 is not None and mu2 is not None:
            if q1 is not None or q2 is not None:
                raise RuntimeError("You can't use *both* limb-darkening "
                                   "parameterizations!")
            self.coeffs = (mu1, mu2)
        else:
            self.q1 = q1 if q1 is not None else 0.5
            self.q2 = q2 if q2 is not None else 0.5

    @property
    def q1(self):
        return self._q1

    @q1.setter
    def q1(self, v):
        if not 0 <= v <= 1:
            raise ValueError("Invalid limb darkening coefficient")
        self._q1 = v

    @property
    def q2(self):
        return self._q2

    @q2.setter
    def q2(self, v):
        if not 0 <= v <= 1:
            raise ValueError("Invalid limb darkening coefficient")
        self._q2 = v

    @property
    def coeffs(self):
        q1, q2 = self.q1, self.q2
        q1 = np.sqrt(np.abs(q1))
        return 2*q1*q2, q1*(1-2*q2)

    @coeffs.setter
    def coeffs(self, value):
        u1, u2 = value
        u2 = u1+u2
        self.q1, self.q2 = u2*u2, 0.5*u1/u2

    @property
    def density(self):
        """Stellar density in CGS units
        """
        r = self.radius * _Rsun
        m = self.mass * _Msun
        return 0.75 * m / (np.pi * r * r * r)

    @density.setter
    def density(self, rho):
        r = self.radius * _Rsun
        m = np.pi * rho * r * r * r / 0.75
        self.mass = m / _Msun


class Body(object):
    r"""
    A "body"---in this context---is a (possibly) massive body orbiting a
    :class:`Central` in a :class:`System`. There are several ways to
    initialize this and once it has been added to a system using the
    :func:`System.add_body` method, they should all be equivalent. The orbital
    elements specified either specify a Keplerian orbit. This object includes
    all sorts of magic for converting between different specifications when
    needed but the base description of the planet and the orbit is
    parameterized by the parameters listed by
    :func:`System.get_parameter_vector`.

    :param r:
        The radius measured in Solar radii. (default: ``0.0``)

    :param mass:
        The mass in Solar masses. (default: ``0.0``)

    :param a:
        The semi-major axis of the orbit measured in Solar radii. Either this
        parameter or ``period`` must be provided but not both.

    :param period:
        The period of the orbit in days. Either this parameter or ``a`` must
        be provided but not both.

    :param t0:
        The epoch of the orbit in days. (default: ``0.0``)

    :param e:
        The eccentricity of the orbit. (default: ``0.0``)

    :param omega:
        The orientation of the orbital ellipse in radians as defined by Winn
        (2010). (default: ``0.0``)

    :param ix:
        The relative inclination of the orbital plane along the line-of-sight
        in degrees. This angle is measured differently than you're used to:
        zero degrees is edge on and 90 degrees in face on. This angle will be
        subtracted from the base inclination of the planetary system to get
        the standard measurement of the inclination. Either this parameter
        or ``b`` can be specified but not both. (default: ``0.0``)

    :param incl:
        An alternative to `ix` but defined in the standard way (90-deg is edge
        on).

    :param b:
        The mean impact parameter of the orbit measured in stellar radii (not
        Solar radii). Specifically, this impact parameter is defined as

        .. math::

            b = \frac{a}{R_\star} \cos i \,
                \left(\frac{1 - e^2}{1+e\,\sin\omega} \right)

        (default: ``0.0``)

    """

    def __init__(self,
                 radius=0.0,
                 mass=0.0,
                 a=None,
                 period=None,
                 t0=0.0,
                 e=0.0,
                 omega=0.0,
                 ix=None,
                 incl=None,
                 b=None,
                 # Deprecated:
                 r=None,
                 pomega=None):
        # Deprecation warnings.
        if r is not None:
            logging.warn("the argument 'r' is deprecated. "
                         "Use 'radius' instead")
        if pomega is not None:
            logging.warn("the argument 'pomega' is deprecated. "
                         "Use 'omega' instead")

        # Check the supplied arguments.
        assert sum((a is None, period is None)) == 1, \
            "you must provide one (and only one) of 'a' and 'period'"
        assert sum((b is None, ix is None, incl is None)) >= 2, \
            "you can give a value for up to one of 'b', 'ix', or 'incl'"
        if ix is None and b is None and incl is None:
            self._ix = 0.0

        # Base parameters.
        self.radius = radius if r is None else r
        self._a = a
        self._period = period
        self.mass = mass
        self.t0 = t0
        self.e = e
        self.omega = omega if pomega is None else pomega
        self._b = b
        self._ix = ix
        self._incl = incl

    def _check_ps(self):
        if not hasattr(self, "system"):
            raise RuntimeError("You must add this body to a system "
                               "before getting the period.")

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, r):
        if r < 0:
            raise ValueError("Invalid planet radius (must be non-negative)")
        self._radius = r

    @property
    def r(self):
        return self.radius

    @r.setter
    def r(self, r):
        self.radius = r

    @property
    def period(self):
        # If we already have a period, return that.
        if self._period is not None:
            return self._period

        # If not, check to make sure that we're already part of a system
        # and then compute the period based on the star's mass.
        self._check_ps()
        mstar = self.system.central.mass
        a = self._a
        return 2 * np.pi * np.sqrt(a * a * a / _G / (mstar + self.mass))

    @period.setter
    def period(self, P):
        if P <= 0.0:
            raise ValueError("Invalid period (must be positive)")
        self._check_ps()
        mstar = self.system.central.mass
        self._a = (_G*P*P*(self.mass+mstar)/(4*np.pi*np.pi)) ** (1./3)
        self._period = None

    @property
    def a(self):
        if self._a is None:
            self.period = self._period
        return self._a

    @a.setter
    def a(self, a):
        self._period = None
        self._a = a

    @property
    def incl(self):
        """
        The standard definition of inclination: 90-deg is edge on.

        """
        if self._incl is not None:
            return self._incl
        self._check_ps()
        return self.system.iobs + self.ix

    @incl.setter
    def incl(self, v):
        self._check_ps()
        self.ix = v - self.system.iobs
        self._incl = None

    @property
    def b(self):
        # If we already have an impact parameter, return that.
        if self._b is not None:
            return self._b

        # If not, check to make sure that we're already part of a system
        # and then compute the impact parameter based on the star's radius.
        self._check_ps()
        rstar = self.system.central.radius
        incl = np.radians(self.incl)

        # Compute contribution due to eccentricity.
        factor = 1.0
        e = self.e
        if e > 0.0:
            factor = (1 - e * e) / (1 + e * np.sin(self.omega))

        return self.a * np.cos(incl) / rstar * factor

    @b.setter
    def b(self, b):
        if b < 0.0:
            raise ValueError("Invalid impact parameter (must be non-negative)")

        self._check_ps()
        rstar = self.system.central.radius

        # Compute contribution due to eccentricity.
        factor = 1.0
        e = self.e
        if e > 0.0:
            factor = (1 + e * np.sin(self.omega)) / (1 - e * e)

        arg = b * factor * rstar / self.a
        if arg > 1.0:
            raise ValueError("Invalid impact parameter")
        self.incl = np.degrees(np.arccos(arg))
        self._b = None

    @property
    def ix(self):
        if self._ix is None:
            if self._b is not None:
                self.b = self._b
            elif self._incl is not None:
                self.incl = self._incl
            else:
                raise RuntimeError("Something went wrong.")
        return self._ix

    @ix.setter
    def ix(self, ix):
        self._b = None
        self._ix = ix

    @property
    def duration(self):
        """
        The approximate duration of the transit :math:`T_\mathrm{tot}` from
        Equation (14) in Winn (2010).

        """
        self._check_ps()

        rstar = self.system.central.radius
        k = self.r/rstar
        dur = self.period / np.pi
        arg = rstar/self.a * np.sqrt((1+k)**2 - self.b**2)
        arg /= np.sin(np.radians(self.incl))
        dur *= np.arcsin(arg)
        if self.e > 0.0:
            dur *= np.sqrt(1 - self.e**2) / (1 + self.e * np.sin(self.omega))
        return dur

    @property
    def e(self):
        return self._e

    @e.setter
    def e(self, e):
        if not 0 <= e < 1.0:
            raise ValueError("Only bound orbits are permitted (0 <= e < 1)")
        self._e = e
        self._b = None

    @property
    def omega(self, hp=0.5*np.pi):
        return self.pomega

    @omega.setter
    def omega(self, v, hp=0.5*np.pi):
        self.pomega = v


class System(object):
    """
    A "planetary system" contains a "central" bright :class:`Central` and some
    number (``>= 0``) :class:`Body` objects orbiting. The default orbits
    are purely Keplerian but sub-classes can include more sophisticated
    solvers.

    :param central:
        A :class:`Central` that specifies the central bright object.

    :para iobs:
        The inclination of the mean orbital plane in degrees. This is
        measured in the standard way with zero inclination meaning face on and
        90 degrees is edge on. (default: ``90.0``)

    """

    def __init__(self, central, iobs=90.0):
        self.central = central
        self.central.system = self
        self.bodies = []
        self.iobs = iobs
        self.unfrozen = np.zeros(6, dtype=bool)

    def add_body(self, body):
        """
        Add a :class:`Body` to the system. This function also sets the
        ``system`` attribute of the body.

        :param body:
            The :class:`Body` to add.

        """
        body.system = self
        self.bodies.append(body)
        self.unfrozen = np.concatenate((
            self.unfrozen[:-2], np.zeros(7, dtype=bool), self.unfrozen[-2:]
        ))

    def _get_solver(self):
        return CythonSolver()

    def light_curve(self, t, texp=0.0, tol=1e-8, maxdepth=4):
        """
        Get the light curve evaluated at a list of times using the current
        model.

        :param t:
            The times where the light curve should be evaluated (in days).

        :param tol:
            The stopping criterion for the exposure time integration.

        :param maxdepth:
            The maximum recursion depth of the exposure time integrator.

        """
        t = np.atleast_1d(t)
        if len(self.bodies) == 0:
            return self.central.flux + np.zeros_like(t)

        return CythonSolver().kepler_light_curve(len(self.bodies),
                                                 self._get_params(),
                                                 t, texp, tol, maxdepth)

    def light_curve_gradient(self, t, texp=0.0, tol=1e-8, maxdepth=4):
        """
        Get the light curve evaluated at a list of times using the current
        model.

        :param t:
            The times where the light curve should be evaluated (in days).

        :param tol:
            The stopping criterion for the exposure time integration.

        :param maxdepth:
            The maximum recursion depth of the exposure time integrator.

        """
        t = np.atleast_1d(t)
        if len(self.bodies) == 0:
            grad = np.zeros((len(t), 5), dtype=float)
            grad[:, 0] = 1.0
            return self.central.flux + np.zeros_like(t), grad[:, self.unfrozen]

        f, df = CythonSolver().kepler_gradient(len(self.bodies),
                                               self._get_params(),
                                               t, texp, tol, maxdepth)
        return f, df[:, self.unfrozen].T

    def __len__(self):
        return np.sum(self.unfrozen)

    def _parameter_names(self):
        names = ["central:ln_flux", "central:ln_radius", "central:ln_mass"]
        for i, body in enumerate(self.bodies):
            names += map("bodies[{0}]:{{0}}".format(i).format,
                         ("ln_radius", "ln_mass", "t0",
                          "sqrt_e_cos_omega", "sqrt_e_sin_omega",
                          "sqrt_a_cos_i", "sqrt_a_sin_i"))
        names += ["central:q1", "central:q2", "central:dilution"]
        return names

    def get_parameter_names(self, full=False):
        if full:
            return self._parameter_names()
        return [n for n, f in zip(self._parameter_names(), self.unfrozen)
                if f]

    def check_vector(self, vector):
        params = self._get_params()
        params[self.unfrozen] = vector
        for i, body in enumerate(self.bodies):
            n = 3 + 7 * i
            ecosp, esinp = params[n+3:n+5]
            e = ecosp**2 + esinp**2
            if not 0 <= e < 1.0:
                return False
        return True

    def get_vector(self):
        return self._get_params()[self.unfrozen]

    def _get_params(self):
        params = np.empty(6+7*len(self.bodies))
        params[0] = np.log(self.central.flux)
        params[1] = np.log(self.central.radius)
        params[2] = np.log(self.central.mass)
        params[-3] = np.log(self.central.q1)-np.log(1.0-self.central.q1)
        params[-2] = np.log(self.central.q2)-np.log(1.0-self.central.q2)
        params[-1] = \
            np.log(self.central.dilution)-np.log(1.0-self.central.dilution)

        for i, body in enumerate(self.bodies):
            n = 3 + 7 * i
            params[n] = np.log(body.r)
            params[n+1] = np.log(max(body.mass, 1e-14))
            params[n+2] = body.t0
            params[n+3] = np.sqrt(body.e) * np.cos(body.omega)
            params[n+4] = np.sqrt(body.e) * np.sin(body.omega)

            sa = np.sqrt(body.a)
            ix = np.radians(self.iobs + body.ix)
            params[n+5] = sa * np.cos(ix)
            params[n+6] = sa * np.sin(ix)

        return params

    def set_vector(self, vector):
        params = self._get_params()
        params[self.unfrozen] = vector
        self._set_params(params)

    def _set_params(self, params):
        self.central.flux = np.exp(params[0])
        self.central.radius = np.exp(params[1])
        self.central.mass = np.exp(params[2])
        self.central.q1 = max(0.0, min(1.0, 1.0 / (1. + np.exp(-params[-3]))))
        self.central.q2 = max(0.0, min(1.0, 1.0 / (1. + np.exp(-params[-2]))))
        self.central.dilution = \
            max(0.0, min(1.0, 1.0 / (1. + np.exp(-params[-1]))))

        for i, body in enumerate(self.bodies):
            n = 3 + 7 * i

            body.r = np.exp(params[n])
            body.mass = np.exp(params[n+1])
            body.t0 = params[n+2]

            ecosp, esinp = params[n+3:n+5]
            body.e = ecosp**2 + esinp**2
            body.pomega = np.arctan2(esinp, ecosp)

            ax, ay = params[n+5:n+7]
            body.a = ax**2 + ay**2
            body.ix = np.degrees(np.arctan2(ay, ax)) - self.iobs

    def get_value(self, t, **kwargs):
        return self.light_curve(t, **kwargs)

    def get_gradient(self, t, **kwargs):
        return self.light_curve_gradient(t, **kwargs)[1]

    def freeze_parameter(self, parameter_name):
        any_ = False
        for i, k in enumerate(self._parameter_names()):
            if not fnmatch.fnmatch(k, parameter_name):
                continue
            any_ = True
            self.unfrozen[i] = False
        if not any_:
            raise ValueError("unknown parameter '{0}'".format(parameter_name))

    def thaw_parameter(self, parameter_name):
        any_ = False
        for i, k in enumerate(self._parameter_names()):
            if not fnmatch.fnmatch(k, parameter_name):
                continue
            any_ = True
            self.unfrozen[i] = True
        if not any_:
            raise ValueError("unknown parameter '{0}'".format(parameter_name))

    def get_parameter(self, parameter_name):
        vector = self._get_params()
        params = []
        for i, k in enumerate(self._parameter_names()):
            if not fnmatch.fnmatch(k, parameter_name):
                continue
            params.append(vector[i])
        if len(params) == 0:
            raise ValueError("unknown parameter '{0}'".format(parameter_name))
        if len(params) == 1:
            return params[0]
        return np.array(params)

    def set_parameter(self, parameter_name, value):
        vector = self._get_params()
        any_ = False
        for i, k in enumerate(self._parameter_names()):
            if not fnmatch.fnmatch(k, parameter_name):
                continue
            any_ = True
            vector[i] = value
        if not any_:
            raise ValueError("unknown parameter '{0}'".format(parameter_name))
        self._set_params(vector)

    def get_bounds(self):
        return [(None, None) for _ in range(len(self))]

    def jacobian(self):
        star = self.central
        j = 0.0
        names = self.get_parameter_names()
        if "central:q1" in names:
            q = star.q1
            j += np.log(q) + np.log(1.0 - q)
        if "central:q2" in names:
            q = star.q2
            j += np.log(q) + np.log(1.0 - q)
        if "central:dilution" in names:
            q = star.dilution
            j += np.log(q) + np.log(1.0 - q)
        return j

    def jacobian_gradient(self):
        names = self.get_parameter_names()
        j = np.zeros(len(names))
        if "central:q1" in names:
            q = self.central.q1
            j[names.index("central:q1")] = 1. - 2*q
        if "central:q2" in names:
            q = self.central.q2
            j[names.index("central:q2")] = 1. - 2*q
        if "central:dilution" in names:
            q = self.central.dilution
            j[names.index("central:dilution")] = 1. - 2*q
        return j
