# -*- coding: utf-8 -*-
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import least_squares, minimize_scalar

from pysme.continuum_and_radial_velocity import (
    ContinuumNormalizationMatch,
    match_rv_continuum,
)
from pysme.crvmatch import sme_crvmatch
from pysme.persistence import save_as_idl
from pysme.sme import SME_Structure

targets = ["WASP-18"]

for target in targets:
    fname = join(
        dirname(__file__), f"results/{target}_monh_teff_logg_vmic_vmac_vsini_fix2.sme"
    )
    sme = SME_Structure.load(fname)

    fname = join(dirname(__file__), "WASP18_03.out")
    idl = SME_Structure.load(fname)

    i = 6

    # plt.plot(sme.wave[i], sme.spec[i], label="sme spec")
    # plt.plot(idl.wave[i - 6], idl.spec[i - 6], label="idl spec")

    # plt.plot(sme.wave[i], sme.synth[i], label="sme synth")
    # plt.plot(idl.wave[i - 6], idl.synth[i - 6], label="idl synth")

    # f = lambda x: -(np.std(sme.spec[6] - gaussian_filter1d(sme.spec[6], x)) ** 2 / x)
    # result = minimize_scalar(f, bounds=[0.1, 5], method="Bounded")
    # sigma = result.x

    # sigmas = np.zeros(sme.nseg)
    # snr = np.zeros(sme.nseg)
    # for i in range(6, 30):
    #     x = np.linspace(1, 10, 100)
    #     y = [np.std(sme.spec[i] - gaussian_filter1d(sme.spec[i], _x)) for _x in x]
    #     y = np.gradient(y)
    #     sigmas[i] = x[np.argmin(y)]
    #     res = sme.spec[i] - gaussian_filter1d(sme.spec[i], sigmas[i])
    #     snr[i] = 1 / (np.nanmedian(np.abs(np.nanmedian(res) - res)) * 1.5)

    module = ContinuumNormalizationMatch()
    module.top_factor = 10_000
    cscale = module(
        sme,
        sme.wave[i],
        sme.synth[i],
        i,
    )
    x = sme.wave[i] - sme.wave[i, 0]
    cont = np.polyval(cscale[0], x)
    # plt.plot(cont)

    plt.plot(sme.wave[i], sme.spec[i], label="sme spec")
    plt.plot(idl.wave[i - 6], idl.spec[i - 6], label="idl spec")

    plt.plot(sme.wave[i], sme.synth[i], label="sme synth")
    plt.plot(sme.wave[i], sme.synth[i] * cont, label="sme synth extra")
    plt.plot(idl.wave[i - 6], idl.synth[i - 6], label="idl synth")

    plt.legend()
    plt.show()

    ratio = sme.spec[i, 1:] / idl.spec[i - 6]

    cscale, cfit, bfit = sme_crvmatch(
        sme.wave[i],
        sme.synth[i],
        sme.wave[i],
        sme.spec[i],
        sme.uncs[i],
        sme.mask[i],
        1,
        np.mean(sme.wave[i]),
        0,
        np.ones(2),
        fixv=True,
    )

    plt.plot(sme.wave[i], cfit, label="cfit")

    plt.legend()
    plt.show()

    for i in range(6, 30):
        cscale, cfit, bfit = sme_crvmatch(
            sme.wave[i],
            sme.synth[i],
            sme.wave[i],
            sme.spec[i],
            sme.uncs[i],
            sme.mask[i],
            1,
            np.mean(sme.wave[i]),
            0,
            np.ones(2),
            fixv=True,
        )

        (line4,) = plt.plot(sme.wave[i], sme.spec[i], "tab:red", label="obs")
        (line1,) = plt.plot(sme.wave[i], cfit, "tab:orange", label="continuum")
        (line2,) = plt.plot(
            sme.wave[i], sme.synth[i] * cfit, "tab:blue", label="corrected"
        )
        (line3,) = plt.plot(sme.wave[i], sme.synth[i], "tab:green", label="synth")

    ax = plt.gca()
    ax.legend(
        handles=[line1, line2, line3, line4],
        # labels=["continuum", "corrected", "synth", "obs"],
    )
    plt.show()
    plt.savefig("crvmatch.png")

    sname = join(dirname(__file__), f"results/{target}.out")
    save_as_idl(sme, sname)
    print(target)
