# Large File Server

PySME does not come with all of the large atmosphere or NLTE grids
as part of the distribution. Instead Uppsala University provides
a server that serves the files when needed. Simply specify one of
the available filenames and PySME will fetch the file on your next run.

## Available Files

### Atmosphere grids:

- recommended:
  - marcs2012.sav [(Gustafsson et al. 2008)](https://ui.adsabs.harvard.edu/abs/2008A%26A...486..951G)
  - marcs2012p_t0.0.sav
  - marcs2012p_t1.0.sav
  - marcs2012p_t2.0.sav
  - marcs2012s_t1.0.sav
  - marcs2012s_t2.0.sav
  - marcs2012s_t5.0.sav
  - marcs2012t00cooldwarfs.sav
  - marcs2012t01cooldwarfs.sav
  - marcs2012t02cooldwarfs.sav

- deprecated:
  - atlas12.sav
  - atlas9_vmic0.0.sav
  - atlas9_vmic2.0.sav
  - interpatlas12.pro
  - interpmarcs2012.pro
  - ll_vmic2.0.sav

### NLTE grids:

- recommended and default grids:
  - H
    - nlte_H_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Li
    - nlte_Li_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - C
    - nlte_C_pysme.grd [(Amarsi et al. 2020; version 2)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - N
    - nlte_N_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - O
    - nlte_O_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Na
    - nlte_Na_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Mg
    - nlte_Mg_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Al
    - nlte_Al_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Si
    - nlte_Si_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - K
    - nlte_K_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Ca
    - nlte_Ca_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Ti
    - nlte_Ti_pysme.grd [(Mallinson et al. 2024)](https://ui.adsabs.harvard.edu/abs/2024A%26A...687A...5M)
  - Mn
    - nlte_Mn_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Fe
    - nlte_Fe_pysme.grd [(Amarsi et al. 2020; version 4)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)
  - Ba
    - nlte_Ba_pysme.grd [(Amarsi et al. 2020; version 3)](https://ui.adsabs.harvard.edu/abs/2020A%26A...642A..62A)

- deprecated:
  - H 
    - marcs2012_H2018.grd
  - Li
    - marcs2012_Li.grd [(Lind et al. 2009)](https://ui.adsabs.harvard.edu/abs/2009A%26A...503..541L)
    - marcs2012_Li2009.grd [(Lind et al. 2009)](https://ui.adsabs.harvard.edu/abs/2009A%26A...503..541L)
    - nlte_Li_multi.grd
  - C
    - marcs2012_C.grd
  - N 
    - marcs2012_N.grd
  - O
    - marcs2012p_t1.0_O.grd [(Sitnova et al. 2013)](https://ui.adsabs.harvard.edu/abs/2013AstL...39..126S)
    - marcs2012_O2015.grd [(Amarsi et al. 2016b)](https://ui.adsabs.harvard.edu/abs/2016MNRAS.455.3735A)
    - marcs2012_O.grd
  - Na
    - marcs2012p_t1.0_Na.grd [(Mashonkina et al. 2001)](https://ui.adsabs.harvard.edu/abs/2000ARep...44..790M)
    - marcs2012_Na.grd [(Lind et al. 2011)](https://ui.adsabs.harvard.edu/abs/2011A%26A...528A.103L)
    - marcs2012_Na2011.grd [(Lind et al. 2011)](https://ui.adsabs.harvard.edu/abs/2011A%26A...528A.103L)
    - nlte_Na_multi_full.grd
    - nlte_Na_multi_sun.grd
  - Al 
    - marcs2012_Al.grd
    - marcs2012_Al2017.grd
  - Mg
    - marcs2012_Mg2016.grd [(Osorio et al. 2016)](https://ui.adsabs.harvard.edu/abs/2016A%26A...586A.120O)
    - marcs2012_Mg.grd
  - Si
    - marcs2012_Si2016.grd [(Amarsi & Asplund 2017)](https://ui.adsabs.harvard.edu/abs/2017MNRAS.464..264A)
    - marcs2012_Si.grd
  - K
    - marcs2012_K.grd
  - Ca
    - marcs2012s_t2.0_Ca.grd [(Mashonkina et al. 2007)](https://ui.adsabs.harvard.edu/abs/2007A%26A...461..261M)
    - marcs2012p_t1.0_Ca.grd [(Mashonkina et al. 2017)](https://ui.adsabs.harvard.edu/abs/2007A%26A...461..261M)
    - marcs2012_Ca.grd
  - Ti
    - marcs2012s_t2.0_Ti.grd [(Sitnova et al. 2016)](https://ui.adsabs.harvard.edu/abs/2016MNRAS.461.1000S)
  - Mn
    - marcs2012_Mn.grd
  - Fe
    - marcs2012_Fe2016.grd [(Amarsi et al. 2016a)](https://ui.adsabs.harvard.edu/abs/2016MNRAS.463.1518A)
    - marcs2012s_t2.0_Fe.grd [(Mashonkina et al. 2011)](https://ui.adsabs.harvard.edu/abs/2011A%26A...528A..87M)
    - nlte_Fe_multi_full.grd
    - marcs2012_Fe.grd
  - Ba
    - marcs2012p_t1.0_Ba.grd [(Mashonkina et al. 1999)](https://ui.adsabs.harvard.edu/abs/1999A%26A...343..519M)
  - Eu
    - nlte_Eu.grd