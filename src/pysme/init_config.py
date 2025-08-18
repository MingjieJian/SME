import json, os
from os.path import dirname, exists, expanduser, join
from shutil import copy

def ensure_user_config():
    # Create folder structure for config files
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
        print('Create config file')
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
    # else:
    #     print("Configuration file already exists")

    # Copy datafile pointers, for use in the GUI
    if not exists(expanduser("~/.sme/datafiles_atmospheres.json")):
        print("Copy references to datafiles for atmospheres to config directory")
        copy(
            join(dirname(__file__), "datafiles_atmospheres.json"),
            expanduser("~/.sme/datafiles_atmospheres.json"),
        )
    if not exists(expanduser("~/.sme/datafiles_nlte.json")):
        print("Copy references to datafiles for nlte to config directory")
        copy(
            join(dirname(__file__), "datafiles_nlte.json"),
            expanduser("~/.sme/datafiles_nlte.json"),
    )