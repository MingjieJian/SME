# -*- coding: utf-8 -*-
import json
from os.path import dirname, join

import cdspyreadme
import numpy as np
import pandas as pd
from matplotlib.pyplot import table

tablemaker = cdspyreadme.CDSTablesMaker()

if __name__ == "__main__":
    results_dir = join(dirname(__file__), "json")
    targets = [
        "au_mic.json",
        "eps_eri.json",
        "55_cnc.json",
        "hd_102195.json",
        "hd_130322.json",
        "hd_179949.json",
        "hd_189733.json",
        "hn_peg.json",
        "wasp-18.json",
    ]
    names = np.array(
        [
            "AU Mic",
            "Eps Eri",
            "55 Cnc",
            "HD 102195",
            "HD 130322",
            "HD 179949",
            "HD 189733",
            "HN Peg",
            "WASP-18",
        ]
    )
    snr = []
    parameters = ["teff", "logg", "monh", "vmic", "vmac", "vsini"]
    parameters_names = [
        r"$T_{eff}$",
        r"$\log(g)$",
        r"[M/H]",
        r"$v_{mic}$",
        r"$v_{mac}$",
        r"$v \sin(i)$",
    ]
    method = []
    units = ["K", "log(cm/s**2)", "[F/H]", "km/s", "km/s", "km/s"]

    data = []
    for i in range(len(targets)):
        data += [
            [None] * (2 * len(parameters) + 1),
        ]
    # values = {p: np.zeros(len(targets)) for p in parameters}
    # uncertainties = {p: np.zeros(len(targets)) for p in parameters}
    # inf_values = {p: np.zeros(len(targets)) for p in parameters}
    # inf_uncertainties = {p: np.zeros(len(targets)) for p in parameters}

    # Load the data from targets
    for i, target in enumerate(targets):
        fname = join(results_dir, target)
        with open(fname) as f:
            sme = json.load(f)
        # sme = SME_Structure.load(fname)
        data[i][0] = names[i]
        for j, p in enumerate(parameters):
            data[i][j * 2 + 1] = sme[p]
            data[i][j * 2 + 2] = sme[f"unc2_{p}"]

    # Create the column names
    # in the most hacked together way possible
    columns = ["name"] + " ".join([f"{p} sig_{p}" for p in parameters]).split()

    df = pd.DataFrame(data=data, columns=columns)

    cds = tablemaker.addTable(
        data, name="table.csv", description="stellar parameters determined with PySME"
    )
    tablemaker.writeCDSTables()

    # Customize ReadMe output
    tablemaker.title = "catalogue title"
    tablemaker.author = "G.Landais"
    tablemaker.date = 2020
    tablemaker.abstract = "This is my abstract..."
    tablemaker.more_description = "Additional information of the data context."
    tablemaker.putRef("II/246", "2mass catalogue")
    tablemaker.putRef("http://...", "external link")

    with open("README", "w") as fd:
        tablemaker.makeReadMe(out=fd)
