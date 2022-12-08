# -*- coding: utf-8 -*-
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy as np

from pysme.continuum_and_radial_velocity import ContinuumNormalizationMatch
from pysme.gui import plot_plotly
from pysme.iliffe_vector import Iliffe_vector
from pysme.sme import SME_Structure
from pysme.solve import SME_Solver, solve

cwd = dirname(__file__)

# fname = join(cwd, "results/55_Cnc_monh_teff_logg_vmic_vmac_vsini_fix.sme")
# fname = join(cwd, "results/WASP-18_monh_teff_logg_vmic_vmac_vsini_fix.sme")
# sme_me = SME_Structure.load(fname)

# fname = join(cwd, "results/55_Cnc_monh_teff_logg_vmic_vmac_vsini_fix6.sme")
# fname = join(cwd, "results/WASP-18_monh_teff_logg_vmic_vmac_vsini_fix4.sme")
# sme_new = SME_Structure.load(fname)

fname = join(cwd, "55_Cnc_tanja_out.sme")
sme = SME_Structure.load(fname)

# sme_me.cscale_flag = 1
# i = 8
# for i in range(6, 30):
#     module = ContinuumNormalizationMatch()
#     module.top_factor = 1_000
#     cscale = module(
#         sme_me,
#         sme_me.wave[i],
#         sme_me.synth[i],
#         i,
#     )
#     x = sme_me.wave[i] - sme_me.wave[i, 0]
#     cont = np.polyval(cscale[0], x)

#     plt.plot(sme_me.wave[i].ravel(), sme_me.spec[i].ravel(), label="observation")
#     plt.plot(sme_me.wave[i].ravel(), sme_me.synth[i].ravel(), label="PySME - Ansgar")
#     plt.plot(
#         sme_me.wave[i].ravel(),
#         sme_me.synth[i] * cont,
#         label=f"PySME - Ansgar - {module.top_factor}",
#     )

#     plt.plot(
#         sme_new.wave[i].ravel(), sme_new.synth[i].ravel(), label="PySME - Ansgar 2"
#     )

#     # plt.plot(sme.wave.ravel(), sme.synth.ravel(), label="PySME - Tanja")
#     plt.legend()
#     # plt.xlim(5671, 5683)
#     # plt.xlim(6430, 6444)
#     plt.title(i)
#     plt.show()

# puncs = SME_Solver.estimate_uncertainties(
#     sme.fitresults.residuals, sme.fitresults.derivative
# )


segments = np.where([sme.synth.shape[1] != 0])[1]

# fname = join(cwd, "55_Cnc_job1_7_NLTE_param_RV_cormask.inp")
fname = join(cwd, "55_Cnc_job1_all_NLTE_param_RV.out")
idl = SME_Structure.load(fname)

# idl = solve(idl, ["monh", "logg", "teff"])
# fname = join(cwd, "55_Cnc_tanja_out.sme")
# idl.save(fname)

orig = np.interp(
    idl.wave.ravel(), sme.wave[segments].ravel(), sme.synth[segments].ravel()
)
orig = Iliffe_vector(orig, offsets=idl.wave.offsets)

fig = plot_plotly.FinalPlot(
    idl, orig=orig, labels={"synth": "IDL SME", "orig": "PySME"}
)
fig.save(filename=join(cwd, "Cnc55_tanja_new.html"))
exit()


mask_orig = np.copy(sme.mask_good[segments].ravel())
sme = sme.import_mask(idl)

mask = sme.mask_good[segments]
unc = sme.uncs[segments]
unc = unc[mask]
unc = unc.ravel()

resid = sme.fitresults.residuals[mask.ravel()[mask_orig]]
deriv = sme.fitresults.derivative[mask.ravel()[mask_orig]]
solver = SME_Solver()
solver.parameter_names = sme.fitresults.parameters
uncs = solver.estimate_uncertainties(unc, resid, deriv)


orig = np.interp(
    idl.wave.ravel(), sme.wave[segments].ravel(), sme.spec[segments].ravel()
)
orig = Iliffe_vector(orig, offsets=idl.wave.offsets)

synth = idl.synth.copy()

idl.vrad_limit = 200
# idl.mask[idl.uncs == 0] = 0
# idl.cscale_type = "match"
# idl.cscale_flag = "linear"
# idl.linelist = sme.linelist
# idl.linelist.medium = "air"

# idl.nlte.set_nlte("Al", "nlte_Al_ama51_pysme.grd")
# idl.nlte.set_nlte("Ba", "nlte_Ba_ama51_pysme.grd")
# idl.nlte.set_nlte("Ca", "nlte_Ca_ama51_pysme.grd")
# idl.nlte.set_nlte("C", "nlte_C_ama51_pysme.grd")
# idl.nlte.set_nlte("H", "nlte_H_ama51_pysme.grd")
# idl.nlte.set_nlte("K", "nlte_K_ama51_pysme.grd")
# idl.nlte.set_nlte("Li", "nlte_Li_ama51_pysme.grd")
# idl.nlte.set_nlte("Mg", "nlte_Mg_ama51_pysme.grd")
# idl.nlte.set_nlte("Mn", "nlte_Mn_ama51_pysme.grd")
# idl.nlte.set_nlte("Na", "nlte_Na_ama51_pysme.grd")
# idl.nlte.set_nlte("N", "nlte_Na_ama51_pysme.grd")
# idl.nlte.set_nlte("O", "nlte_O_ama51_pysme.grd")
# idl.nlte.set_nlte("Si", "nlte_Si_ama51_pysme.grd")
# idl.nlte.set_nlte("Fe", "marcs2012_Fe2016.grd")

# idl = synthesize_spectrum(idl)
# fp = ["teff", "logg", "monh", "vmic", "vmac", "vsini"]
# idl = solve(idl, fp)
# idl.save(join(cwd, "results/Cnc55_tanja.sme"))

# idl_solved = SME_Structure.load(join(cwd, "results/Cnc55_tanja.sme"))


fig = plot_plotly.FinalPlot(
    idl, orig=orig, labels={"synth": "IDL SME", "orig": "PySME"}
)
fig.save(filename=join(cwd, "Cnc55_tanja.html"))
pass
