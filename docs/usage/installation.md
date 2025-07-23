# Installation

PySME can be installed through PyPI (recommended) or from github directly.

## Prerequisites:
- libgfortran5 (e.g., from [here](https://pkgs.org/download/libgfortran5))
- gcc
- autoconf, automake, libtool
- You can install them by `sudo apt install autoconf automake libtool gcc` (or use `brew` for Mac).

## (optional) set up virtual environment
- download the environment.yml from [here](https://github.com/MingjieJian/SME.git).
- cd to the download location
- `conda env create -f environment.yml`
- `source activate pysme`

## Install 
-
- For the "stable" version (recommended):
    - `pip install pysme-astro`

```{warning}
PySME requires the pre-compled C++/Fortran SME library to run. Currently we deliver SME library with Linux and Mac version; for Windows users, we recommend to use WSL and hence the Linux version. 
```

## Running SME
- An simple minimum example is provided in the [examples directory](https://github.com/MingjieJian/SME/tree/master/examples). Make sure to also download the provided input structure.
- You can then run it with: `python minimum.py`

```{admonition} Accessing data files
The atmosphere and nlte data files should be downloaded from the server automatically when used, so network connection is required when using PySME (not only during installation).
These files can also be downloaded manually by:
- Download data files as part of IDL SME from [here](http://www.stsci.edu/~valenti/sme.html).
-  copy them into their respective storage locations in ~/.sme/atmospheres and ~/.sme/nlte_grids
    - atmospheres: everything from SME/atmospheres
- Download the nlte_grids in [zenodo](https://doi.org/10.5281/zenodo.3888393).
```
