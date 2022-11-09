# -*- coding: utf-8 -*-
import re
from os.path import dirname, join

import pybtex.database

from pysme.abund import elements_dict
from pysme.atmosphere.savfile import SavFile
from pysme.large_file_storage import setup_lfs
from pysme.nlte import Grid
from pysme.sme import SME_Structure

cwd = dirname(__file__)

sme = SME_Structure.load(join(cwd, "results/AU_Mic_inp.sme"))
_, lfs, lfs_nlte = setup_lfs()

# linelist
def linelist(sme):
    cite = sme.linelist.citation_info
    bibdata = pybtex.database.parse_string(cite, bib_format="bibtex")

    ref = sme.linelist.reference
    pattern = r"\s\d+ (\w+:)?([\w+]+)[\s']"
    pattern = re.compile(pattern)
    idiscard = 45  # long format
    species = set(sme.linelist.species)

    # Sort species by charge number
    # And put molecules at the end
    def sorter(key):
        elem, ion = key.split()
        try:
            return elements_dict[elem] * 100 + int(ion)
        except KeyError:
            return 100 ** 2 + ord(elem[0]) + int(ion)

    species = sorted(species, key=sorter)

    references = {}

    for spec in species:
        idx = sme.linelist.species == spec
        # Discard the initial part of the line
        lines = [line[idiscard:] for line in ref[idx]]
        lines = "".join(lines)
        r = [match.group(2) for match in re.finditer(pattern, lines)]
        r = set(r)
        if "LWb" in r:
            r.add("LWb2")
            r.remove("LWb")
        if "LGb" in r:
            r.add("LGb2")
            r.remove("LGb")

        # r = [bibdata.entries[r2] for r2 in r]
        references[spec] = r

    # Make it into a latex table
    # Species & Reference \\
    # H 1     & \citealt{CDROM18,...} \\
    table = [r"\toprule", r"Species & Reference \\", r"\midrule"]
    for spec in species:
        cite = ",".join(references[spec])
        line = r"{} & \citealt{{{}}} \\".format(spec, cite)
        table += [line]
    table += [r"\bottomrule"]
    table = "\n".join(table)
    print(table)

    cite = sme.linelist.citation_info
    while "\\\\" in cite:
        cite = cite.replace("\\\\", "\\")
    with open("debug_citation_info.bib", "w") as f:
        f.write(cite)

    return table, cite


# Atmospere
def atmosphere(sme):
    grid = lfs.get(sme.atmo.source)
    grid = SavFile(grid)
    grid.citation_info


# NLTE
elems = sme.nlte.elements
elems = sorted(elems, key=lambda k: elements_dict[k])
cite = {}
for elem in elems:
    grid = Grid(sme, elem, lfs_nlte)
    cite[elem] = [grid.citation_info]


cite = sme.citation()
print(cite)
