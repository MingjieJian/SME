# -*- coding: utf-8 -*-
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    fitparameters = ["teff", "logg", "monh"]
    # snrs = [50, 100, 150, 200]
    # wranges = [1, 2, 3, 4]
    snrs = [100]
    wranges = [1]
    scatter = np.zeros((len(snrs), len(wranges), len(fitparameters)))
    u_mean = np.zeros((len(snrs), len(wranges), len(fitparameters)))
    u_mean_sme = np.zeros((len(snrs), len(wranges), len(fitparameters)))

    for i, snr in enumerate(snrs):
        for j, wrange in enumerate(wranges):
            # Load the data
            fname = join(dirname(__file__), f"mc_uncs_snr{snr}.0_w{wrange}.npz")
            data = np.load(fname)

            values = data["values"]
            values_input = data["values_input"]
            values_true = data["values_true"]
            uncs = data["uncs"]
            uncs_sme = data["uncs_sme"]
            # fitparameters = data["fitparameters"]

            # Remove points that are still empty because the execution stopped
            mask = np.all(values != 0, axis=0)
            values = values[:, mask]
            values_input = values_input[:, mask]
            uncs = uncs[:, mask]
            uncs_sme = uncs_sme[:, mask]

            print(np.count_nonzero(mask))

            # Plot the distribution for each parameter

            for k, fp in enumerate(fitparameters):
                # MAD adjusted to match the std
                scatter[i, j, k] = (
                    np.nanmedian(np.abs(np.nanmedian(values[k]) - values[k])) * 1.4826
                )
                # Median of the fit uncertainties
                u_mean[i, j, k] = np.nanmedian(uncs[k])
                u_mean_sme[i, j, k] = np.nanmedian(uncs_sme[k])

                vmin = np.nanmin(values[k])
                vmax = np.nanmax(values[k])
                v, _, _ = plt.hist(values[k], bins="auto", range=(vmin, vmax))
                plt.vlines(values_true[k], 0, np.nanmax(v))
                plt.xlabel(fp)
                plt.ylabel("#")
                plt.savefig(join(dirname(__file__), f"mc_uncs_{fp}.png"))
                plt.show()
                plt.clf()

            # factor = scatter / u_mean
            # factor /= np.sum(factor)
            # factor = np.round(factor, 2)

    pass
