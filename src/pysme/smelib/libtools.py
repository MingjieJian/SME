# -*- coding: utf-8 -*-
"""
These libtools are used to locate, download, and install the SME C/Fortran
library.
"""

import ctypes as ct
import logging
import os, re
import platform
import subprocess
import sys, glob, shutil
import zipfile
from pathlib import Path
from os.path import basename, dirname, exists, join, realpath

import os, sys, subprocess
import zipfile
from pathlib import Path
import shutil

import wget

logger = logging.getLogger(__name__)

smelib_releases = {
    "default":  "latest/download",
    "0.4.198":  "download/v6.0.6",
    "0.4.199":  "download/v6.0.6",          
}

def download_libsme(loc=None, pysme_version='default'):
    """
    Download the SME library and the necessary datafiles

    Parameters
    ----------
    loc : str, optional
        the path to the location the files should be placed,
        by default they are placed so that PySME can find and use them

    Raises
    ------
    KeyError
        If no existing library is found for this system
    """

    pysme_version = pysme_version.split('+')[0]
    release_subpath = smelib_releases.get(
        pysme_version, smelib_releases["default"]
    )

    if loc is None:
        loc = dirname(dirname(get_full_libfile()))

    # Download compiled library from github releases
    github_releases_url = (
        f"https://github.com/MingjieJian/SMElib/releases/{release_subpath}"
    )
    print("Downloading and installing the latest libsme version for this system")
    aliases = {
        "Linux": "manylinux2014_x86_64",
        "Windows": "windows",
        "Darwin": "macos",
    }
    system = platform.system()

    try:
        system = aliases[system]
        print("Identified OS: %s" % system)
    except KeyError:
        raise KeyError(
            f"Could not find the associated compiled library for this system {system}."
            " Either compile it yourself and place it in src/pysme/ or open an"
            " issue on Github. Supported systems are: Linux, MacOS, Windows."
        )

    # Refine verion for Apple Silicon chips
    if system == 'macos':
        brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
        print(brand)

        # Search for the number after "Apple M"
        match = re.search(r"Apple\s*M\s*(\d+)", brand)
        if match:
            # For M1, use M2 version; for M3 use M4 verion (but not test yet)
            if match.group(1) == '1':
                use_version = '2'
            elif match.group(1) == '3':
                use_version = '4'
            else:
                use_version = match.group(1)
            system += f'-arm-M{use_version}' 

    github_releases_fname = "{system}-gfortran.zip".format(system=system)
    url = github_releases_url + "/" + github_releases_fname
    fname = join(loc, github_releases_fname)

    try:
        os.remove(fname)
    except FileNotFoundError:
        pass

    print("Downloading file %s" % url)
    print(f"Creating folder for lib files: {loc}")
    os.makedirs(loc, exist_ok=True)
    wget.download(url, out=loc)
    # the wget progress bar, does not include a new line
    print("")

    print("Extracting file")
    zipfile.ZipFile(fname).extractall(loc)

    try:
        os.remove(fname)
    except FileNotFoundError:
        pass

    print("done")

    if system in ["macos"]:
        # Need to adjust the install_names in the dylib
        print("Fixing the file paths in the .dylib file")
        fname = realpath(get_full_libfile())
        subprocess.run(
            ["install_name_tool", "-id", fname, fname], capture_output=True, check=True
        )

def download_compile_smelib(tag=None, outdir=f'{str(Path.home())}/.sme/SMElib'):
    """
    Download and compile a specified versio of SMElib; if tag=None then download the latest.

    Example: tag: 6.13.3
    """
    # def _github_get(url):
    #     hdrs = {"Accept": "application/vnd.github+json"}
    #     r = requests.get(url, headers=hdrs, timeout=30)
    #     r.raise_for_status()
    #     return r.json()
    
    GITHUB_API = "https://api.github.com"
    OWNER = "MingjieJian"
    REPO  = "SMElib"

    if not Path(outdir).exists():
        Path(outdir).mkdir(parents=True, exist_ok=True)

    # if tag:
    #     pass
    #     # meta = _github_get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/releases/tags/{tag}")
    # else:
    #     meta = _github_get(f"{GITHUB_API}/repos/{OWNER}/{REPO}/releases/latest")
    #     tag = meta["tag_name"].replace('v', '')

    # zip_url = meta["zipball_url"]
    zip_url = f'https://api.github.com/repos/MingjieJian/SMElib/zipball/{tag}'
    local_zip = os.path.join(outdir, f"SMElib-{tag}.zip")
    extract_dir = os.path.join(outdir, f"SMElib-{tag}")

    if Path(local_zip).exists():
        Path(local_zip).unlink()
    if Path(extract_dir).exists():
        shutil.rmtree(extract_dir)

    logger.info(f'Downloading SMElib verion {tag} from {zip_url}, saving it as {local_zip}')
    wget.download(zip_url, local_zip)

    logger.info(f'Extracting {local_zip} to {extract_dir}')
    zipfile.ZipFile(local_zip).extractall(extract_dir)

    top = Path(extract_dir).resolve()
    
    # Find the only one subfolder
    subdirs = [p for p in top.iterdir() if p.is_dir()]
    if len(subdirs) != 1:
        raise RuntimeError(f"Expected to find 1 subfolder, found {len(subdirs)}: {subdirs}")
    
    sub = subdirs[0]
    
    for item in sub.iterdir():
        target = top / item.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.move(str(item), top)

    logger.info('Compiling SMElib ...')
    cwd = Path.cwd()
    os.chdir(extract_dir)
    subprocess.run(["chmod", "755", "./compile_smelib.sh"], check=True)
    # with open("smelib_compile.log", "w") as f:
    #     subprocess.run(["./compile_smelib.sh"], stdout=f, stderr=subprocess.STDOUT, check=True)

    proc = subprocess.run(
        ["./compile_smelib.sh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,   # 把 stderr 合并进 stdout，方便统一处理
        text=True                   # Python 3.7+，自动把 bytes 解码成 str
    )

    with open("smelib_compile.log", "w") as f:
        f.write(proc.stdout)
    
    print(proc.stdout)
    print(proc.stderr)
    
    os.chdir(cwd)
    logger.info('Compilation finished.')

    return extract_dir

def _safe_symlink(src, dst):
    """Create **dst → src** symbolic link, forcibly replacing any pre-existing
    file, directory, or symlink at *dst*.
    """
    src = Path(src).resolve()
    dst = Path(dst)

    if dst.is_symlink() or dst.exists():
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:  # directory
            shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.symlink_to(src)

def link_interface_smelib(loc):
    '''
    This funciton does not check if the library exists or not.
    '''

    pysme_dir = dirname(dirname(__file__))
    _safe_symlink(Path(f"{loc}/lib").resolve(), Path(f"{pysme_dir}/lib"))
    _safe_symlink(Path(f"{loc}/src/data").resolve(), Path(f"{pysme_dir}/share/libsme"))

def compile_interface():
    """
    Compiles the Python Module Interface to the SME library. This needs to be
    called once, before trying to import _smelib.

    Since the module uses the setup.py method to be compiled,
    it is somewhat hacked together to make it work.
    """
    libdir = join(dirname(__file__))
    executable = sys.executable
    if executable is None:
        # If python is unable to identify the path to its own executable use python3
        # This is unlikely to happen for us though
        executable = "python3"
    cwd = os.getcwd()
    # We need to swith to the correct directory and back, for setup.py to work
    os.chdir(libdir)
    subprocess.run([executable, "setup.py", "build_ext", "--inplace"])
    os.chdir(cwd)


def get_lib_name():
    """Get the name of the SME C library"""
    system = platform.system().lower()

    if system == "windows":
        return "libsme-5.dll"
    elif system == "darwin":
        return "libsme.dylib"

    arch = platform.machine()
    bits = 64  # platform.architecture()[0][:-3]

    return "sme_synth.so.{system}.{arch}.{bits}".format(
        system=system, arch=arch, bits=bits
    )


def get_lib_directory():
    """
    Get the directory name of the library. I.e. 'lib' on all systems
    execpt windows, and 'bin' on windows
    """
    if platform.system() in ["Windows"]:
        dirpath = "bin"
    else:
        # For Linux/MacOS
        dirpath = "lib"
    return dirpath


def get_full_libfile():
    """Get the full path to the sme C library"""
    localdir = dirname(dirname(__file__))
    libfile = get_lib_name()
    dirpath = get_lib_directory()
    libfile = join(localdir, dirpath, libfile)
    return libfile


def load_library(libfile=None):
    """
    Load the SME library using cytpes.CDLL

    This is useful and necessary for the pymodule interface to find the
    library.

    Parameters
    ----------
    libfile : str, optional
        filename of the library to load, by default use the SME library in
        this package

    Returns
    -------
    lib : CDLL
        library object of the SME library
    """
    if libfile is None:
        libfile = get_full_libfile()
    try:
        os.add_dll_directory(dirname(libfile))
    except AttributeError:
        newpath = dirname(libfile)
        if "PATH" in os.environ:
            newpath += os.pathsep + os.environ["PATH"]
        os.environ["PATH"] = newpath
    return ct.CDLL(str(libfile))


def get_full_datadir():
    """
    Get the filepath to the datafiles of the SME library
    """
    localdir = dirname(dirname(__file__))
    datadir = join(localdir, "share/libsme/")
    return datadir
