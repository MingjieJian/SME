.. _nlte:

NLTE
====

NLTE [#]_ calculations are important to accuarately fit certain lines.
PySME supports them using pre-computed grids of NLTE departure coefficients, which need to be created for
every element. For common elements PySME provides grids via the LFS
(see :ref:`lfs`). If any of these grids are used, please kindly take care to cite the papers describing the NLTE models
and departure coefficient calculations.

If you want to provide your own NLTE grid files, they should be present in `~/.sme/nlte_grids`.

NLTE calculations need to be specified for each element they are
supposed to be used for individually using 'sme.nlte.set_nlte(el, grid)'.
Similarly they can be disabled for each element using
'sme.nlte.remove_nlte(el)', where sme is your SME structure.
If no element is set to NLTE in the structure PySME will perform
LTE calculations only.

.. raw:: html

    <iframe src="../_static/nlte_table.html"
            width="100%" height="480"
            style="border:none;"></iframe>

Furthermore a long format linelist is required for NLTE calculations.
If only a short format has been given, then the calculations will
only be in LTE as well. (See :ref:`linelist`)

The NLTE object has the following fields

:elements: The elements for which NLTE has been activated
:grids: The grid file that is used for each active element
:subgrid_size:
    A small segment of the NLTE grid will be cached in memory
    to speed up calculations. This sets the size of that cache
    by defining the number of points in each
    axis (rabund, teff, logg, monh).
:flags: After the synthesis all lines are flaged if they used NLTE

.. [#] Non Local Thermal Equilibrium


Grid interpolation
------------------

The grid has 6 dimensions.

:teff: Effective Temperature
:logg: Surface Gravity
:monh: Overall Metallicity
:rabund: relative abundance of that element
:depth: optical depth in the atmosphere
:departure coefficients:
    The NLTE departure coefficients describing how much
    it varies from the LTE calculation

We then perform linear interpolation to the stellar parameters
we want to model. And we then perform a cubic spline fit to the depth scale
of the model atmosphere we specified (See :ref:`atmosphere`).

We then use the linelist to find only the relevant transitions in the grid,
and pass the departure coefficients for each line to the C library.
