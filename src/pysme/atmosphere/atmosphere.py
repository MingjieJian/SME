# -*- coding: utf-8 -*-
""" Handles reading and interpolation of atmopshere (grid) data """
import logging

import numpy as np
from flex.extensions.bindata import MultipleDataExtension

from ..abund import Abund
from ..data_structure import (
    Collection,
    CollectionFactory,
    absolute,
    array,
    asfloat,
    asstr,
    lowercase,
    oneof,
    this,
    uppercase,
)

logger = logging.getLogger(__name__)


class AtmosphereError(RuntimeError):
    """Something went wrong with the atmosphere interpolation"""


@CollectionFactory
class Atmosphere(Collection):
    """
    Atmosphere structure
    contains all information to describe the solar atmosphere
    i.e. temperature etc in the different layers
    as well as stellar parameters and abundances
    """

    # fmt: off
    _fields = [
        ("teff", 5770, asfloat, this, "float: effective temperature in Kelvin"),
        ("logg", 4.0, asfloat, this, "float: surface gravity in log10(cgs)"),
        ("abund", Abund.solar(), this, this, "Abund: elemental abundances"),
        ("vturb", 0, absolute, this, "float: turbulence velocity in km/s"),
        ("lonh", 0, asfloat, this, "float: ?"),
        ("source", "marcs2012.sav", this, this, "str: datafile name of this data, or atmosphere grid/file"),
        ("method", "grid", lowercase(oneof("grid", "routine", "embedded")), this,
            "str: whether the data source is a grid or a fixed atmosphere"),
        ("geom", "PP", uppercase(oneof("PP", "SPH", None)), this,
            "str: the geometry of the atmopshere model"),
        ("radius", 0, asfloat, this, "float: radius of the spherical model"),
        ("height", None, array(None, "f8"), this, "array: height of the spherical model"),
        ("opflag", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], array(20, int), this,
            "array of size (20,): opacity flags"),
        ("wlstd", 5000, asfloat, this, "float: wavelength standard deviation"),
        ("depth", None, uppercase(oneof(None, "RHOX", "TAU")), this,
            "str: flag that determines whether to use RHOX or TAU for calculations"),
        ("interp", None, uppercase(oneof(None, "RHOX", "TAU")), this,
            "str: flag that determines whether to use RHOX or TAU for interpolation"),
        ("rhox", None, array(None, "f8"), this,
            "array: mass column density"),
        ("tau", None, array(None, "f8"), this,
            "array: continuum optical depth"),
        ("temp", None, array(None, "f8"), this,
            "array: temperature profile in Kelvin"),
        ("rho", None, array(None, "f8"), this,
            "array: density profile"),
        ("xna", None, array(None, "f8"), this,
            "array: number density of atoms in 1/cm**3"),
        ("xne", None, array(None, "f8"), this,
            "array: number density of electrons in 1/cm**3"),
        ("citation_info", "", asstr, this, "str: citation for this atmosphere"),
    ]
    # fmt: on

    # TODO: pick the right geometry for the grid, based on whether it has height/radius values or not
    def __init__(self, *args, **kwargs):
        monh = kwargs.pop("monh", kwargs.pop("feh", 0))
        abund = kwargs.pop("abund", "empty")
        abund_format = kwargs.pop("abund_format", "sme")
        if "geom" in kwargs.keys() and kwargs["geom"] == "":
            kwargs["geom"] = None
        super().__init__(**kwargs)
        self.abund = Abund(monh=monh, pattern=abund, type=abund_format)

    @property
    def monh(self):
        """float: metallicity"""
        return self.abund.monh

    @monh.setter
    def monh(self, value):
        self.abund.monh = value

    @property
    def names(self):
        return self._names + ["monh"]

    @property
    def dtype(self):
        obj = lambda: None
        obj.names = [n.lower() for n in self.names]
        return obj

    @property
    def ndep(self):
        scale = self.temp
        if scale is not None:
            return scale.shape[0]
        return None

    @ndep.setter
    def ndep(self, value):
        pass

    def _save(self):
        data = {}
        ext2 = self.abund._save()
        header = ext2.header
        data["abund"] = ext2.data
        header["abund_format"] = header["type"]
        del header["type"]

        for name in self._names:
            value = self[name]

            if isinstance(value, np.ndarray):
                data[name] = value
            elif value is None or isinstance(value, Abund):
                pass
            else:
                # if isinstance(value, (np.floating, np.integer, np.str, float, int, str)):
                header[name] = value

        ext = MultipleDataExtension(header, data)

        return ext

    @classmethod
    def _load(cls, ext):
        header = ext.header
        header.update(ext.data)
        obj = cls(**header)
        return obj


@CollectionFactory
class AtmosphereGrid(np.recarray):
    """
    A grid of atmospheres, used for the interpolation
    of model atmospheres. Each entry represents one
    atmosphere model.
    """

    # fmt: off
    _fields = [
        ("source", None, asstr, this, "str: datafile name of this data"),
        ("method", "grid", lowercase(oneof("grid", "embedded")), this,
            "str: whether the data source is a grid or a fixed atmosphere"),
        ("geom", None, uppercase(oneof(None, "PP", "SPH")), this,
            "str: the geometry of the atmopshere model"),
        ("depth", None, uppercase(oneof(None, "RHOX", "TAU")), this,
            "str: flag that determines whether to use RHOX or TAU for calculations"),
        ("interp", None, uppercase(oneof(None, "RHOX", "TAU")), this,
            "str: flag that determines whether to use RHOX or TAU for interpolation"),
        ("abund_format", "sme", oneof(*Abund._formats), this,
            "str: format of the Abundance field, as defined by the Abund class"),
        ("citation_info", "", asstr, this, "str: Citation text to cite in your papers"),
    ]
    # fmt: on

    def __new__(cls, natmo, npoints, **kwargs):
        dtype = [
            ("teff", "f4"),
            ("logg", "f4"),
            ("monh", "f4"),
            ("vturb", "f4"),
            ("lonh", "f4"),
            ("radius", "f4"),
            ("height", f"({npoints},)f4"),
            ("wlstd", "f4"),
            ("opflag", "(20,)i4"),
            ("abund", "(99,)f4"),
            ("temp", f"({npoints},)f4"),
            ("rhox", f"({npoints},)f4"),
            ("tau", f"({npoints},)f4"),
            ("rho", f"({npoints},)f4"),
            ("xna", f"({npoints},)f4"),
            ("xne", f"({npoints},)f4"),
        ]

        names = [s[0].lower() for s in dtype]
        titles = [s[0].upper() for s in dtype]

        data = super().__new__(cls, (natmo,), dtype=dtype, names=names, titles=titles)

        data.interp = "TAU"
        data.depth = "RHOX"
        data.method = "grid"
        data.geom = "PP"
        data.source = ""
        data.citation_info = ""
        data.abund_format = "sme"
        data.info = ""
        return data

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.interp = getattr(obj, "interp", "TAU")
        self.depth = getattr(obj, "depth", "RHOX")
        self.method = getattr(obj, "method", "grid")
        self.geom = getattr(obj, "geom", "PP")
        self.source = getattr(obj, "source", "")
        self.citation_info = getattr(obj, "citation_info", "")
        self.abund_format = getattr(obj, "abund_format", "sme")
        self.info = getattr(obj, "info", "")

    def __reduce__(self):
        # Get the parent's __reduce__ tuple
        pickled_state = super(AtmosphereGrid, self).__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + (
            self.interp,
            self.depth,
            self.source,
            self.geom,
            self.citation_info,
            self.method,
            self.abund_format,
            self.info,
        )
        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        self.interp = state[-8]
        self.depth = state[-7]
        self.source = state[-6]
        self.geom = state[-5]
        self.citation_info = state[-4]
        self.method = state[-3]
        self.abund_format = state[-2]
        self.info = state[-1]

        # Call the parent's __setstate__ with the other tuple elements.
        super(AtmosphereGrid, self).__setstate__(state[0:-8])

    def __getitem__(self, key):
        """Overwrite the getitem routine, so we keep additional
        properties and/or return an atmosphere object, when only
        one record is returned"""
        cls = self.__class__
        value = super().__getitem__(key)
        if isinstance(value, cls) and value.size == 1:
            return value[0]

        if isinstance(value, np.record):
            kwargs = {s: value[s] for s in value.dtype.names}
            value = Atmosphere(**kwargs)
        if isinstance(value, (Atmosphere, cls)):
            for name in self._names:
                setattr(value, name, getattr(self, name))
        return value

    def __str__(self):
        return self.source

    def __repr__(self):
        return str(self)

    def get(self, teff, logg, monh):
        mask = self.teff == teff
        mask &= self.logg == logg
        mask &= self.monh == monh
        return self[mask]

    @property
    def ndep(self):
        return self.shape[1]

    def save(self, filename):
        """Save the Atmopshere grid to a file using a numpy save format"""
        header = {
            "interp": self.interp,
            "depth": self.depth,
            "source": self.source,
            "geom": self.geom,
            "citation_info": self.citation_info,
            "method": self.method,
            "abund_format": self.abund_format,
            "info": self.info,
        }
        names = list(header.keys())
        values = [header[n] for n in names]
        header = np.rec.array(values, names=names)
        np.savez(filename, data=self, header=header)
        return

    @classmethod
    def load(cls, filename):
        """Load the atmosphere grid data from disk"""
        data = np.load(filename)
        self = data["data"].view(cls)
        header = data["header"]
        for k in header.dtype.names:
            v = header[k][()]
            setattr(self, k, v)
        return self
