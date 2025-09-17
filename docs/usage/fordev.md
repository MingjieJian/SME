# For dev


```{warning}
This is the page mainly for developers of PySME and the note on its function, which may have inaccurate information.
```

## PySME components

Since SME is the C++/Fortran library for the spectral synthesis part, PySME is divided into a few components to make the code work.
1. python package. This is the main interface which the users interact with.
2. `SMR_DLL` class in `sme_synth.py`. This class perform some necessary manipulation for the input and pass it to the functions inside `_smelib`
3. `_smelib` compiled in `src/pysme/smelib`. This is the C-extension which attach the python side data and C++ side data.
4. `libsme.so` pre-compiled in `SMElib` repository. It perform actual synthesis with C++/Fortran.

## What does PySME do from installation to the first use?

### 1. `pip install pysme-astro`

Part 1 and 2 are download and compiled from source. Note that part 3 and 4 are not downloaded nor compiled.

### 2. `import pysme` - part 4

This triggers the running of `__init__.py`.
For the first time running, there is no part 4 (the SME library). 
The code then triggers `libtools.download_libsme()`.
It downloads the latest version of SME library from the [github repository](https://github.com/MingjieJian/SMElib/releases/latest) to `py_env/lib/python3.10/site-packages/pysme/`, extract to the `lib` folder, and delete the compressed file.

### 3. `import pysme` - part 3

The last step is part 3. The code first try to run `from .smelib import _smelib`. 
If there is an error (no `_smelib` is found), then the code triggers `libtools.compile_interface()`.

The code then goes to `py_env/lib/python3.10/site-packages/pysme/smelib`, run `python3 setup.py build_ext --inplace` and goes back to the initial folder.

## How to rebuild  smelib

```py
cd src/pysme/smelib
python3 setup.py build_ext --inplace
cp _smelib.cpython-310-x86_64-linux-gnu.so /path/to/anaconda3/envs/astro_py310/lib/python3.10/site-packages/pysme/smelib/      
```

## Versions in SME/PySME

There are a few versions in SME/PySME:
- SMElib version
    - The version of the SME library, defined in `SMElib/src/sme/sme_synth_faster.h`, varialbe `VERSION`.
    - This is defined manually.
- SMElib release version
    - Since the SME library here is mainly for the use of PySME, slight modification may be required for the library compilation.
    - The release version is desigend for such small (not effection the synthesize result) function.
    - It will keep the same MAJOR and MINOR versioning, and use PATCH version to indicate the updates.
    - In the ideal situation, SMELIb release version will be the same as SMElib version. 
- PySME version
    - The version of the PySME, which is independent of the versions mentioned above.
    - We will try our best to use the MINOR version to refer to the SMELib version, but large release may take a leap on this.

### Version matching between SMElib and PySME

For the convenience of development, most of the PySME version will download the latest version of SMELib in their first run.
This will allow us to keep the PySME using the latest SMElib, receving new functions and bug fixes on the library side.
However, when SMElib have breaking updates, the older version of PySME would match with incompatible SMELib in its latest version.
Before each breaking updates in SMElib, one specific PySME version (usually ) will be connected with a specific SMELib version to maintain the compatibilty of this version.

For other versions, we will not solve the future compatibility issue.
You can download the corresponding SMElib, and override the default library manually.

The follwing table shows the version matching between SMElib and PySME.

|PySME version|SMElib release version|SMElib version|
|:--:|:--:|:--:|
|v0.5.0-|latest (v6.13.x)|6.13 (June 2025)|
|v0.4.199|v6.0.6 (freezed)|6.03 (July 2019)|
|v0.4.167-v0.4.198|v6.0.6 (not freezed)|6.03 (July 2019)|

The PySME version range indicate the versions which manually matchting of the SMELib is required, and the single PySME version indicates the one with freezed SMElib (thus only pip install is required before using).
Note that:
- Small bug fix on SMElib will be labeled with the PATCH version, thus the actual SMElib used would be 6.13.x. The change of SMElib MAJOR and MINOR version will follow that in SME. 
- The support for Apple Silicon Mac is not complete for PySME v0.4. You need to clone the SMELib from the source code, compile and replace the library files by yourself.

### How to update PySME/SMElib version

The versions are controlled by `git tag`. 
For PySME, setting a new tag will update the version to the latest tag.
For SMElib, setting a new release will based on a tag. 

## NLTE departure coefficients

What happens when the NLTE grid is added into PySME?

1. `sme.nlte.set_nlte()`, then nothing happens.
2. Inside `synthesize_spectrum()`, `sme.nlte.update_coefficients(sme, dll, self.lfs_nlte)` will be triggered if there is nlte grids in `sme`.

### `nlte.update_coefficients`

1. All the $b$s will be reset by `dll.ResetDepartureCoefficients()`.
2. Format of line list will be check, and NLTE calculation will not be performed if the format is not `long`.
3. Get the NLTE grid using `self.get_grid(sme, elem, lfs_nlte)`
4. If no lines are found for this element, remove it from NLTE list.
5. Get the $b$ matrix using `grid.get(sme.abund, sme.teff, sme.logg, sme.monh, sme.atmo)`. 
    - This is also the core part of `update_coefficients`.
6. Input the $b$s using `dll.InputDepartureCoefficients(bmat[:, lr], li)`.

### `grid.get`

