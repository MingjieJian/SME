# -*- coding: utf-8 -*-
import json
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy as np

from pysme.sme import SME_Structure

if __name__ == "__main__":
    results_dir = join(dirname(__file__), "results")
    targets = [
        "Eps_Eri_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        "HN_Peg_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        "HD_102195_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        "HD_130322_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        "HD_179949_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        "HD_189733_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        "55_Cnc_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        "WASP-18_monh_teff_logg_vmic_vmac_vsini_fix4.sme",
        # "AU_Mic_monh_teff_logg_vmic_vmac_vsini_fix.sme",
    ]
    names = np.array(
        [
            "Eps Eri",
            "HN Peg",
            "HD 102195",
            "HD 130322",
            "HD 179949",
            "HD 189733",
            "55 Cnc",
            "WASP-18",
            # "AU Mic",
        ]
    )

    data = []
    for i, target in enumerate(targets):
        fname = join(results_dir, target)
        sme = SME_Structure.load(fname)
        data += [sme]

    seg = 26

    nrows = len(targets)
    fig, ax = plt.subplots(figsize=(20, 16))
    for i, target in enumerate(targets):
        if i == 0:
            ax = ax1 = plt.subplot(nrows, 1, i + 1)
        else:
            ax = plt.subplot(nrows, 1, i + 1, sharex=ax1)
        wave = data[i].wave[seg][5000:]
        spec = data[i].spec[seg][5000:]
        synth = data[i].synth[seg][5000:]

        plt.plot(wave, spec)
        plt.plot(wave, synth)
        # plt.ylabel(names[i])
        plt.text(0.05, 0.3, names[i], transform=ax.transAxes, fontsize="xx-large")
        plt.yticks([])
        plt.xticks(fontsize="x-large")

        if i == nrows - 1:
            plt.xlabel("Wavelength [Å]", fontsize="xx-large")
        # else:
        #     plt.xticks([])

    plt.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=0)
    plt.savefig(join(dirname(__file__), "images/plot_all.pdf"))
    # plt.show()

    pass
