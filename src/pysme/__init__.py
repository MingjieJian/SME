# -*- coding: utf-8 -*-
__file_ending__ = ".sme"

# Load correct version string
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

# Add output to the console
import logging, os, sys

import colorlog
import tqdm
from pathlib import Path


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console = TqdmLoggingHandler()
console.setLevel(logging.INFO)
console.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)s - %(message)s")
)
logger.addHandler(console)

# Download library if it does not exist
import os.path
from ctypes import cdll

from .smelib import libtools

# First-time setup, if not done.
from .init_config import ensure_user_config
ensure_user_config()

# if os.getenv("PYSME_AUTO_INIT", "1") not in ("0", "false", "False"):
#     try:
#         from .init_config import ensure_user_config
#         verbose = os.getenv("PYSME_INIT_VERBOSE", "0") in ("1", "true", "True")
#         ensure_user_config()
#     except Exception:
#         # 别让导入因为初始化失败而崩；必要时记录日志
#         pass

libfile = libtools.get_full_libfile()
if not os.path.exists(libfile):
    # smelib_dir = libtools.download_compile_smelib(tag='6.13.5', outdir=f'{os.path.dirname(__file__)}/lib_sc')
    # smelib_dir = libtools.download_compile_smelib(tag='6.13.7')
    # libtools.link_interface_smelib(smelib_dir)
    smelib_dir = libtools.download_smelib()

try:
    cdll.LoadLibrary(libfile)
    from .smelib import _smelib
except OSError as e:
    # macOS 上若报架构不匹配，自动下载所需架构并重试一次
    msg = str(e)
    if sys.platform == "darwin" and ("incompatible architecture" in msg or "mach-o file" in msg):
        need = libtools._parse_needed_arch_from_error(msg)
        print("Detected arch mismatch; need:", need)
        libtools.download_smelib(force_arch=need)
        try:
            cdll.LoadLibrary(libfile)
            from .smelib import _smelib
        except Exception:
            libtools.compile_interface()
    else:
        libtools.compile_interface()
except Exception:
    # 其它非 OSError 的情况（如 ImportError 等）
    libtools.compile_interface()

# try:
#     cdll.LoadLibrary(libfile)
#     from .smelib import _smelib
# except:
#     libtools.compile_interface()

# Extract the 3DNLTE H line profiles
if not os.path.exists('~/.sme/hlineprof/lineprof.dat'):
    """Setup the H line profile data during package installation"""
    import gzip
    from pathlib import Path
    
    # 创建目标目录
    target_dir = os.path.expanduser("~/.sme/hlineprof")
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    
    # 获取包内的gz文件路径
    gz_file = os.path.join(os.path.dirname(__file__), "lineprof.dat.gz")
    
    # 解压文件
    target_file = os.path.join(target_dir, "lineprof.dat")  # 去掉.gz后缀
    if not os.path.exists(target_file):
        with gzip.open(gz_file, 'rb') as f_in:
            with open(target_file, 'wb') as f_out:
                f_out.write(f_in.read())

# Provide submodules to the outside
__all__ = [
    "util",
    "abund",
    "atmosphere",
    "broadening",
    "continuum_and_radial_velocity",
    "cwrapper",
    "echelle",
    "iliffe_vector",
    "linelist",
    "nlte",
    "sme_synth",
    "sme",
    "solve",
    "uncertainties",
    "smelib",
]