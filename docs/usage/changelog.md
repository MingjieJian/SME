# Changelog

This page stores the change log for pysme since May 2024.

## In-development

## In github-repo

- (synthesize) synthesize function now support calculating line central-depth and range, and can use it to select only the relevant lines in synthesize (and thus in solve). 

## v0.4.187

- Latest NLTE grids available.

## v0.4.184

- (vald) add save and merge function to ValdFile.
    - Coupling information ('LS', 'JK' etc) are missed during reading. Now added back.
    - There is no `vmic` column in VALD short extract_all mode, but pysme have. This leads to I/O fail for this kind of line list. Fixed.

## v0.4.183

- (mask) revert mask function back. The modification in v0.4.180 caused a bug on mask and it is fixed now.
- (synthesize) fix the vstep issue when synthesizing sparce spectrum.
- (nlte) add ResetDepartureCoefficients function to ensure correct NLTE calculation
- (solve) use 'vrad' instead of 'v_rad' for the radial velocity fitting.
- (solve) add dynamic parameter function; sme parameter can changes according to other parameters while not being included in the fitting.
- New readthedocs theme (alabaster -> sphinx_book_theme).

## v0.4.180

- ~~fix mask bug. The continuum fitting function is now available.~~ (see v0.4.183)

## v0.4.179

- Add line depth result to sme_structure.
- Add line range result to sme_structure.
- Support python 3.12.
- Support new VALD3 line format.