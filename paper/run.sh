#!/bin/bash
# AU Mic
parallel --jobs 3 --bar --joblog parallel.log --header : --results . 'python HD_22049.py {}' ::: log Eps_Eri HN_Peg  HD_130322 HD_179949 HD_189733 55_Cnc WASP-18 HD_102195
