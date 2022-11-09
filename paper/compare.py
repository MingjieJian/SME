# -*- coding: utf-8 -*-
from os.path import dirname, join

import numpy as np

from pysme.gui import plot_plotly
from pysme.iliffe_vector import Iliffe_vector
from pysme.sme import SME_Structure
from pysme.solve import SME_Solver, solve

cwd = dirname(__file__)

# fname = join(cwd, "results/55_Cnc_monh_teff_logg_vmic_vmac_vsini.sme")
fname = join(cwd, "55_Cnc_tanja_out.sme")
sme = SME_Structure.load(fname)
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
