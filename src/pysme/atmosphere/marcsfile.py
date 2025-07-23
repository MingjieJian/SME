import re
import sys
import logging
import numpy as np
import pandas as pd

from ..abund import Abund, elements
from .atmosphere import Atmosphere

logger = logging.getLogger(__name__)


def readmarcsfile(marcsfilename):
    marcsfile = open(marcsfilename, "r")
    name = marcsfile.readline().strip()  # model name on first line

    teffraw = marcsfile.readline().strip()
    fluxraw = marcsfile.readline().strip()
    gravraw = marcsfile.readline().strip()
    vturbraw = marcsfile.readline().strip()
    massraw = marcsfile.readline().strip()
    metalraw = marcsfile.readline().strip()
    radiusraw = marcsfile.readline().strip()
    lumraw = marcsfile.readline().strip()
    convraw = marcsfile.readline().strip()
    xyzraw = marcsfile.readline().strip()

    if len(teffraw) == 0 or len(fluxraw) == 0 or len(gravraw) == 0 or len(vturbraw) == 0 or len(massraw) == 0 or\
            len(metalraw) == 0 or len(radiusraw) == 0 or len(lumraw) == 0 or len(convraw) == 0 or len(xyzraw) == 0:
        logger.error("unable to read global headers from file: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)

    teff = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+teff", teffraw, flags=re.IGNORECASE)
    if m:
        teff = float(m.group(1))
    flux = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+flux", fluxraw, flags=re.IGNORECASE)
    if m:
        flux = float(m.group(1))
    grav = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+surface gravity", gravraw, flags=re.IGNORECASE)
    if m:
        grav = float(m.group(1))
    vturb = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+microturbulence", vturbraw, flags=re.IGNORECASE)
    if m:
        vturb = float(m.group(1))
    mass = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+n?o?\s*mass", massraw, flags=re.IGNORECASE)
    if m:
        mass = float(m.group(1))
    monh = None
    alpha = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+([+-]?\d+\.?\d*e?[+-]?\d*|\?+)\s+metallicity", metalraw,
                 flags=re.IGNORECASE)
    if m:
        monh = float(m.group(1))
        alpha = 0.0 if '?' in m.group(2) else float(m.group(2))
    radius = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)", radiusraw, flags=re.IGNORECASE)
    if m:
        radius = float(m.group(1))
    lum = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)", lumraw, flags=re.IGNORECASE)
    if m:
        lum = float(m.group(1))
    conv_alpha = None
    conv_y = None
    conv_nu = None
    conv_beta = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+([+-]?\d+\.?\d*e?[+-]?\d*)\s+([+-]?\d+\.?\d*e?[+-]?\d*)\s+([+-]?\d+\.?\d*e?[+-]?\d*)", convraw, flags=re.IGNORECASE)
    if m:
        conv_alpha = float(m.group(1))
        conv_y = float(m.group(2))
        conv_nu = float(m.group(3))
        conv_beta = float(m.group(4))
    abund_x = None
    abund_y = None
    abund_z = None
    c12c13 = None
    m = re.match(r"\s*([+-]?\d+\.?\d*e?[+-]?\d*)\s+([+-]?\d+\.?\d*e?[+-]?\d*)\s+([+-]?\d+\.?\d*e?[+-]?\d*) are X, Y and Z, 12C/13C=([+-]?\d+\.?\d*e?[+-]?\d*|\?+)", xyzraw, flags=re.IGNORECASE)
    if m:
        abund_x = float(m.group(1))
        abund_y = float(m.group(2))
        abund_z = float(m.group(3))
        c12c13 = None if '?' in m.group(4) else float(m.group(4))

    headererror = False
    if teff is None:
        headererror = True
        logger.error("unable to determine teff in marcs model: " + marcsfilename)
    if flux is None:
        headererror = True
        logger.error("unable to determine flux in marcs model: " + marcsfilename)
    if grav is None:
        headererror = True
        logger.error("unable to determine logg in marcs model: " + marcsfilename)
    if vturb is None:
        headererror = True
        logger.error("unable to determine vturb in marcs model: " + marcsfilename)
    if mass is None:
        headererror = True
        logger.error("unable to determine mass in marcs model: " + marcsfilename)
    if monh is None:
        headererror = True
        logger.error("unable to determine metallicity in marcs model: " + marcsfilename)
    if radius is None:
        headererror = True
        logger.error("unable to determine radius in marcs model: " + marcsfilename)
    if lum is None:
        headererror = True
        logger.error("unable to determine luminosity in marcs model: " + marcsfilename)
    if headererror:
        marcsfile.close()
        sys.exit(1)

    geom = 'PP' if abs(radius - 1.0) < 0.1 else 'SPH'

    if re.search(r"\s*Logarithmic chemical number abundances", marcsfile.readline(), flags=re.IGNORECASE):
        abundtxtraw = [marcsfile.readline().strip() for _ in range(10)]
        abundtxtarray = " ".join(abundtxtraw).split()
        for idx in range(len(abundtxtarray),len(elements)):
            abundtxtarray.append("-99")
        abund = pd.DataFrame([abundtxtarray], columns=elements).astype(float)
    else:
        logger.error("unable to read abundance info from file: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)

    m = re.search(r"\s*(\d+)\s+Number of depth points", marcsfile.readline(), flags=re.IGNORECASE)
    if m:
        ndepth = int(m.group(1))
    else:
        logger.error("unable to determine number of depth points in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)

    if not re.search(r"Model structure", marcsfile.readline(), flags=re.IGNORECASE):
        logger.error("Not finding model structure values in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)

    modelarray_1 = [marcsfile.readline().strip().split() for _ in range(ndepth+1)]
    if (len(modelarray_1) != (ndepth+1)) or modelarray_1[0][0] != 'k' or modelarray_1[ndepth][0] != str(ndepth):
        logger.error("Model structure found not expected in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)
    modelpd_1 = pd.DataFrame(modelarray_1[1:], columns=modelarray_1[0]).astype(float)
    modelarray_2 = [marcsfile.readline().strip().split() for _ in range(ndepth+1)]
    if (len(modelarray_2) != (ndepth+1)) or modelarray_2[0][0] != 'k' or modelarray_2[ndepth][0] != str(ndepth):
        logger.error("Model structure found (2. part) not expected in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)
    modelpd_2 = pd.DataFrame(modelarray_2[1:], columns=modelarray_2[0]).astype(float)
    modelstruct = pd.concat([modelpd_1.drop(columns='k'), modelpd_2.drop(columns='k')], axis=1, join="inner")

    if not re.search(r"Assorted logarithmic partial pressures", marcsfile.readline(), flags=re.IGNORECASE):
        logger.error("Not finding partial pressures in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)

    pparray_1 = [re.sub(r"H I","H1", marcsfile.readline()).strip().split() for _ in range(ndepth+1)]
    if (len(pparray_1) != (ndepth+1)) or pparray_1[0][0] != 'k' or pparray_1[ndepth][0] != str(ndepth):
        logger.error("Partial pressures found not expected in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)
    pparray_1 = pd.DataFrame(pparray_1[1:], columns=pparray_1[0]).astype(float)
    pparray_2 = [marcsfile.readline().strip().split() for _ in range(ndepth+1)]
    if (len(pparray_2) != (ndepth+1)) or pparray_2[0][0] != 'k' or pparray_2[ndepth][0] != str(ndepth):
        logger.error("Partial pressures found (2. part) not expected in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)
    pparray_2 = pd.DataFrame(pparray_2[1:], columns=pparray_2[0]).astype(float)
    pparray_3 = [marcsfile.readline().strip().split() for _ in range(ndepth+1)]
    if (len(pparray_3) != (ndepth+1)) or pparray_3[0][0] != 'k' or pparray_3[ndepth][0] != str(ndepth):
        logger.error("Partial pressures found (3. part) not expected in marcs model: " + marcsfilename)
        marcsfile.close()
        sys.exit(1)
    pparray_3 = pd.DataFrame(pparray_3[1:], columns=pparray_3[0]).astype(float)
    partialpressures = pd.concat([pparray_1.drop(columns='k'), pparray_2.drop(columns='k'), pparray_3.drop(columns='k')], axis=1, join="inner")

    marcsfile.close()
    return {
        "name": name,
        "teff": teff,
        "flux": flux,
        "grav": grav,
        "vturb": vturb,
        "mass": mass,
        "monh": monh,
        "alpha": alpha,
        "radius": radius,
        "lumin": lum,
        "geom": geom,
        "conv_alpha": conv_alpha,
        "conv_y": conv_y,
        "conv_nu": conv_nu,
        "conv_beta": conv_beta,
        "abund_x": abund_x,
        "abund_y": abund_y,
        "abund_z": abund_z,
        "c12c13": c12c13,
        "abund_inclmonh": abund,
        "ndepth": ndepth,
        "modelstruct": modelstruct,
        "partialpressures": partialpressures
    }


class MarcsAtmosphere(Atmosphere):
    '''
    Read marcs atmosphere single files
    '''
    def __init__(self, filename, calcRHOX=False):
        super().__init__()
        data = readmarcsfile(filename)
        self.source = filename
        self.method = 'embedded'
        self.citation_info = 'https://ui.adsabs.harvard.edu/abs/2008A&A...486..951G'
        self.opflag = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0]  # MARCS model standard
        self.wlstd = 5000.0  # MARCS model standard
        self.teff = data["teff"]
        self.logg = np.log10(data["grav"])
        self.geom = data["geom"]
        if self.geom.upper() == 'SPH':
            self.radius = data["radius"]
        self.depth = 'RHOX' if self.geom.upper() == 'SPH' else 'TAU'  # spherical models should depth calculate using RHOX
        self.interp = 'TAU'  # not sure this is needed for embedded models
        self.vturb = data["vturb"]

        self.abund = Abund(monh=data["monh"], pattern=data["abund_inclmonh"].to_numpy()[0]-data["monh"], type="H=12")

        mdl: pd.DataFrame = data["modelstruct"]

        kb_cgs = 1.380622e-16  # Boltzmann's constant in cgs units (g cm^2 s^-2 K^-1)
        self.temp = mdl['T'].to_numpy()
        Pe = mdl['Pe'].to_numpy()
        Pg = mdl['Pg'].to_numpy()
        self.xne = np.true_divide(Pe,self.temp)/kb_cgs
        self.xna = np.true_divide((Pg-Pe),self.temp)/kb_cgs
        self.rho = mdl['Density'].to_numpy()
        depth = mdl['Depth'].to_numpy()
        self.height = 0.0 - depth  # only really necessary for spherical models
        self.tau = 10 ** mdl['lgTau5'].to_numpy()

        # option to calculate rhox as some old model files have errors
        if calcRHOX:
            self.rhox = np.zeros(len(self.rho))
            Prad = mdl['Prad'].to_numpy()
            Pturb = mdl['Pturb'].to_numpy()
            ptotzero = Pg[0] + Prad[0] + (Pturb[0] + Pturb[1])/2  # does not include Pe
            if self.geom.upper() == 'SPH':
                self.rhox[0] = ptotzero / (data["grav"]*(self.radius/(self.radius+self.height[0]))**2)  # not sure how to translate rr[0]
                for idx in range(1,len(self.rho)):
                    rr = self.radius + self.height[idx]
                    rrm1 = self.radius + self.height[idx-1]
                    self.rhox[idx] = self.rhox[idx-1]*(rrm1/rr)**2 + (self.rho[idx-1]+self.rho[idx])/6.0 * (rrm1*(rrm1/rr)**2-rr)
            else:
                self.rhox[0] = ptotzero / data["grav"]
                for idx in range(1,len(self.rho)):
                    self.rhox[idx] = self.rhox[idx-1] + (depth[idx]-depth[idx-1]) * (self.rho[idx-1]+self.rho[idx]) / 2.0
        else:
            self.rhox = mdl['RHOX'].to_numpy()