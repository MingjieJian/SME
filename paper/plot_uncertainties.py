# -*- coding: utf-8 -*-
import json
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import erf
from tqdm import tqdm

from pysme.sme import SME_Structure


def estimate_uncertainties(resid, deriv, names=None, plot=False):
    """
    Estimate the uncertainties by fitting the cumulative distribution of
    derivative / uncertainties vs. residual / derivative
    with the generalized normal distribution and use the 68% percentile
    as the 1 sigma approximation for a normally distributed variable

    Parameters
    ----------
    unc : array of shape (n,)
        uncertainties
    resid : array of shape (n,)
        residuals of the least squares fit
    deriv : array of shape (n, p)
        derivatives (jacobian) of the least squares fit for each parameter

    Returns
    -------
    freep_unc : array of shape (p,)
        uncertainties for each free paramater, in the same order as self.parameter_names
    """

    nparameters = deriv.shape[1]
    freep_unc = np.zeros(nparameters)

    # The goodness of fit
    # but the metric below, is already indifferent to
    # the absolute scale of the uncertainties
    # chi2 = np.sum(resid ** 2) / (resid.size - nparameters)

    # def cdf(x, mu, alpha):
    #     """
    #     Cumulative distribution function of the generalized normal distribution
    #     the factor sqrt(2) is a conversion between generalized and regular normal distribution
    #     """
    #     # return gennorm.cdf(x, beta, loc=mu, scale=alpha * np.sqrt(2))
    #     return norm.cdf(x, loc=mu, scale=alpha)

    # def std(mu, alpha):
    #     """1 sigma (68.27 %) quantile, assuming symmetric distribution"""
    #     # interval = gennorm.interval(0.6827, beta, loc=mu, scale=alpha * np.sqrt(2))
    #     interval = norm.interval(0.6827, loc=mu, scale=alpha)
    #     sigma = (interval[1] - interval[0]) / 2
    #     return sigma

    plot_names = {
        "teff": r"$T_{eff}$",
        "logg": r"$\log(g)$",
        "monh": r"[M/H]",
        "vmic": r"$v_{mic}$",
        "vmac": r"$v_{mac}$",
        "vsini": r"$v \sin(i)$",
    }

    for i in tqdm(range(nparameters), total=nparameters):
        pder = deriv[:, i]
        idx = pder != 0
        idx &= np.isfinite(pder)

        if np.count_nonzero(idx) <= 5:
            continue
        # Sort pixels according to the change of the i
        # parameter needed to match the observations
        idx_sort = np.argsort(resid[idx] / pder[idx])
        ch_x = resid[idx][idx_sort] / pder[idx][idx_sort]
        # Weights of the individual pixels also sorted
        # uncertainties are already included in pder / unc[idx][idx_sort]
        ch_y = np.abs(pder[idx][idx_sort])
        # Cumulative weights
        ch_y = np.cumsum(ch_y)
        # Normalized cumulative weights
        ch_y /= ch_y[-1]

        hmed = np.interp(0.5, ch_y, ch_x)
        interval = np.interp([0.16, 0.84], ch_y, ch_x)
        sigma = (interval[1] - interval[0]) / 2
        freep_unc[i] = sigma

        if plot:
            # Fit the distribution
            print(f"Plot {names[i]}")

            # Cumulative distribution function of the normal distribution
            cdf = lambda x, mu, sig: 0.5 * (1 + erf((x - mu) / (np.sqrt(2) * sig)))
            std = lambda mu, sig: sig
            pdf = (
                lambda x, mu, sig: 1
                / np.sqrt(2 * np.pi * sig ** 2)
                * np.exp(-0.5 * ((x - mu) / sig) ** 2)
            )

            # Plot 1 (cumulative distribution)

            color = "k"
            # plt.axvline(hmed, color="tab:blue", ls="--")
            # plt.axhline(0.5, color="tab:blue", ls="--")
            plt.axvline(hmed - sigma, color=color, ls="dashdot", alpha=0.5)
            plt.axvline(hmed + sigma, color=color, ls="dashdot", alpha=0.5)
            plt.axhline(0.84, color=color, ls="dashdot", alpha=0.5)
            plt.axhline(0.16, color=color, ls="dashdot", alpha=0.5)

            plt.plot(ch_x, ch_y, "-", label="residual/derivative", lw=2)
            plt.plot(ch_x, cdf(ch_x, hmed, sigma), label="gaussian fit", lw=2)

            vmin, vmax = hmed - 5 * sigma, hmed + 5 * sigma
            plt.xlim(vmin, vmax)
            plt.xlabel(fr"$\Delta${plot_names[names[i]]}")
            plt.ylabel("cumulative probability")
            plt.tight_layout()
            plt.legend(loc="upper left")
            plt.savefig(f"cumulative_probability_{names[i]}.pdf")
            # plt.show()
            plt.clf()

            # Plot 2 (density distribution)
            r = (hmed - 5 * sigma, hmed + 5 * sigma)
            x = np.linspace(r[0], r[-1], 1000)
            dist, bins, _ = plt.hist(
                ch_x,
                bins="auto",
                density=True,
                histtype="step",
                range=r,
                label="residual/derivative",
            )
            plt.plot(x, pdf(x, hmed, sigma), label="gaussian fit")

            imin, imax = np.digitize((hmed - sigma, hmed + sigma), bins, right=True)
            imin -= 1
            imax -= 1
            xfill = (hmed - sigma, *bins[imin + 1 : imax + 1], hmed + sigma)
            yfill = (
                dist[imin],
                *dist[imin + 1 : imax + 1],
                dist[imax + 2],
            )
            plt.fill_between(
                xfill,
                0,
                yfill,
                alpha=0.5,
                color="tab:orange",
                step="post",
            )

            idx = np.digitize(hmed, bins) - 1
            plt.vlines(hmed, 0, dist[idx], ls="--", colors="tab:blue")

            plt.vlines(
                (hmed - sigma, hmed + sigma),
                0,
                (dist[imin], dist[imax]),
                ls="dashdot",
                colors="tab:blue",
            )

            plt.xlabel(fr"$\Delta${plot_names[names[i]]}")
            plt.ylabel("probability")
            plt.xlim(r)
            plt.legend(loc="upper right")
            plt.tight_layout()
            plt.savefig(f"probability_density_{names[i]}.pdf")
            # plt.show()
            plt.clf()

    return freep_unc


target = "Eps_Eri"

cwd = dirname(__file__)

fname = join(cwd, f"results/{target}_monh_teff_logg_vmic_vmac_vsini_fix3.sme")
sme = SME_Structure.load(fname)

resid = sme.fitresults.residuals
deriv = sme.fitresults.derivative
uncs = estimate_uncertainties(resid, deriv, names=sme.fitresults.parameters, plot=True)
