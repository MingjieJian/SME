# Atmosphere

For the spectral synthesis PySME needs a model atmosphere
to perform the radiative transfer in. PySME does not come
with a set of atmospheres in each distribution but instead
uses the LFS (See [lfs](lfs.md)) to fetch only the required
model atmosphere when run.

If you want to provide your own model atmosphere file, it should be present in `~/.sme/atmospheres/`.

Each atmosphere model file describes a grid of models, on
which we then linearly interpolate to the desired stellar parameters.
Sometimes we dare extrapolate from this grid as well, but in that case,
we always show a warnning.

Note that the atmosphere also contains a seperate set of stellar
parameters, which is usually the same as that of the sme structure,
but can be different, if for example the atmosphere is embedded, i.e.
fixed, or has not been calculated yet.

The atmopshere object has the following fields

- **`teff`**: Effective Temperature in Kelvin  
- **`logg`**: Surface Gravity in log(cgs)  
- **`monh`**: Metallicity relative to the individual abundances  
- **`abund`**: The individual abundances (see [abund](#abund))  
- **`vsini`**: Projected Rotational velocity in km/s  
- **`vmic`**: Microturbulence velocity in km/s  
- **`vmac`**: Macroturbulence velocity in km/s  
- **`vturb`**: Turbulent velocity in km/s  
- **`lonh`**: Mixing length   
- **`source`**: Filename of the atmosphere grid  
- **`depth`**:  
  The depth scale to use for calculations.  
  Either RHOX or TAU  
- **`interp`**:  
  The depth scale to use for interpolation.  
  Either RHOX or TAU  
- **`geom`**:  
  The geometry of the atmosphere. Either Plane  
  Parallel `'PP'` or Spherical `'SPH'`  
- **`method`**:  
  The method to use for interpolation. Either `'grid'`  
  for a model grid or `'embedded'` if only a single  
  atmosphere is given.  
- **`rhox`**: 'Column density' depth scale  
- **`tau`**: 'Optical depth' depth scale  
- **`temp`**: Temperature profile  
- **`xna`**: Number density of atoms, ions, and molecules in each depth  
- **`xne`**: Number density of electrons in each depth  

## Grid atmospheres 

![](../img/atmosphere/marcs2012_grid.png)
![](../img/atmosphere/marcs2012p_t0.0_grid.png)
![](../img/atmosphere/marcs2012p_t1.0_grid.png)
![](../img/atmosphere/marcs2012p_t2.0_grid.png)
![](../img/atmosphere/marcs2012s_t1.0_grid.png)
![](../img/atmosphere/marcs2012s_t2.0_grid.png)
![](../img/atmosphere/marcs2012s_t5.0_grid.png)
![](../img/atmosphere/marcs2012t00cooldwarfs_grid.png)
![](../img/atmosphere/marcs2012t01cooldwarfs_grid.png)
![](../img/atmosphere/marcs2012t02cooldwarfs_grid.png)
![](../img/atmosphere/atlas12_grid.png)
![](../img/atmosphere/atlas9_vmic0.0_grid.png)
![](../img/atmosphere/atlas9_vmic2.0_grid.png)
![](../img/atmosphere/ll_vmic2.0_grid.png)