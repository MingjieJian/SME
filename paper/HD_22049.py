# -*- coding: utf-8 -*-
"""
Prepare and fit a number of similar spectra for a list of targets
"""
import datetime
import os
import os.path
import re
import sys
from os.path import dirname, join, realpath

# import matplotlib.pyplot as plt
import numpy as np
from astropy import constants as const
from astropy.io import fits
from data_sources.StellarDB import StellarDB
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.optimize import least_squares
from tqdm import tqdm

from pysme import sme as SME
from pysme import util
from pysme.abund import Abund
from pysme.continuum_and_radial_velocity import determine_radial_velocity
from pysme.gui import plot_plotly
from pysme.iliffe_vector import Iliffe_vector
from pysme.linelist.vald import ValdFile
from pysme.sme import MASK_VALUES
from pysme.solve import solve
from pysme.synthesize import synthesize_spectrum

# from pyreduce.util import top, middle


# def continuum_normalize(
#     spec,
#     wave,
#     cont,
#     sigm,
#     iterations=10,
#     smooth_initial=1e5,
#     smooth_final=5e6,
#     scale_vert=1,
# ):
#     """Fit a continuum to a spectrum by slowly approaching it from the top.
#     We exploit here that the continuum varies only on large wavelength scales, while individual lines act on much smaller scales

#     TODO automatically find good parameters for smooth_initial and smooth_final
#     TODO give variables better names

#     Parameters
#     ----------
#     spec : masked array of shape (nord, ncol)
#         Observed input spectrum, masked values describe column ranges
#     wave : masked array of shape (nord, ncol)
#         Wavelength solution of the spectrum
#     cont : masked array of shape (nord, ncol)
#         Initial continuum guess, for example based on the blaze
#     sigm : masked array of shape (nord, ncol)
#         Uncertainties of the spectrum
#     iterations : int, optional
#         Number of iterations of the algorithm,
#         note that runtime roughly scales with the number of iterations squared
#         (default: 10)
#     smooth_initial : float, optional
#         Smoothing parameter in the initial runs, usually smaller than smooth_final (default: 1e5)
#     smooth_final : float, optional
#         Smoothing parameter of the final run (default: 5e6)
#     scale_vert : float, optional
#         Vertical scale of the spectrum. Usually 1 if a previous normalization exists (default: 1)
#     plot : bool, optional
#         Wether to plot the current status and results or not (default: True)

#     Returns
#     -------
#     cont : masked array of shape (nord, ncol)
#         New continuum
#     """

#     nord, ncol = spec.shape

#     par2 = 1e-4
#     par4 = 0.01 * (1 - np.clip(2, None, 1 / np.sqrt(np.ma.median(spec))))

#     b = np.clip(cont, 1, None)
#     mask = ~np.ma.getmaskarray(b)
#     for i in range(nord):
#         b[i, mask[i]] = middle(b[i, mask[i]], 1)
#     cont = b

#     # Create new equispaced wavelength grid
#     tmp = wave.ravel()
#     wmin = np.min(tmp)
#     wmax = np.max(tmp)
#     dwave = np.abs(tmp[tmp.size // 2] - tmp[tmp.size // 2 - 1]) * 0.5
#     nwave = np.ceil((wmax - wmin) / dwave) + 1
#     new_wave = np.linspace(wmin, wmax, int(nwave), endpoint=True)

#     # Combine all orders into one big spectrum, sorted by wavelength
#     wsort, j, index = np.unique(tmp, return_index=True, return_inverse=True)
#     sB = ((spec / cont).ravel())[j]

#     # Get initial weights for each point
#     weight = middle(sB, 0.5, x=wsort - wmin)
#     weight = weight / middle(weight, 3 * smooth_initial) + np.concatenate(
#         ([0], 2 * weight[1:-1] - weight[0:-2] - weight[2:], [0])
#     )
#     weight = np.clip(weight, 0, None)
#     # TODO for some reason the interpolation messes up, use linear instead for now
#     # weight = util.safe_interpolation(wsort, weight, new_wave)
#     weight = np.interp(new_wave, wsort, weight)
#     weight /= np.max(weight)

#     # Interpolate Spectrum onto the new grid
#     # ssB = util.safe_interpolation(wsort, sB, new_wave)
#     ssB = np.interp(new_wave, wsort, sB)
#     # Keep the scale of the continuum
#     bbb = middle(cont.ravel()[j], 1)

#     contB = np.ones_like(ssB)

#     try:
#         for i in tqdm(range(iterations)):
#             # Find new approximation of the top, smoothed by some parameter
#             c = ssB / contB
#             for _ in tqdm(range(iterations)):
#                 _c = top(
#                     c, smooth_initial, eps=par2, weight=weight, lambda2=smooth_final
#                 )
#                 c = np.clip(_c, c, None)
#             c = (
#                 top(c, smooth_initial, eps=par4, weight=weight, lambda2=smooth_final)
#                 * contB
#             )

#             # Scale it and update the weights of each point
#             contB = c * scale_vert
#             contB = middle(contB, 1)
#             weight = np.clip(ssB / contB, None, contB / np.clip(ssB, 1, None))
#     except ValueError:
#         pass

#     # Calculate the new continuum from intermediate values
#     # new_cont = util.safe_interpolation(new_wave, contB, wsort)
#     new_cont = np.interp(wsort, new_wave, contB)
#     mask = np.ma.getmaskarray(cont)
#     cont[~mask] = (new_cont * bbb)[index]

#     return cont


def hl_envelopes_idx(s, dmin=1, dmax=1, split=False):
    """
    Input :
    s: 1d-array, data signal from which to extract high and low envelopes
    dmin, dmax: int, optional, size of chunks, use this if the size of the input signal is too big
    split: bool, optional, if True, split the signal in half along its mean, might help to generate the envelope in some cases
    Output :
    lmin,lmax : high/low envelope idx of input signal s
    """

    # locals min
    lmin = (np.diff(np.sign(np.diff(s))) > 0).nonzero()[0] + 1
    # locals max
    lmax = (np.diff(np.sign(np.diff(s))) < 0).nonzero()[0] + 1

    if split:
        # s_mid is zero if s centered around x-axis or more generally mean of signal
        s_mid = np.mean(s)
        # pre-sorting of locals min based on relative position with respect to s_mid
        lmin = lmin[s[lmin] < s_mid]
        # pre-sorting of local max based on relative position with respect to s_mid
        lmax = lmax[s[lmax] > s_mid]

    # global max of dmax-chunks of locals max
    lmin = lmin[
        [i + np.argmin(s[lmin[i : i + dmin]]) for i in range(0, len(lmin), dmin)]
    ]
    # global min of dmin-chunks of locals min
    lmax = lmax[
        [i + np.argmax(s[lmax[i : i + dmax]]) for i in range(0, len(lmax), dmax)]
    ]

    return lmin, lmax


def load_star(target, update=True):
    sdb = StellarDB(sources=["simbad", "exoplanets_nasa"])
    if update:
        star = sdb.auto_fill(target)
    star = sdb.load(target)
    return star


def get_value(star, name, unit, alt=None):
    if name in star:
        return star[name].to_value(unit)
    else:
        return alt


def load_fname(star, data_dir):
    alias = [re.sub(r"[-_ *]", "", s).lower() for s in star["id"]]

    # Find the correct data file for this target
    files = [fname for fname in os.listdir(data_dir) if fname.endswith(".fits")]
    isFound = False
    for fname in files:
        hdu = fits.open(join(data_dir, fname))
        header = hdu[0].header
        obj = header["OBJECT"]
        obj = re.sub(r"[-_ *]", "", obj).lower()
        hdu.close()
        if obj in alias:
            isFound = True
            break
    if not isFound:
        raise ValueError("No data file found")
    return join(data_dir, fname)


def load_tellurics():
    # Get tellurics from Tapas
    examples_dir = dirname(realpath(__file__))
    fname = join(examples_dir, "data/tapas.npz")
    try:
        data = np.load(fname)
        wtapas = data["wave"]
        ftapas = data["flux"]
    except:
        ftapas = join(examples_dir, "data/tapas.ipac")
        dtapas = np.genfromtxt(ftapas, comments="\\", skip_header=36)
        wtapas, ftapas = dtapas[:, 0], dtapas[:, 1]
        # convert to angstrom
        wtapas *= 10
        # Normalize
        ftapas -= ftapas.min()
        ftapas /= ftapas.max()
        wtapas = wtapas[::-1]
        ftapas = ftapas[::-1]
        np.savez(fname, wave=wtapas, flux=ftapas)
    return wtapas, ftapas


def normalize(wave, flux, dmin=1000, dmax=1000, return_cont=False):
    scale = np.nanpercentile(flux, 95)
    flux = flux / scale
    # Get first guess from upper envelope
    mflux = median_filter(flux, 3)
    _, high_idx = hl_envelopes_idx(mflux, dmin=dmin, dmax=dmax)
    high_idx = np.array([0, *high_idx])
    cont = interp1d(
        wave[high_idx], flux[high_idx], kind="linear", fill_value="extrapolate"
    )(wave)
    cont = gaussian_filter1d(cont, dmax)
    if return_cont:
        return cont * scale
    else:
        return flux / cont


def vel_shift(rv, wave):
    c_light = const.c.to_value("km/s")
    rv_factor = np.sqrt((1 - rv / c_light) / (1 + rv / c_light))
    wave = rv_factor * wave
    return wave


def get_rv_tell(wave, flux, wtell, ftell):
    # mask = (wave > 6200) & (wave < 6400)
    mask = wave > 6866
    sme = SME.SME_Structure(wave=[wave[mask]], sob=[flux[mask]])
    sme.vrad_flag = "each"
    sme.cscale_flag = "none"
    rv_tell = determine_radial_velocity(
        sme, wtell, ftell, 0, least_squares_kwargs={"bounds": (-200, 200)}
    )
    # plt.plot(vel_shift(rv, wave[sme.mask[0] == 1]), flux[sme.mask[0] == 1])
    # plt.plot(wtapas[wtapas > 6866], ftapas[wtapas > 6866])
    # plt.show()
    return rv_tell


def match_tell_with_obs(wave, flux, wtell, ftell):
    ftell = np.interp(wave, wtell, ftell)
    wtell = wave
    mtell = wtell > 6866
    func = lambda x: gaussian_filter1d(ftell[mtell], x[0]) - flux[mtell]
    res = least_squares(func, x0=[1], loss="soft_l1", method="trf")
    ftell = gaussian_filter1d(ftell, res.x[0])
    # plt.plot(wave, flux)
    # plt.plot(wtell, ftell)
    # plt.show()
    return wtell, ftell


def split_into_segments(wave, flux, ftell):
    nsteps = 10000
    wave = [
        wave[nsteps * i : nsteps * (i + 1)]
        for i in range(int(np.ceil(len(wave) / nsteps)))
    ]
    flux = [
        flux[nsteps * i : nsteps * (i + 1)]
        for i in range(int(np.ceil(len(flux) / nsteps)))
    ]
    ftell = [
        ftell[nsteps * i : nsteps * (i + 1)]
        for i in range(int(np.ceil(len(ftell) / nsteps)))
    ]
    return wave, flux, ftell


def init(
    target,
    mask=None,
    linelist="harps.lin",
    segments="all",
    cscale="match+linear",
    vrad="each",
):
    examples_dir = dirname(realpath(__file__))
    data_dir = join(examples_dir, "data")
    # /home/ansgar/Documents/Python/sme/examples/paper/data/ADP.2019-11-16T01 15 37.789.fits
    # Define the location of all your files
    # this will put everything into the example dir
    # Get stellar data from online sources
    star = load_star(target, update=False)
    # Find the correct data file for this target
    in_file = load_fname(star, data_dir)
    vald_file = join(examples_dir, f"data/{linelist}")
    mid_file = join(examples_dir, f"results/{target}_inp.sme")

    # Load data from fits file
    hdu = fits.open(in_file)
    wave = hdu[1].data["WAVE"][0]
    if "FLUX_REDUCED" in hdu[1].data.columns.names:
        flux = hdu[1].data["FLUX_REDUCED"][0]
    else:
        flux = hdu[1].data["FLUX"][0]
    if "ERR_REDUCED" in hdu[1].data.columns.names:
        uncs = hdu[1].data["ERR_REDUCED"][0]
    else:
        uncs = hdu[1].data["ERR"][0]
    # the error column is all NaNs
    uncs[np.isnan(uncs)] = np.sqrt(np.abs(flux[np.isnan(uncs)]))

    if mask is not None:
        for m in mask:
            flux[m[0] : m[1]] = 0
    cont = normalize(wave, flux, return_cont=True)
    # dw = np.median(np.diff(wave))
    # cont = gaussian_filter1d(flux, 6000 * dw) * 1.5
    flux /= cont
    uncs /= np.abs(cont)

    # plt.plot(wave, uncs / np.nanmedian(uncs))
    # plt.plot(wave, np.sqrt(flux) / np.nanmedian(np.sqrt(flux)))
    # plt.show()

    # cont = continuum_normalize(
    #     flux[None, :],
    #     wave[None, :],
    #     cont[None, :],
    #     None,
    # )

    # Get tellurics from Tapas
    wtapas, ftapas = load_tellurics()
    ftapas = normalize(wtapas, ftapas, dmin=100, dmax=100)

    # Transform to earth restframe
    rv_tell = get_rv_tell(wave, flux, wtapas, ftapas)
    wave = vel_shift(rv_tell, wave)

    # Match the broadening of the observation
    wtapas, ftapas = match_tell_with_obs(wave, flux, wtapas, ftapas)

    # Split the spectrum into arbitrary chunks
    # (This makes the progress bar more useful)
    # TODO: is this the same for all stars?
    wave, flux, ftapas = split_into_segments(wave, flux, ftapas)

    # Create the SME structure
    sme = SME.SME_Structure(wave=wave, sob=flux)
    # This should already be the default
    sme.leastsquares_loss = "linear"

    sme.meta["object"] = target
    sme.normalize_by_continuum = True
    sme.nmu = 7
    # Use simple shot noise assumption for uncertainties
    sme.uncs = uncs
    # Add telluric data (without rayleigh scattering)
    sme.telluric = Iliffe_vector(values=ftapas)
    # Create first mask by removing the telluric offset
    sme.mask = MASK_VALUES.LINE
    for i in range(sme.nseg):
        sme.mask[i][sme.telluric[i] < 0.995] = MASK_VALUES.BAD
        sme.mask[i][sme.spec[i] == 0] = MASK_VALUES.BAD

    # Get first guess from literature values
    sme.teff = get_value(star, "t_eff", "K", alt=6000)
    sme.logg = get_value(star, "logg", 1, alt=4.4)
    monh = get_value(star, "metallicity", 1, alt=0)
    sme.abund = Abund(monh, "asplund2009")
    # There is no reference for these, use solar values instead
    sme.vmic = 1
    sme.vmac = 4
    sme.vsini = get_value(star, "velocity_rotation", "km/s", 4)

    # Load the linelist
    # and restrict the linelist to relevant lines
    sme.linelist = ValdFile(vald_file)
    # TODO: Why AIR? This will match Tanjas Linelist though
    # Is there a problem with the conversion?
    sme.linelist.medium = "air"
    wmin = sme.wran[segments[0]][0]
    wmax = sme.wran[segments[-1]][-1]
    sme.linelist = sme.linelist.trim(wmin, wmax, rvel=100)
    if target in linelist_cull.keys():
        sme.linelist = sme.linelist.cull_percentage(linelist_cull[target])
    # Set the atmosphere grid
    sme.atmo.source = "marcs2012.sav"
    sme.atmo.geom = "PP"
    sme.atmo.depth = "RHOX"
    sme.atmo.interp = "TAU"

    # Add NLTE corrections
    sme.nlte.set_nlte("Al", "nlte_Al_ama51_pysme.grd")
    sme.nlte.set_nlte("Ba", "nlte_Ba_ama51_pysme.grd")
    sme.nlte.set_nlte("Ca", "nlte_Ca_ama51_pysme.grd")
    sme.nlte.set_nlte("C", "nlte_C_ama51_pysme.grd")
    sme.nlte.set_nlte("H", "nlte_H_ama51_pysme.grd")
    sme.nlte.set_nlte("K", "nlte_K_ama51_pysme.grd")
    sme.nlte.set_nlte("Li", "nlte_Li_ama51_pysme.grd")
    sme.nlte.set_nlte("Mg", "nlte_Mg_ama51_pysme.grd")
    sme.nlte.set_nlte("Mn", "nlte_Mn_ama51_pysme.grd")
    sme.nlte.set_nlte("Na", "nlte_Na_ama51_pysme.grd")
    sme.nlte.set_nlte("N", "nlte_Na_ama51_pysme.grd")
    sme.nlte.set_nlte("O", "nlte_O_ama51_pysme.grd")
    sme.nlte.set_nlte("Si", "nlte_Si_ama51_pysme.grd")
    sme.nlte.set_nlte("Fe", "marcs2012_Fe2016.grd")

    # Set radial velocity and continuum settings
    # Set RV and Continuum flags
    ctype, cflag = cscale.rsplit("+", 1)
    sme.cscale_flag = cflag
    sme.cscale_type = ctype
    sme.cscale = None

    if vrad is None:
        sme.vrad_flag = "none"
        sme.vrad = None
    if isinstance(vrad, str):
        sme.vrad_flag = vrad
        sme.vrad = None
    else:
        sme.vrad_flag = "fix"
        sme.vrad = vrad

    # Harps instrumental broadening
    sme.iptype = "gauss"
    sme.ipres = 105_000

    # Save and Plot
    sme.save(mid_file)
    return sme


def fit(sme, target, segments="all", remove_outliers=False):
    examples_dir = dirname(realpath(__file__))

    # Define all parameters to be extra sure they are correct
    fitparameters = ["monh", "teff", "logg", "vmic", "vmac", "vsini"]
    # sme.vrad = None
    # sme.cscale = None

    # Mask outlier points
    if remove_outliers:
        sme = synthesize_spectrum(sme, segments=segments)
        resid = sme.synth[segments] - sme.spec[segments]
        mask = np.abs(resid) < 0.1
        mask &= sme.mask[segments] != 0
        for i, seg in enumerate(segments):
            sme.mask[seg] = np.where(mask[i], 1, 0)
        sme.vrad_flag = "fix"
        sme.cscale_flag = "fix"

    # Run least squares fit
    backup_fname = f"{target}_{'_'.join(fitparameters)}_bkp.sme"
    backup_fname = os.path.join(examples_dir, "results", backup_fname)
    sme = solve(sme, fitparameters, segments=segments, filename=backup_fname)

    # Save results
    fname = f"{target}_{'_'.join(fitparameters)}"
    out_file = os.path.join(examples_dir, "results", fname + "_fix2.sme")
    sme.save(out_file)

    # plot
    plot_file = os.path.join(examples_dir, "results", fname + "_fix2.html")
    fig = plot_plotly.FinalPlot(sme)
    fig.save(filename=plot_file, auto_open=False)

    print(f"Finished: {target}")
    return sme


if __name__ == "__main__":
    targets = [
        "AU_Mic",
        "Eps_Eri",
        "HN_Peg",
        "HD_102195",
        "HD_130322",
        "HD_179949",
        "HD_189733",
        "55_Cnc",
        "WASP-18",
        "GJ1214",
    ]
    # rv = {
    #     "AU_Mic": {"star": -51.9035, "tell": -56},
    #     "Eps_Eri": {"star": 66, "tell": -103},
    #     "HN_Peg": {"star": 0, "tell": -101},
    #     "HD_102195": {"star": 0, "tell": -100},
    #     "HD_130322": {"star": 0, "tell": -55},
    #     "HD_179949": {"star": 0, "tell": -103},
    #     "HD_189733": {"star": 0, "tell": -96},
    #     "55_Cnc": {"star": 0, "tell": -82},
    #     "WASP-18": {"star": 0, "tell": -98},
    # }
    # These areas contain bad pixels, that disturb our initial rough
    # continuum normalization, and are therefore removed even before that
    masked = {
        "AU_Mic": [
            (4982, 5527),
            (10561, 10962),
            (15063, 15287),
            (18559, 18925),
            (31888, 32002),
            (44415, 44478),
            (55757, 55892),
            (107806, 107983),
            (210728, 210797),
            (211327, 211393),
            (277889, 278216),
        ],
        "HN_Peg": [
            (128657, 128688),
            (191706, 191797),
            (216217, 216274),
            (230970, 231002),
            (284504, 284525),
        ],
        "HD_102195": [
            (172920, 172934),
            (204149, 204179),
            (217108, 217127),
            (246136, 246158),
            (270349, 270375),
            (275453, 275473),
            (284042, 284073),
            (300087, 300117),
        ],
        "HD_130322": [
            (99454, 99483),
            (155753, 155766),
            (167969, 167977),
            (174306, 174326),
            (186611, 186627),
            (195202, 195213),
            (201398, 201412),
            (227032, 227048),
            (244238, 244249),
            (244248, 244254),
            (250164, 250186),
            (250810, 250831),
            (282881, 282894),
            (283855, 283867),
            (293643, 293654),
            (295342, 295352),
        ],
        "HD_179949": [
            (67173, 67193),
            (87649, 87658),
            (186042, 186058),
            (223959, 223967),
            (228333, 228345),
            (272063, 272132),
            (276278, 276392),
        ],
        "HD_189733": [
            (103750, 103758),
            (107170, 107178),
            (110191, 110206),
            (111987, 112007),
            (186224, 186238),
            (206396, 206449),
            (234368, 234381),
            (236937, 236972),
            (249979, 249993),
            (256079, 256085),
            (263106, 263168),
        ],
        "55_Cnc": [(198466, 198469), (272134, 272144), (297364, 297371)],
        "WASP-18": [
            (21199, 21219),
            (57432, 57450),
            (138968, 138980),
            (151274, 151288),
            (156029, 156041),
            (168338, 168355),
            (196785, 196813),
            (200006, 200040),
            (205810, 205832),
            (208697, 208751),
            (219797, 219822),
            (225037, 225045),
            (225173, 225203),
            (226631, 226828),
            (244240, 244251),
            (247508, 247532),
            (272924, 272942),
            (274365, 274384),
        ],
        "GJ1214": [],
    }
    linelist = {
        "AU_Mic": "au_mic.lin",
        "GJ1214": "gj1214.lin",
        # "HN_Peg": "hn_peg.lin",
        # "Eps_Eri": "eps_eri.lin",
        # "HD_102195": "hd_102195.lin",
        # "HD_130322": "hd_130322.lin",
        # "HD_179949": "hd_179949.lin",
        # "HD_189733": "hd_189733.lin",
        # "55_Cnc": "55_cnc.lin",
        # "WASP-18": "wasp_18.lin",
    }
    linelist_cull = {"GJ1214": 50}
    cscale_type = {
        "AU_Mic": "matchlines+quadratic",
        "GJ1214": "matchlines+quadratic",
    }
    vrad_flag = {"AU_Mic": 51.9035}
    remove_outliers = {"AU_Mic": True}

    def parallel(target):
        print(f"Starting {target}")
        segments = range(6, 31)
        # segments = [9, 10]
        # segments = range(1, 6)

        # Start the logging to the file
        examples_dir = dirname(realpath(__file__))
        date_string = datetime.datetime.now().isoformat().replace(":", ".")
        log_file = os.path.join(examples_dir, f"logs/{target}_{date_string}.log")
        util.start_logging(log_file)

        # Create the first synthethic spectrum to use for manual masking
        mask = masked.get(target)
        ll = linelist.get(target, "harps.lin")
        cscale = cscale_type.get(target, "match+linear")
        vrad = vrad_flag.get(target, "whole")
        remove = remove_outliers.get(target, False)
        sme = init(
            target,
            mask=mask,
            linelist=ll,
            segments=segments,
            cscale=cscale,
            vrad=vrad,
        )

        # Finally fit it to the data
        sme = fit(
            sme,
            target,
            segments=segments,
            remove_outliers=remove,
        )
        return sme

    # Parse the cmd arguments
    target = sys.argv[1] if len(sys.argv) != 1 else "AU_Mic"

    parallel(target)
    pass
