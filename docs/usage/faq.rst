FAQ
===

* How do I change the default log file?
    Call util.start_logging(filename)

    >>> from SME import util
    >>> util.start_logging("your_log_file.log")

* I get an error "Derivatives in the starting point are not finite"
    Make sure your initial stellar parameters are within the
    atmosphere grid defined by the atmosphere file set in sme.atmo.source

* I get an error "lnGAS: DGESVX failed to solved for corrections the partial pressures."
    The most possible reason would be the abvundance of the element in error
    is too low or nan, thus the EOS code cannot compute its EOS. 
