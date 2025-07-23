#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from os.path import dirname, exists, expanduser, join
from shutil import copy

from setuptools import setup

# 设置环境变量，标记为安装模式
os.environ['SETUPTOOLS_INSTALL_MODE'] = '1'

import versioneer

# Create folder structure for config files
print("Set up the configuration files for PySME")
directory = expanduser("~/.sme/")
conf = join(directory, "config.json")
atmo = join(directory, "atmospheres")
nlte = join(directory, "nlte_grids")
cache_atmo = join(atmo, "cache")
cache_nlte = join(nlte, "cache")

os.makedirs(directory, exist_ok=True)
os.makedirs(atmo, exist_ok=True)
os.makedirs(nlte, exist_ok=True)
os.makedirs(cache_atmo, exist_ok=True)
os.makedirs(cache_nlte, exist_ok=True)

# Create config file if it does not exist
if not exists(conf):
    # Hardcode default settings?
    defaults = {
        "data.file_server": "http://sme.astro.uu.se/atmos",
        "data.atmospheres": "~/.sme/atmospheres",
        "data.nlte_grids": "~/.sme/nlte_grids",
        "data.cache.atmospheres": "~/.sme/atmospheres/cache",
        "data.cache.nlte_grids": "~/.sme/nlte_grids/cache",
        "data.pointers.atmospheres": "datafiles_atmospheres.json",
        "data.pointers.nlte_grids": "datafiles_nlte.json",
    }

    # Save file to disk
    with open(conf, "w") as f:
        json.dump(defaults, f)
else:
    print("Configuration file already exists")

# Copy datafile pointers, for use in the GUI
print("Copy references to datafiles to config directory")
copy(
    join(dirname(__file__), "src/pysme/datafiles_atmospheres.json"),
    expanduser("~/.sme/datafiles_atmospheres.json"),
)
copy(
    join(dirname(__file__), "src/pysme/datafiles_nlte.json"),
    expanduser("~/.sme/datafiles_nlte.json"),
)

# TODO: Have smelib compiled before distribution
with open(join(dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

# Setup package
setup(
    name="pysme-astro",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Spectroscopy Made Easy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mingjie Jian, Ansgar Wehrhahn, Jeff A. Valenti",
    author_email="mingjie.jian@astro.su.se, valenti@stsci.edu",
    packages=[
        "pysme",
        "pysme.gui",
        "pysme.atmosphere",
        "pysme.linelist",
        "pysme.smelib",
    ],
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "scipy",
        "astropy",
        "pandas",
        "wget",
        "tqdm",
        "pqdm",
        "colorlog",
        "emcee",
        "pybtex",
        "flex-format",
        "matplotlib"
    ],
    url="https://github.com/MingjieJian/SME/",
    project_urls={
        "Bug Tracker": "https://github.com/MingjieJian/SME/issues",
        "Documentation": "https://pysme-astro.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/MingjieJian/SME/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
