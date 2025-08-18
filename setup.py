#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py — minimal shim for legacy invocations
from setuptools import setup
import versioneer

if __name__ == "__main__":
    setup(
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
    )
