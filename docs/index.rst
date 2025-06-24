PySME documentation
===================

More than two decades ago `Valenti & Piskunov (1996) <https://ui.adsabs.harvard.edu/abs/1996A&AS..118..595V>`_ developed SME – Spectroscopy Made Easy, a high-precision stellar-spectra synthesis/analysis engine that has powered hundreds of studies.
PySME is its modern Python front-end: a wrapper around the original C++/Fortran core that lets you (1) compute accurate, high-resolution synthetic spectra from a linelist + model atmosphere, (2) invert observed spectra to derive stellar parameters, and (3) explore NLTE corrections — all from an interactive notebook or scripted pipeline. The same capabilities make PySME invaluable for exoplanet work, where characterising the host star is essential for understanding its planets.

.. admonition:: Key features

   * Plane-parallel and spherical radiative-transfer engine  
   * LTE & 1-D NLTE line formation with pre-computed grids  
   * Automatic :math:`\chi^2` fitting for :math:`T_\mathrm{eff}`, :math:`\log{g}`, :math:`v_\mathrm{mic}`, [X/Fe] …  
   * Seamless use of ATLAS, MARCS, Phoenix and PINN model atmospheres and VALD line lists

.. note:: 

   * If you are new to PySME: follow the :ref:`usage/installation` and :ref:`usage/quickstart` to get started.
   * If you want to get familiar with PySME: read the :ref:`usage/sme_struct` for detail information on using PySME.
   * If you are familiar with PySME: check out the :ref:`usage/how-to.md` and :ref:`usage/changelog` to see the new functions.  

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Installation <usage/installation>
   usage/quickstart
   usage/sme_struct
   Large File Server <usage/lfs>
   PySME how to <usage/how-to>
   usage/faq
   usage/system_info
   usage/changes
   Changelog <usage/changelog>
   _sources/modules

Indices and tables
~~~~~~~~~~~~~~~~~~

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. rubric:: Quick links
:GitHub repository: https://github.com/MingjieJian/SME
:Issue tracker:     https://github.com/MingjieJian/SME/issues