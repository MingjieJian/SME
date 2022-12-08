# -*- coding: utf-8 -*-
import json
from os.path import dirname, join

import matplotlib.pyplot as plt

from pysme.sme import SME_Structure
from pysme.solve import SME_Solver

targets = [
    "Eps_Eri",
    "HN_Peg",
    "55_Cnc",
    # "AU_Mic",
    "HD_102195",
    "HD_130322",
    "HD_179949",
    "HD_189733",
    "WASP-18",
]

cwd = dirname(__file__)

for target in targets:
    fname = join(cwd, f"results/{target}_monh_teff_logg_vmic_vmac_vsini_fix6.sme")
    jname = join(cwd, f"json/{target.lower()}.json")
    try:
        sme = SME_Structure.load(fname)
    except FileNotFoundError as ex:
        print(f"WARNING: {ex}")
        continue

    # resid = sme.fitresults.residuals
    # deriv = sme.fitresults.derivative
    # uncs = SME_Solver.estimate_uncertainties(resid, deriv)
    # sme.fitresults.uncertainties = uncs

    with open(jname, "r") as f:
        data = json.load(f)

    for param in ["teff", "logg", "monh", "vmic", "vmac", "vsini"]:
        idx = [i for i, p in enumerate(sme.fitresults.parameters) if p == param][0]
        data[param] = sme.fitresults.values[idx]
        data[f"unc_{param}"] = sme.fitresults.fit_uncertainties[idx]
        data[f"unc2_{param}"] = sme.fitresults.uncertainties[idx]
        # data[f"unc_{param}"] = sme.fitresults.fit_uncertainties[idx]

    with open(jname, "w") as f:
        json.dump(data, f)
