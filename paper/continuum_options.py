# -*- coding: utf-8 -*-
""" Minimum working example of an SME script
"""

from os.path import dirname, join, realpath

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import readsav
from scipy.ndimage import label as scipy_label

from pysme import sme as SME
from pysme import util
from pysme.abund import Abund
from pysme.linelist.vald import ValdFile
from pysme.persistence import save_as_idl
from pysme.solve import solve
from pysme.synthesize import synthesize_spectrum

if __name__ == "__main__":
    # Define the location of all your files
    # this will put everything into the example dir
    examples_dir = dirname(realpath(__file__))
    mask_file = join(examples_dir, "continuum.sme")
    in_file = join(examples_dir, "gr8_HARPS_HD148816.inp")

    # Load your existing SME structure or create your own
    sme = SME.SME_Structure.load(in_file)
    sme_mask = SME.SME_Structure.load(mask_file)

    sme.mask = np.copy(sme_mask.mask)
    # sme.nmu = 7
    # sme.teff = 5770
    # sme.logg = 4.4
    # sme.abund = Abund(0, "asplund2009")
    # sme.vmic = 1
    # sme.vmac = 2
    # sme.vsini = 2

    # sme.atmo.source = "marcs2014.sav"
    # sme.linelist = ValdFile(join(examples_dir, "sun.lin"))

    # orig = np.copy(sme.synth[0])

    # Start SME solver
    sme.cscale = None
    sme.vrad_flag = "whole"

    continuum = {}
    synth = {}
    x = sme.wave[0] - sme.wave[0][0]
    # Mask linear
    sme.cscale_type = "mask"
    sme.cscale_flag = "linear"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["mask+linear"] = np.polyval(sme.cscale[0], x)
    synth["mask+linear"] = np.copy(sme.synth[0])
    # Mask quadratic
    sme.cscale_type = "mask"
    sme.cscale_flag = "quadratic"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["mask+quadratic"] = np.polyval(sme.cscale[0], x)
    synth["mask+quadratic"] = np.copy(sme.synth[0])
    # Match linear
    sme.cscale_type = "match"
    sme.cscale_flag = "linear"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["match+linear"] = np.polyval(sme.cscale[0], x)
    synth["match+linear"] = np.copy(sme.synth[0])
    # Match quadratic
    sme.cscale_type = "match"
    sme.cscale_flag = "quadratic"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["match+quadratic"] = np.polyval(sme.cscale[0], x)
    synth["match+quadratic"] = np.copy(sme.synth[0])
    # Match+Mask linear
    sme.cscale_type = "match+mask"
    sme.cscale_flag = "linear"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["match+mask+linear"] = np.polyval(sme.cscale[0], x)
    synth["match+mask+linear"] = np.copy(sme.synth[0])
    # Match+Mask quadratic
    sme.cscale_type = "match+mask"
    sme.cscale_flag = "quadratic"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["match+mask+quadratic"] = np.polyval(sme.cscale[0], x)
    synth["match+mask+quadratic"] = np.copy(sme.synth[0])
    # Matchlines
    sme.cscale_type = "matchlines"
    sme.cscale_flag = "linear"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["matchlines+linear"] = np.polyval(sme.cscale[0], x)
    synth["matchlines+linear"] = np.copy(sme.synth[0])
    # Matchlines+Mask
    sme.cscale_type = "matchlines+mask"
    sme.cscale_flag = "linear"
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["matchlines+mask+linear"] = np.polyval(sme.cscale[0], x)
    synth["matchlines+mask+linear"] = np.copy(sme.synth[0])
    # Spline
    sme.cscale_type = "spline"
    sme.cscale_flag = 2
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["spline"] = sme.cscale[0]
    synth["spline"] = np.copy(sme.synth[0])
    # Spline+Mask
    sme.cscale_type = "spline+mask"
    sme.cscale_flag = 2
    sme.cscale = None
    sme.vrad = None
    sme = synthesize_spectrum(sme, segments=[0])
    continuum["spline+mask"] = sme.cscale[0]
    synth["spline+mask"] = np.copy(sme.synth[0])
    # MCMC
    # sme.cscale_type = "mcmc"
    # sme.cscale_flag = "linear"
    # sme.cscale = None
    # sme.vrad = None
    # sme = synthesize_spectrum(sme, segments=[0])
    # continuum["mcmc+linear"] = np.polyval(sme.cscale[0], x)

    # Add last calculate the spectrum without continuum correction
    sme.cscale_type = "mask"
    sme.cscale_flag = "none"
    sme = synthesize_spectrum(sme, segments=[0])

    # Plot results
    for label, cont in continuum.items():

        plot_file = join(dirname(__file__), f"images/continuum_{label}.pdf")
        plt.plot(sme.wave[0], sme.spec[0], label="Observation", color="tab:blue")
        # plt.plot(sme.wave[0], sme.synth[0], label="Synthetic")

        plt.plot(sme.wave[0], cont, label=f"{label} Continuum", color="tab:purple")
        plt.plot(
            sme.wave[0],
            synth[label],
            label=f"{label} Corrected",
            color="tab:orange",
            linestyle="dotted",
        )

        m = sme.mask[0] == 2
        labels, n = scipy_label(m)
        ax = plt.gca()
        ybound = ax.get_ybound()
        for i in range(1, n + 1):
            mask = labels == i
            # plt.plot(
            #     sme.wave[0][mask],
            #     sme.spec[0][mask],
            #     color="tab:green",
            #     label="Mask" if i == 1 else None,
            #     lw=5,
            # )
            plt.fill_between(
                sme.wave[0][mask],
                0,
                1,
                alpha=0.5,
                color="tab:green",
                transform=ax.get_xaxis_transform(),
                label="Mask" if i == 1 else None,
            )

        plt.legend(loc="lower left", fontsize="small")
        plt.xlabel("Wavelength [Å]")
        plt.ylabel("Flux [A.U.]")
        # plt.ylim(0.9, 1.01)
        plt.savefig(plot_file)
        plt.clf()

    pass
