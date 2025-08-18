# # -*- coding: utf-8 -*-
# from distutils.core import Extension, setup
# from os.path import abspath, dirname, join

# import numpy, sys
# from libtools import get_full_libfile

# libdir = abspath(dirname(get_full_libfile()))
# include_dirs = [numpy.get_include(), libdir]

# extra_link_args = []
# if sys.platform == "darwin":
#     # Ensure the extension first searches a sibling ``lib/`` directory at runtime
#     # for libsme.{dylib,so}.  @loader_path expands to the directory containing
#     # the *_smelib*.so itself, so placing libs in ``pysme/smelib/lib`` works both
#     # in editable installs and built wheels.
#     extra_link_args.append("-Wl,-rpath,@loader_path/lib")

# module = Extension(
#     "_smelib",
#     sources=["_smelib.cpp"],
#     language="c++",
#     include_dirs=include_dirs,
#     libraries=["sme"],
#     library_dirs=[libdir],
#     extra_link_args=extra_link_args
# )

# setup(ext_modules=[module])

# -*- coding: utf-8 -*-
from setuptools import Extension, setup
from pathlib import Path
import numpy as np
import sys

from libtools import get_full_libfile

libdir = Path(get_full_libfile()).resolve().parent
include_dirs = [np.get_include(), str(libdir)]

extra_link_args = []
if sys.platform == "darwin":
    extra_link_args += ["-Wl,-rpath,@loader_path/../lib"]
# elif sys.platform.startswith("linux"):
#     extra_link_args += ["-Wl,-rpath,$ORIGIN/../lib"]

ext = Extension(
    name="_smelib",                          # 在 pysme/smelib 目录内就地编译
    sources=["_smelib.cpp"],                 # 你的 C++ 扩展源码 :contentReference[oaicite:2]{index=2}
    language="c++",
    include_dirs=include_dirs,
    libraries=["sme"],                       # 仍然链接 libsme.*
    library_dirs=[str(libdir)],
    extra_link_args=extra_link_args,
)

if __name__ == "__main__":
    setup(ext_modules=[ext])
