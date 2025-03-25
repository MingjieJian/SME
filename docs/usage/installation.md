# Installation

PySME can be installed through PyPI (recommended) or from github directly.

## Prerequisites:
- libgfortran5 (e.g., from https://pkgs.org/download/libgfortran5)
- gcc

## (optional) set up virtual environment
- download the environment.yml from https://github.com/MingjieJian/SME.git
- cd to the download location
- `conda env create -f environment.yml`
- `source activate pysme`

## Install 
- For the "stable" version (recommended):
    - `pip install pysme-astro`
- For the latest version use:
    - `pip install git+https://github.com/MingjieJian/SME.git`

## Accessing data files

The atmosphere and nlte data files should be downloaded from the server automatically when used, so network connection is required when using PySME (not only during installation).
These files can also be downloaded manually:
- Download data files as part of IDL SME from http://www.stsci.edu/~valenti/sme.html
-  copy them into their respective storage locations in ~/.sme/atmospheres and ~/.sme/nlte_grids
    - atmospheres
        - everything from SME/atmospheres
    - nlte_grids
        - \*.grd from SME/NLTE
        - Note that these NLTE grids are not the latest version (listed in the LFS page). 

## Running SME
- An simple minimum example is provided in the examples directory (https://github.com/MingjieJian/SME/tree/master/examples). Make sure to also download the provided input structure.
- You can then run it with: `python minimum.py`
