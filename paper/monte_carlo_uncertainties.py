# -*- coding: utf-8 -*-
""" Minimum working example of an SME script
"""
import os.path
import sys
from os.path import dirname, join

import numpy as np
from tqdm import tqdm

from pysme import sme as SME
from pysme.abund import Abund
from pysme.linelist.vald import ValdFile
from pysme.solve import solve
from pysme.synthesize import synthesize_spectrum


def setup_sme_structure(wrange):
    sme = SME.SME_Structure()

    vald_fname = join(dirname(__file__), "monte_carlo.lin")
    sme.linelist = ValdFile(vald_fname)

    sme.teff = 6000
    sme.logg = 4.4
    sme.monh = 0.0
    sme.abund = Abund(sme.monh, "asplund2009")

    sme.vsini = 1
    sme.vmic = 2
    sme.vmac = 4

    wmin = sme.linelist["wlcent"].min()
    wmax = sme.linelist["wlcent"].max()
    step = (wmax - wmin) / 4
    if wrange == 1:
        wmin = wmin
        wmax = wmin + step
    elif wrange == 2:
        wmin = wmin
        wmax = wmin + 2 * step
    elif wrange == 3:
        wmin = wmin
        wmax = wmin + 3 * step
    else:
        wmin = wmin
        wmax = wmax
    rv = 100
    # wmin *= 1 - rv / 3e5
    # wmax *= 1 + rv / 3e5

    sme.wave = np.linspace(wmin, wmax, 1000)
    sme.linelist = sme.linelist.trim(wmin, wmax, rvel=rv)

    sme.vrad = 0
    sme.vrad_flag = "whole"
    sme.cscale_flag = "none"
    sme.cscale_type = "match"

    sme.leastsquares_loss = "linear"

    sme = synthesize_spectrum(sme)
    return sme


if __name__ == "__main__":
    # initialize randomness
    rng = np.random.default_rng(0)
    fitparameters = ["teff", "logg", "monh"]
    scale = {"teff": 100, "logg": 1, "monh": 1}

    # Parse command line parameters
    if len(sys.argv) > 1:
        snr = float(sys.argv[1])
        wrange = int(sys.argv[2])
    else:
        snr = float(100)
        wrange = int(1)

    # generate synthetic sme structure
    sme = setup_sme_structure(wrange)
    spec_true = sme.synth.copy()
    sme.spec = spec_true.copy()

    # signal to noise ratio of 100 is roughly what we expect to have in good cases
    # TODO: experiment with lower values
    nrepeats = 1000
    nparam = len(fitparameters)

    # Store initial "true" parameters
    values_true = np.array([sme[fp] for fp in fitparameters])
    values = np.zeros((nparam, nrepeats))
    values_input = np.zeros((nparam, nrepeats))
    uncs = np.zeros((nparam, nrepeats))
    uncs_sme = np.zeros((nparam, nrepeats))

    for i in tqdm(range(nrepeats), total=nrepeats):
        # Generate a noise input spectrum
        noise = rng.standard_normal(sme.spec[0].size) / snr
        spec_copy = spec_true.copy()
        sme.spec[0] = spec_copy * (1 + noise)
        sme.uncs = np.sqrt(sme.spec)
        # Initialize first guess randomly
        for j, fp in enumerate(fitparameters):
            sme[fp] = values_true[j] + rng.standard_normal() * scale[fp]
            values_input[j, i] = sme[fp]
        # find the best fit parameters
        try:
            sme = solve(sme, fitparameters)
            # Store the parameters for analysis
            for j, fp in enumerate(fitparameters):
                values[j, i] = sme[fp]
                uncs[j, i] = sme.fitresults.fit_uncertainties[j]
                uncs_sme[j, i] = sme.fitresults.uncertainties[j]
        except Exception as e:
            print(e)
            for j, fp in enumerate(fitparameters):
                values[j, i] = np.nan
                uncs[j, i] = np.nan
                uncs_sme[j, i] = np.nan

        np.savez(
            f"mc_uncs_snr{snr}_w{wrange}.npz",
            values=values,
            values_input=values_input,
            values_true=values_true,
            uncs=uncs,
            uncs_sme=uncs_sme,
            fitparameters=fitparameters,
        )

    pass
