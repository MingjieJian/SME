# Quickstart

## SME Structure

The first step in each SME project is to create an SME structure

```py    
from pysme.sme import SME_Structure
```

This can be done in done in a few different ways:
- load an existing SME save file (from Python or IDL): `sme = SME_Structure.load("sme.inp")`
- load an .ech file spectrum: `sme = SME_Structure.load("obs.ech")`
- assign values manually: `sme = SME_Structure()`

Either way one has to make sure that a few essential properties are set in the object, those are:
    * Stellar parameters (teff, logg, monh, abund)
        >>> from pysme.abund import Abund
        >>> sme.teff, sme.logg, sme.monh = 5700, 4.4, -0.1
        >>> sme.abund = Abund.solar()
    * LineList (linelist), e.g. from VALD
        >>> from pysme.linelist.vald import ValdFile
        >>> vald = ValdFile("linelist.lin")
        >>> sme.linelist = vald
    * Atmosphere (atmo), the file has to be in PySME/src/sme/atmospheres
        >>> # SME comes with a few model atmospheres see Atmosphere section
        >>> sme.atmo.source = "marcs2012p_t1.0.sav"
        >>> sme.atmo.method = "grid"
        >>> sme.atmo.geom = "PP"

If no wavelength grid (sme.wave) is set, one has to set the wavelength range:
    * Wavelength range(s) in Ångstrom
        >>> sme.wran = [[4500, 4600], [5200, 5400]]

Furthermore for fitting to an observation an observation is required:
    * Wavelength wave
        >>> # The observation may be split into segments (orders etc)
        >>> # Then Wavelength is a list of arrays [segment1, segment2, ...]
        >>> # The same applies to spec, uncs, and mask
        >>> # The wavelength is always given in Angstrom
        >>> sme.wave = Wavelength
    * Spectrum spec
        >>> sme.spec = Spectrum
    * Uncertainties uncs
        >>> sme.uncs = Uncertainties
    * Mask mask
        >>> # The mask values are: 0: bad pixel, 1: line pixel, 2: continuum pixel, 4: vrad pixel
        >>> # The masks are additive, i.e., you can set mask value to 5 for line and vrad pixel.
        >>> # Note that the dtype of sme.mask must be int.
        >>> sme.mask = np.ones(len(Spectrum), dtype=int)
    * radial velocity and continuum flags
        >>> # possible values are: "each", "whole", "fix", "none"
        >>> # "each": Each segment is fitted individually
        >>> # "whole": All segments are fit with the same radial velocity
        >>> # "fix": use the set radial velocity
        >>> # "none": Apply no radial velocity offset
        >>> sme.vrad_flag = "whole"
        >>> # possible values are: "constant", "linear", "fix", "none"
        >>> # "constant": Scale the synthetic spectrum by a constant
        >>> # "linear": Scale the synthetic spectrum by a linear polynomial
        >>> # "fix": Use the set continnuum scale
        >>> # "none": apply no continuum correction
        >>> sme.cscale_flag = "linear"
        >>> # possible values are: "whole", "mask"
        >>> # "whole": use MCMC to match the synthetic to the observed spectrum
        >>> # "mask": use the continuum mask points to fit the continuum
        >>> sme.cscale_type = "mask"

Optionally the following can be set:
    * NLTE nlte for non local thermal equilibrium calculations
        >>> # SME also comes with a few NLTE grids, see NLTE section
        >>> # The NLTE grid is atmosphere model dependant!
        >>> sme.nlte.set_nlte("Ca", "marcs2012p_t1.0_Ca.grd")

Once the SME structure is prepared, SME can be run in one of its two modes:
    1. Synthesize a spectrum
        >>> from sme.solve import synthesize_spectrum
        >>> sme = synthesize_spectrum(sme)
    2. Finding the best fit (least squares) solution
        >>> from sme.solve import solve
        >>> # for more details on the fitparameter option, see fitparameters
        >>> fitparameters = ["teff", "logg", "monh", "abund Mg"]
        >>> sme = solve(sme, fitparameters)

The results will be contained in the output sme structure. These can for example be plotted using the gui module.
    >>> from gui import plot_plotly
    >>> fig = plot_plotly.FinalPlot(sme)
    >>> fig.save(filename="sme.html")

.. raw:: html
    :file: ../_static/sun.html

or saved with
    >>> sme.save("out.npy")

