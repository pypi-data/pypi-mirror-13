#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example python code to call the 2 mocks correlation function
routines from python. (The codes are written in C)

Author: Manodeep Sinha <manodeep@gmail.com>

Requires: numpy

"""
from __future__ import print_function
import os
import sys
import re
import time
import numpy as np
try:
    import pandas as pd
except ImportError:
    pd = None

from Corrfunc import _countpairs_mocks, rd


def main():

    tstart=time.time()
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../xi_mocks/tests/data/","Mr19_mock_northonly.rdcz.dat")


    ### The following section to figure out data-types seems to be no longer
    ### required. 


    ## Figure out the datatype, use the header file in the include directory
    ## because that is most likely correct (common.mk might have been modified
    ## but not recompiled)
    include_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "../include/", "countpairs_rp_pi_mocks.h")
    try:
        includes = rd(include_file)
    except (IOError, OSError) as e:
        print("ERROR: Could not find file {}.\nPlease compile the `Corrfunc' library directly before running python setup.py install".format(include_file))
        raise

    vector_type = re.search(r'(\w+)\s*\*\s*rupp\s*\;', includes, re.I).group(1)
    allowed_types = {"float":np.float32,"double":np.float}
    if vector_type not in list(allowed_types.keys()):
        raise TypeError("Error: Unknown precision={} found in header file {}. Allowed types are `{}'".format(vector_type,include_file,allowed_types))

    dtype = allowed_types[vector_type]
    dtype = np.float32
    ### Check if pandas is available - much faster to read in the data through pandas
    t0=time.time()
    print("Reading in the data...")
    try:
        if pd is not None:
            df  = pd.read_csv(file,header=None,engine="c",dtype={"x":dtype,"y":dtype,"z":dtype},delim_whitespace=True)
            ra  = np.asarray(df[0],dtype=dtype)
            dec = np.asarray(df[1],dtype=dtype)
            cz  = np.asarray(df[2],dtype=dtype)
        else:
            ra,dec,cz = np.genfromtxt(file,dtype=dtype,unpack=True)
    except:
        pass


    t1=time.time()    
    print("Done reading the data - time taken = {0:10.1f} seconds.\nBeginning Correlation functions calculations".format(t1-t0))


    nthreads=4
    pimax=40.0
    binfile=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../xi_mocks/tests/","bins")
    autocorr=1
    numbins_to_print=5
    cosmology=1

    print("RA min  = {:10.3f} max = {:10.3f}".format(np.min(ra),np.max(ra)))
    print("DEC min = {:10.3f} max = {:10.3f}".format(np.min(dec),np.max(dec)))
    print("cz min  = {:10.3f} max = {:10.3f}".format(np.min(cz),np.max(cz)))

    print("\nRunning 2-D correlation function xi(rp,pi)")
    results_DDrppi = _countpairs_mocks.countpairs_rp_pi_mocks(autocorr, cosmology,nthreads,pimax,binfile,ra,dec,cz,ra,dec,cz)
    print("\n#            ****** DD(rp,pi): first {} bins  *******      ".format(numbins_to_print))
    print("#      rmin        rmax       rpavg     pi_upper     npairs")
    print("###########################################################")
    for ibin in range(numbins_to_print):
        items = results_DDrppi[ibin]
        print("{0:12.4f} {1:12.4f} {2:10.4f} {3:10.1f} {4:10d}".format(items[0],items[1],items[2],items[3],items[4]))
    print("-----------------------------------------------------------")

    binfile=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../xi_mocks/tests/","angular_bins")
    print("\nRunning angular correlation function w(theta)")
    results_wtheta = _countpairs_mocks.countpairs_theta_mocks(autocorr, cosmology, nthreads, binfile, ra,dec, ra,dec)
    print("\n#         ******  wtheta: first {} bins  *******        ".format(numbins_to_print))
    print("#      thetamin        thetamax       thetaavg      npairs")
    print("##########################################################")
    for ibin in range(numbins_to_print):
        items = results_wtheta[ibin]
        print("{0:14.4f} {1:14.4f} {2:14.4f} {3:14d}".format(items[0],items[1],items[2],items[3]))
    print("-----------------------------------------------------------")

    print("Beginning the VPF")
    ## Max. sphere radius of 10 Mpc
    rmax=10.0
    ## 10 bins..so counts in spheres of radius 1, 2, 3, 4...10 Mpc spheres
    nbin=10
    num_spheres=10000
    num_pN=6
    threshold_neighbors=1 ## does not matter since we already have the centers
    volume=0.0 ## does not matter since we already have the centers
    centers_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../xi_mocks/tests/data/","Mr19_centers_xyz_forVPF_rmax_10Mpc.txt")
    Nran=num_spheres ## set it so that the code runs the loop
    results_vpf = _countpairs_mocks.countspheres_vpf_mocks(rmax,nbin,num_spheres,num_pN,threshold_neighbors,centers_file,cosmology,ra,dec,cz,ra,dec,cz)
    print("\n#            ******    pN: first {} bins  *******         ".format(numbins_to_print))
    print('#       r    ',end="")

    for ipn in range(num_pN):
        print('        p{:0d}      '.format(ipn),end="")

    print("")

    print("###########",end="")
    for ipn in range(num_pN):
        print('################',end="")
    print("")


    for ibin in range(numbins_to_print):
        items = results_vpf[ibin]
        print('{0:10.2f} '.format(items[0]),end="")
        for ipn in range(num_pN):
            print(' {0:15.4e}'.format(items[ipn+1]),end="")
        print("")

    print("-----------------------------------------------------------")
    print("Done with the VPF.")
    tend=time.time()
    print("Done with all the MOCK clustering calculations. Total time taken = {:0.2f} seconds.".format(tend-tstart))


if __name__ == "__main__":
    main()

