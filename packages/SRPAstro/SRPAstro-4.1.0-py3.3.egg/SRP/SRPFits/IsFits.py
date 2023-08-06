""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 31/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (27/05/2010) First version.
        : (31/07/2015) python3 porting.
"""

import pyfits
from . import FitsConstants

def IsFits(fitsfile):
    try:
        hdr = pyfits.open(fitsfile)
    except IOError:
        return False
    hdr.close()
    return True
    

    
