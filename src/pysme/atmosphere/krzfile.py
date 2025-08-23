# -*- coding: utf-8 -*-
import re
from os.path import basename

import numpy as np

from ..abund import Abund
from .atmosphere import Atmosphere


# Atmoic mass from mendeleev package.
atmoic_mass = {
    'H': 1.008, 'He': 4.002602, 'Li': 6.94, 'Be': 9.0121831, 'B': 10.81, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998403163, 'Ne': 20.1797, 'Na': 22.98976928, 'Mg': 24.305, 'Al': 26.9815385, 'Si': 28.085, 'P': 30.973761998, 'S': 32.06, 'Cl': 35.45, 'Ar': 39.948, 'K': 39.0983, 'Ca': 40.078, 'Sc': 44.955908, 'Ti': 47.867, 'V': 50.9415, 'Cr': 51.9961, 'Mn': 54.938044, 'Fe': 55.845, 'Co': 58.933194, 'Ni': 58.6934, 'Cu': 63.546, 'Zn': 65.38, 'Ga': 69.723, 'Ge': 72.63, 'As': 74.921595, 'Se': 78.971, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.4678, 'Sr': 87.62, 'Y': 88.90584, 'Zr': 91.224, 'Nb': 92.90637, 'Mo': 95.95, 'Tc': 97.90721, 'Ru': 101.07, 'Rh': 102.9055, 'Pd': 106.42, 'Ag': 107.8682, 'Cd': 112.414, 'In': 114.818, 'Sn': 118.71, 'Sb': 121.76, 'Te': 127.6, 'I': 126.90447, 'Xe': 131.293, 'Cs': 132.90545196, 'Ba': 137.327, 'La': 138.90547, 'Ce': 140.116, 'Pr': 140.90766, 'Nd': 144.242, 'Pm': 144.91276, 'Sm': 150.36, 'Eu': 151.964, 'Gd': 157.25, 'Tb': 158.92535, 'Dy': 162.5, 'Ho': 164.93033, 'Er': 167.259, 'Tm': 168.93422, 'Yb': 173.045, 'Lu': 174.9668, 'Hf': 178.49, 'Ta': 180.94788, 'W': 183.84, 'Re': 186.207, 'Os': 190.23, 'Ir': 192.217, 'Pt': 195.084, 'Au': 196.966569, 'Hg': 200.592, 'Tl': 204.38, 'Pb': 207.2, 'Bi': 208.9804, 'Po': 209.0, 'At': 210.0, 'Rn': 222.0, 'Fr': 223.0, 'Ra': 226.0, 'Ac': 227.0, 'Th': 232.0377, 'Pa': 231.03588, 'U': 238.02891, 'Np': 237.0, 'Pu': 244.0, 'Am': 243.0, 'Cm': 247.0, 'Bk': 247.0, 'Cf': 251.0, 'Es': 252.0, 'Fm': 257.0, 'Md': 258.0, 'No': 259.0, 'Lr': 262.0, 'Rf': 267.0, 'Db': 268.0, 'Sg': 271.0, 'Bh': 274.0, 'Hs': 269.0, 'Mt': 276.0, 'Ds': 281.0, 'Rg': 281.0, 'Cn': 285.0, 'Nh': 286.0, 'Fl': 289.0, 'Mc': 288.0, 'Lv': 293.0, 'Ts': 294.0, 'Og': 294.0
    }

class KrzFile(Atmosphere):
    """Read .krz atmosphere files"""

    def __init__(self, filename, source=None):
        super().__init__()
        if source is None:
            self.source = basename(filename)
        else:
            self.source = source
        self.method = "embedded"
        self.citation_info = r"""
            @MISC{2017ascl.soft10017K,
                author = {{Kurucz}, Robert L.},
                title = "{ATLAS9: Model atmosphere program with opacity distribution functions}",
                keywords = {Software},
                year = "2017",
                month = "Oct",
                eid = {ascl:1710.017},
                pages = {ascl:1710.017},
                archivePrefix = {ascl},
                eprint = {1710.017},
                adsurl = {https://ui.adsabs.harvard.edu/abs/2017ascl.soft10017K},
                adsnote = {Provided by the SAO/NASA Astrophysics Data System}}
        """
        self.load(filename)

    def load(self, filename):
        """
        Load data from disk

        Parameters
        ----------
        filename : str
            name of the file to load
        """

        kB, mH = 1.380649e-16, 1.6735575e-24
        
        with open(filename, "r") as file:
            header = file.readline() + file.readline()
            opacity = file.readline()
            _ = file.readline()
            # Read in abund
            abun_list = ''
            temp = file.readline()
            abun_list = abun_list + temp[42:].replace('E', '')
            temp = file.readline()
            while 'ABUNDANCE CHANGE' in temp:
                abun_list = abun_list + temp[temp.index('ABUNDANCE CHANGE')+16:]
                temp = file.readline()
            abun = np.array(abun_list.split(), dtype='f').reshape(int(len(abun_list.split())/2), 2)
            # Read the model lines
            temp = temp.split()
            model_lines = []
            for _ in range(int(temp[2])):
                model_lines.append(file.readline().split())
            model_lines = np.array(model_lines, dtype=np.float64)

        try:
            self.monh = float(re.findall(r"\[\s*([+-]?\d+(?:\.\d*)?)\s*\]", header)[0])
        except IndexError:
            self.monh = 0.0

        try:
            self.vturb = float(re.findall(r"VTURB=?\s*(\d)", header, flags=re.I)[0])
        except IndexError:
            self.vturb = 0

        try:
            self.lonh = float(re.findall(r"L/H=?\s*(\d+.?\d*)", header, flags=re.I)[0])
        except IndexError:
            self.lonh = 0

        self.teff = float(re.findall(r"T ?EFF=?\s*(\d+.?\d*)", header, flags=re.I)[0])
        self.logg = float(
            re.findall(r"GRAV(ITY)?=?\s*(\d+.?\d*)", header, flags=re.I)[0][1]
        )

        self.depth = 'RHOX'
        self.geom = "pp"
        self.wlstd = 5000.

        # parse opacity
        opacity_numbers = re.findall(r'OPACITY IFOP\s+([\d\s]+)', opacity, flags=re.I)
        if opacity_numbers:
            self.opflag = np.array([int(k) for k in opacity_numbers[0].split()])
        else:
            # Back to old weird method
            i = opacity.find("-")
            opacity = opacity[:i].split()
            self.opflag = np.array([int(k) for k in opacity])

        # parse abundance
        pattern = abun[:, 1]
        self.abund = Abund(monh=self.monh, pattern=pattern, type="kurucz")

        # parse table
        self.table = model_lines
        self.rhox = self.table[:, 0]
        self.temp = self.table[:, 1]
        self.xne = self.table[:, 3]
        self.P_gas = self.table[:, 2]
        self.xna = self.P_gas / (kB * self.temp)
        atmoic_mu = self.get_mu_from_abund()
        self.rho = self.P_gas * atmoic_mu * mH / (kB * self.temp)

        # This is not used since it is tau_ross instead of tau_5000
        # self.abross = self.table[:, 4]
        # self.tau    = np.zeros_like(self.rhox)
        # self.tau[1:] = np.cumsum(0.5 * (self.abross[1:] + self.abross[:-1]) * np.diff(self.rhox))

    def get_mu_from_abund(self):
        abun = self.abund.pattern
        X, Y = abun['H'], abun['He']
        # 1. 预处理金属
        metals = {el: 10.0**val for el, val in abun.items() if el not in ('H', 'He')}
        R = sum(ri * atmoic_mass[el] for el, ri in metals.items())   # ∑ ri mi
    
        # 2. r = N_He / N_H
        mH, mHe = atmoic_mass['H'], atmoic_mass['He']
        r = (mH/X - mH - R) / (mHe + R)
        if r <= 0:
            raise ValueError("r≤0")
    
        # 3. 归一化取 N_H = 1
        NH  = 1.0
        NHe = r * NH
        Ni = {el: (1+r) * NH * ri for el, ri in metals.items()}
        M_metals = sum(Ni[el] * atmoic_mass[el] for el in Ni)
        N_metals = sum(Ni.values())
    
        mu = (mH + r * mHe + M_metals) / (1.0 + r + N_metals)
    
        return  mu