# -*- coding: utf-8 -*-
""" Create a plot from an sme file
"""
from os.path import dirname, join

from pysme import sme as SME
from pysme.gui import plot_plotly

if __name__ == "__main__":

    # Define the location of all your files
    # this will put everything into the example dir
    fname = join(
        dirname(__file__), "results", "GJ1214_monh_teff_logg_vmic_vmac_vsini_bkp.sme"
    )
    plot_file = join(
        dirname(__file__), "results", "GJ1214_monh_teff_logg_vmic_vmac_vsini_bkp.html"
    )

    sme = SME.SME_Structure.load(fname)
    # Plot results
    fig = plot_plotly.FinalPlot(sme)
    fig.save(filename=plot_file)
