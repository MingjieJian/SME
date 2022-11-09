#!/bin/bash
parallel --jobs 2 --bar --joblog monte_carlo.log --header : --results . 'python monte_carlo_uncertainties.py {}' ::: SNR 50 100 150 200 ::: WRANGE 1 2 3 4
