.. _linelist:

Linelist
========

The linelist is an important part of every synthetic spectrum,
since it includes all information that is line specific.

Line format
-----------

PySME knows to types of linelists. A short format, and a long format.
The difference between the two is the amount of information contained therein.
The short format contains only enough parameters for LTE calculations,
while the long format is required for NLTE calculations.

Line parameters
---------------

The short format fields are

:species:
    A string identifier including the element
    and ionization state or the molecule
:atom number:
    Identifies the species by the atomic number
    (i.e. the number of protons)
:ionization: The ionization state of the species, where 1 is neutral (?)
:wlcent: The central wavelength of the line in Angstrom
:excit: The excitation energy in ?
:gflog:
    The log of the product of the statistical weight of
    the lower level and the oscillator strength for the transition.
:gamrad: The radiation broadening parameter
:gamqst: A broadening parameter
:gamvw: van der Waals broadening parameter
:lande: The lande factor
:depth: An arbitrary depth estimation of the line
:reference: A citation where this data came from

In addition the long format has the following fields

:lande_lower: The lower Lande factor
:lande_upper: The upper Lande factor
:j_lo: The spin of the lower level
:j_up: The spin of the upper level
:e_upp: The energy of the upper level
:term_lower: The electron configuration of the lower level
:term_upper: The electron configuration of the upper level
:error: An uncertainty estimate for this linedata

Important Note
--------------
As far as the radiative transfer code is concerned the ionization is defined as part of the species term.
I.e. a line with species = "Fe 2" will be calculated as ionization = 2.
If no number is set within the species field, SME will use an ionization of 1.

Also atom_number is ignored in the radiative transfer calculations and therefore does not need to be set.

VALD integration
----------------

PySME is designed to be used in combination with
VALD3 (https://vald.astro.uu.se/). The easiest way to
get a linelist into PySME is therefore to use VALD
extract stellar, as that can be directly imported
using the ValdFile class.
