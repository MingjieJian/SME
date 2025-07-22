# -*- coding: utf-8 -*-
from distutils.core import Extension, setup
from os.path import abspath, dirname, join

import numpy, sys
from libtools import get_full_libfile

libdir = abspath(dirname(get_full_libfile()))
include_dirs = [numpy.get_include(), libdir]

extra_link_args = []
if sys.platform == "darwin":
    # Ensure the extension first searches a sibling ``lib/`` directory at runtime
    # for libsme.{dylib,so}.  @loader_path expands to the directory containing
    # the *_smelib*.so itself, so placing libs in ``pysme/smelib/lib`` works both
    # in editable installs and built wheels.
    extra_link_args.append("-Wl,-rpath,@loader_path/lib")

module = Extension(
    "_smelib",
    sources=["_smelib.cpp"],
    language="c++",
    include_dirs=include_dirs,
    libraries=["sme"],
    library_dirs=[libdir],
    extra_link_args=extra_link_args
)

setup(ext_modules=[module])
