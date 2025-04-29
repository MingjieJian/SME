# -*- coding: utf-8 -*-
"""
Utility functions for SME

safe interpolation
"""

import argparse
import builtins
import contextlib
import logging
import os
import subprocess
import sys
from functools import wraps
from platform import python_version

import numpy as np
import pandas as pd
from numpy import __version__ as npversion
from pandas import __version__ as pdversion
from scipy import __version__ as spversion
from scipy.interpolate import interp1d
from scipy.interpolate import RBFInterpolator
from matplotlib.path import Path

from . import __version__ as smeversion
from .sme_synth import SME_DLL

logger = logging.getLogger(__name__)
show_progress_bars = False

def disable_progress_bars():
    global show_progress_bars
    show_progress_bars = False


def enable_progress_bars():
    global show_progress_bars
    show_progress_bars = True


@contextlib.contextmanager
def print_to_log():
    original_print = builtins.print

    def logprint(*args, file=None, **kwargs):
        # The debugger freaks out if we dont give it what it wants
        if file is not None:
            original_print(*args, **kwargs, file=file)
        elif len(args) != 0:
            logger.info(*args, **kwargs)

    builtins.print = logprint
    try:
        yield None
    finally:
        builtins.print = original_print


class getter:
    def __call__(self, func):
        @wraps(func)
        def fget(obj):
            value = func(obj)
            return self.fget(obj, value)

        return fget

    def fget(self, obj, value):
        raise NotImplementedError


class apply(getter):
    def __init__(self, app, allowNone=True):
        self.app = app
        self.allowNone = allowNone

    def fget(self, obj, value):
        if self.allowNone and value is None:
            return value
        if isinstance(self.app, str):
            return getattr(value, self.app)()
        else:
            return self.app(value)


class setter:
    def __call__(self, func):
        @wraps(func)
        def fset(obj, value):
            value = self.fset(obj, value)
            func(obj, value)

        return fset

    def fset(self, obj, value):
        raise NotImplementedError


class oftype(setter):
    def __init__(self, _type, allowNone=True, **kwargs):
        self._type = _type
        self.allowNone = allowNone
        self.kwargs = kwargs

    def fset(self, obj, value):
        if self.allowNone and value is None:
            return value
        elif value is None:
            raise TypeError(
                f"Expected value of type {self._type}, but got None instead"
            )
        return self._type(value, **self.kwargs)


class ofarray(setter):
    def __init__(self, dtype=float, allowNone=True):
        self.dtype = dtype
        self.allowNone = allowNone

    def fset(self, obj, value):
        if self.allowNone and value is None:
            return value
        elif value is None:
            raise TypeError(
                f"Expected value of type {self.dtype}, but got {value} instead"
            )
        arr = np.asarray(value, dtype=self.dtype)
        return np.atleast_1d(arr)


class oneof(setter):
    def __init__(self, allowed_values=()):
        self.allowed_values = allowed_values

    def fset(self, obj, value):
        if value not in self.allowed_values:
            raise ValueError(
                f"Expected one of {self.allowed_values}, but got {value} instead"
            )
        return value


class ofsize(setter):
    def __init__(self, shape, allowNone=True):
        self.shape = shape
        self.allowNone = allowNone
        if hasattr(shape, "__len__"):
            self.ndim = len(shape)
        else:
            self.ndim = 1
            self.shape = (self.shape,)

    def fset(self, obj, value):
        if self.allowNone and value is None:
            return value
        if hasattr(value, "shape"):
            ndim = len(value.shape)
            shape = value.shape
        elif hasattr(value, "__len__"):
            ndim = 1
            shape = (len(value),)
        else:
            ndim = 1
            shape = (1,)

        if ndim != self.ndim:
            raise ValueError(
                f"Expected value with {self.ndim} dimensions, but got {ndim} instead"
            )
        elif not all([i == j for i, j in zip(shape, self.shape)]):
            raise ValueError(
                f"Expected value of shape {self.shape}, but got {shape} instead"
            )
        return value


class absolute(oftype):
    def __init__(self):
        super().__init__(float)

    def fset(self, obj, value):
        value = super().fset(obj, value)
        if value is not None:
            value = abs(value)
        return value


class uppercase(oftype):
    def __init__(self):
        super().__init__(str)

    def fset(self, obj, value):
        value = super().fset(obj, value)
        if value is not None:
            value = value.upper()
        return value


class lowercase(oftype):
    def __init__(self):
        super().__init__(str)

    def fset(self, obj, value):
        value = super().fset(obj, value)
        if value is not None:
            value = value.lower()
        return value


def air2vac(wl_air, copy=True):
    """
    Convert wavelengths in air to vacuum wavelength
    in Angstrom
    Author: Nikolai Piskunov
    """
    if copy:
        wl_vac = np.copy(wl_air)
    else:
        wl_vac = np.asarray(wl_air)
    wl_air = np.asarray(wl_air)

    ii = np.where(wl_air > 1999.352)

    sigma2 = (1e4 / wl_air[ii]) ** 2  # Compute wavenumbers squared
    fact = (
        1e0
        + 8.336624212083e-5
        + 2.408926869968e-2 / (1.301065924522e2 - sigma2)
        + 1.599740894897e-4 / (3.892568793293e1 - sigma2)
    )
    wl_vac[ii] = wl_air[ii] * fact  # Convert to vacuum wavelength

    return wl_vac


def vac2air(wl_vac, copy=True):
    """
    Convert vacuum wavelengths to wavelengths in air
    in Angstrom
    Author: Nikolai Piskunov
    """
    if copy:
        wl_air = np.copy(wl_vac)
    else:
        wl_air = np.asarray(wl_vac)
    wl_vac = np.asarray(wl_vac)

    # Only works for wavelengths above 2000 Angstrom
    ii = np.where(wl_vac > 2e3)

    sigma2 = (1e4 / wl_vac[ii]) ** 2  # Compute wavenumbers squared
    fact = (
        1e0
        + 8.34254e-5
        + 2.406147e-2 / (130e0 - sigma2)
        + 1.5998e-4 / (38.9e0 - sigma2)
    )
    wl_air[ii] = wl_vac[ii] / fact  # Convert to air wavelength
    return wl_air


def safe_interpolation(x_old, y_old, x_new=None, fill_value=0):
    """
    'Safe' interpolation method that should avoid
    the common pitfalls of spline interpolation

    masked arrays are compressed, i.e. only non masked entries are used
    remove NaN input in x_old and y_old
    only unique x values are used, corresponding y values are 'random'
    if all else fails, revert to linear interpolation

    Parameters
    ----------
    x_old : array of size (n,)
        x values of the data
    y_old : array of size (n,)
        y values of the data
    x_new : array of size (m, ) or None, optional
        x values of the interpolated values
        if None will return the interpolator object
        (default: None)

    Returns
    -------
    y_new: array of size (m, ) or interpolator
        if x_new was given, return the interpolated values
        otherwise return the interpolator object
    """

    # Handle masked arrays
    if np.ma.is_masked(x_old):
        x_old = np.ma.compressed(x_old)
        y_old = np.ma.compressed(y_old)

    mask = np.isfinite(x_old) & np.isfinite(y_old)
    x_old = x_old[mask]
    y_old = y_old[mask]

    # avoid duplicate entries in x
    # also sorts data, which allows us to use assume_sorted below
    x_old, index = np.unique(x_old, return_index=True)
    y_old = y_old[index]

    try:
        interpolator = interp1d(
            x_old,
            y_old,
            kind="cubic",
            fill_value=fill_value,
            bounds_error=False,
            assume_sorted=True,
        )
    except ValueError:
        logger.warning(
            "Could not instantiate cubic spline interpolation, using linear instead"
        )
        interpolator = interp1d(
            x_old,
            y_old,
            kind="linear",
            fill_value=fill_value,
            bounds_error=False,
            assume_sorted=True,
        )

    if x_new is not None:
        return interpolator(x_new)
    else:
        return interpolator


def log_version():
    """For Debug purposes"""
    dll = SME_DLL()
    logger.debug("----------------------")
    logger.debug("Python version: %s", python_version())
    try:
        logger.debug("SME CLib version: %s", dll.SMELibraryVersion())
    except OSError:
        logger.debug("SME CLib version: ???")
    logger.debug("PySME version: %s", smeversion)
    logger.debug("Numpy version: %s", npversion)
    logger.debug("Scipy version: %s", spversion)
    logger.debug("Pandas version: %s", pdversion)


def start_logging(
    log_file="log.log",
    level="DEBUG",
    format="%(asctime)-15s - %(levelname)s - %(name)-8s - %(message)s",
):
    """Start logging to log file and command line

    Parameters
    ----------
    log_file : str, optional
        name of the logging file (default: "log.log")
    """

    try:
        level = getattr(logging, str(level).upper())
    except:
        raise ValueError(
            f"Logging level not recognized, try one of ['DEBUG', 'INFO', 'WARNING']"
        )

    name, _ = __name__.split(".", 1)
    logger = logging.getLogger(name)

    logger.setLevel(level)
    filehandler = logging.FileHandler(log_file, mode="w")
    formatter = logging.Formatter(format)
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

    logging.captureWarnings(True)
    log_version()


def redirect_output_to_file(output_file):
    """Redirect ALL output that would go to the commandline, to a file instead

    Parameters
    ----------
    output_file : str
        output filename
    """

    tee = subprocess.Popen(["tee", output_file], stdin=subprocess.PIPE)
    # Cause tee's stdin to get a copy of our stdin/stdout (as well as that
    # of any child processes we spawn)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

    # The flush flag is needed to guarantee these lines are written before
    # the two spawned /bin/ls processes emit any output
    print("\nHello World", flush=True)
    # print("\nstdout", flush=True)
    # print("stderr", file=sys.stderr, flush=True)

    # These child processes' stdin/stdout are
    # os.spawnve("P_WAIT", "/bin/ls", ["/bin/ls"], {})
    # os.execve("/bin/ls", ["/bin/ls"], os.environ)


def parse_args():
    """Parse command line arguments

    Returns
    -------
    sme : str
        filename to input sme structure
    vald : str
        filename of input linelist or None
    fitparameters : list(str)
        names of the parameters to fit, empty list if none are specified
    """

    parser = argparse.ArgumentParser(description="SME solve")
    parser.add_argument(
        "sme",
        type=str,
        help="an sme input file (either in IDL sav or Numpy npy format)",
    )
    parser.add_argument("--vald", type=str, default=None, help="the vald linelist file")
    parser.add_argument(
        "fitparameters",
        type=str,
        nargs="*",
        help="Parameters to fit, abundances are 'Mg Abund'",
    )
    args = parser.parse_args()
    return args.sme, args.vald, args.fitparameters

H_lineprof = pd.read_csv(os.path.expanduser("~/.sme/hlineprof/lineprof.dat"), sep=' +', names=['Teff', 'logg', 'Fe_H', 'nu', 'wl', 'wlair', 'mu', 'wmu', 'Ic', 'I'], engine='python')
H_lineprof['wl'] *= 10
H_lineprof['wl'] = vac2air(H_lineprof['wl'])

boundary_vertices = [
    (4000, 1.5), (4500, 1.5), (7000, 4.5), (7000, 5.0),
    (4500, 5.0), (4500, 2.5), (4000, 2.5), (4000, 1.5)
]

def interpolate_H_spectrum(
    df: pd.DataFrame,
    Teff_star: float,
    logg_star: float,
    FeH_star: float,
    boundary_vertices: list,
    rbf_kernel: str = 'linear',
    fill_value: float = np.nan,
):
    """
    Interpolates the hydrogen line spectrum (Ic and I) over a grid of stellar parameters
    (Teff, logg, FeH) using radial basis function (RBF) interpolation, with 
    boundary control in the Teff-logg space.

    Parameters
    ----------
    df : pd.DataFrame
        Hydrogen line profile data with columns:
        ['Teff', 'logg', 'Fe_H', 'mu', 'wl', 'wmu', 'Ic', 'I'].
    Teff_star : float
        Effective temperature to interpolate at.
    logg_star : float
        Surface gravity to interpolate at.
    FeH_star : float
        Metallicity to interpolate at.
    boundary_vertices : list of (Teff, logg)
        Defines interpolation region. Outside this, returns fill_value.
    rbf_kernel : str
        Kernel to use for RBFInterpolator.
    fill_value : float
        Value to return if point is outside interpolation region.
    output : str
        'intensity' returns detailed (mu, wl) values,
        'flux' returns integrated flux across mu for each wl.

    Returns
    -------
    pd.DataFrame
        Interpolated result as either intensity table or flux summary.
    """
    result = []
    point_star_2d = (Teff_star, logg_star)
    polygon = Path(boundary_vertices)
    in_boundary = polygon.contains_point(point_star_2d)
    unique_wl = df['wl'].unique()

    for wl in unique_wl:
        sub_df_wl = df[df['wl'] == wl]
        sub_results = []

        for mu in sub_df_wl['mu'].unique():
            sub_df = sub_df_wl[sub_df_wl['mu'] == mu]
            if sub_df.shape[0] < 4:
                continue

            wmu = sub_df['wmu'].iloc[0]

            if not in_boundary:
                sub_results.append([mu, wmu, fill_value, fill_value])
                continue

            points = sub_df[['Teff', 'logg', 'Fe_H']].values
            Ic_vals = sub_df['Ic'].values
            I_vals = sub_df['I'].values

            try:
                rbf_Ic = RBFInterpolator(points, Ic_vals, kernel=rbf_kernel)
                rbf_I = RBFInterpolator(points, I_vals, kernel=rbf_kernel)

                Ic_interp = rbf_Ic([[Teff_star, logg_star, FeH_star]])[0]
                I_interp = rbf_I([[Teff_star, logg_star, FeH_star]])[0]

                sub_results.append([mu, wmu, Ic_interp, I_interp])
            except Exception as e:
                print(f"Interpolation failed at mu={mu}, wl={wl}, skipped. Reason: {e}")
                continue

        for mu, wmu, Ic_interp, I_interp in sub_results:
            result.append([mu, wl, wmu, Ic_interp, I_interp])

    return pd.DataFrame(result, columns=['mu', 'wl', 'wmu', 'Ic_interp', 'I_interp']), in_boundary