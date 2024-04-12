# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 14:31:45 2018

@author: vuik/dupuits
"""

from collections import namedtuple
import numpy as np


def overtopping(Hm0, Tm, slope, Rc, **kwargs):
    """
    required input:
        Hm0   : significant wave height (m)
        Tm    : spectral mean wave period Tm-1,0 (s)
        slope : characteristic outer slope angle of dike slope=tan(alpha)
        Rc    : relative freeboard (with respect to MWL) (m)
    optional input:
        yb    : reduction factor for presence of berm
        yf    : reduction factor for roughness
        betaw : angle of oblique incidence (degrees)
        yv    : reduction factor for effect of wave wall
        ctype : probabilic ('prob') or deterministic ('det')
        ed    : edition of EurOtop: 2007 or 2016
        C**   : parameters for overtopping formulas, depending on ctype and ed.
                A default value is used if C**=0 or not set at all.
    output:
        q     : average overtopping discharge (m3/s/m)
    """

    if Hm0.shape != Tm.shape or Hm0.shape != slope.shape or Hm0.shape != Rc.shape:
        raise ValueError('Hm0, Tm, slope and/or Rc do not have the same array shape')

    # Default values
    yb    = kwargs.get("yb",    np.ones(Hm0.shape))
    yf    = kwargs.get("yf",    np.ones(Hm0.shape))
    betaw = kwargs.get("betaw", np.zeros(Hm0.shape))
    yv    = kwargs.get("yv",    np.ones(Hm0.shape))
    ctype = kwargs.get("ctype", "prob")
    ed    = kwargs.get("ed",    2016)
    g     = kwargs.get("g",     9.81)
    debug = kwargs.get("debug", False)

    if ed not in [2007, 2016] or ctype not in ["prob", "det"]:
        raise ValueError("Unrecognized value for 'ed'.")

    # Default values for overtopping constants.
    parnames = ["C1a", "C1b", "C1c", "C2a", "C2b", "C2c", "C3a", "C3b", "C3c"]
    if ed == 2007 and ctype == "prob":
        par = dict(zip(parnames, [0.067, 4.75, 1.0, 0.20,   2.60, 1.0, -0.92, 0.33, 0.022]))
    if ed == 2007 and ctype == "det":
        par = dict(zip(parnames, [0.067, 4.30, 1.0, 0.20,   2.30, 1.0, -0.68, 0.33, 0.022]))
    if ed == 2016 and ctype == "prob":
        par = dict(zip(parnames, [0.023, 2.70, 1.3, 0.09,   1.50, 1.3, -0.79, 0.33, 0.022]))
    if ed == 2016 and ctype == "det":
        par = dict(zip(parnames, [0.026, 2.50, 1.3, 0.1035, 1.35, 1.3,  0.50, 0.33, 0.022]))

    # Check if any of the overtopping constants needs to be overwritten.
    for key, value in kwargs.items():
        if key in parnames and value != 0.0:
            par[key] = value

    # Convert to a namedtuple because:
    #  - Makes it less painful to look at long formulas (use of dot operator).
    #  - Raises an error if code tries to alter a value of the namedtuple.
    OvertoppingConstants = namedtuple("OvertoppingConstants", parnames)
    par = OvertoppingConstants(**par)

    # Create copies of the input
    Hm0 = Hm0.copy()
    Tm = Tm.copy()
    slope = slope.copy()
    Rc = Rc.copy()

    # Create empty arrays to fill later
    q1 = np.empty(Hm0.shape)
    q2 = np.empty(Hm0.shape)
    q3 = np.empty(Hm0.shape)
    zeta = np.empty(Hm0.shape)
    q = np.empty(Hm0.shape)

    # Special case for negative freeboard
    rc_neg = Rc < 0
    rc_pos = Rc >= 0
    if ed == 2007:
        q[rc_neg] = 0.60 * np.sqrt(g * np.abs(Rc[rc_neg])**3)
    elif ed == 2016:
        q[rc_neg] = 0.54 * np.sqrt(g * np.abs(Rc[rc_neg])**3)

    # Negative or NaN results in NaN
    hm0_neg = (Hm0 < 0) | (Tm < 0) | np.isnan(Hm0) | np.isnan(Tm)
    q[rc_pos & hm0_neg] = np.nan

    # Zero wave height or period is zero discharge
    hm0_zer = ((Hm0 == 0) & (Tm >= 0)) | ((Tm == 0) & (Hm0 >= 0))
    q[rc_pos & hm0_zer] = 0.0

    # Valid indices for non-negative freeboards and positive waveheight/periods
    valid_ind = rc_pos & (Hm0 > 0) & (Tm > 0)

    # Fix betaw to be between 0 and 180, and derive gamma beta
    if betaw > 180:
        betaw = 360-betaw

    ybeta = np.ones(Hm0.shape) * 0.736
    
    if betaw <= 80:
        ybeta = 1.0 - 0.0033 * betaw # still valid in 2016, Eq. 5.29

    # Zero overtopping discharge for waves not attacking the profile
    q[valid_ind & (betaw > 110)] = 0.0
    valid_ind = valid_ind & (betaw <= 110)

    # Reduce wave height and periods for very oblique waves
    if valid_ind & (betaw > 80):
        Hm0 = Hm0 * (110.0 - betaw) / 30.0
        Tm  = Tm * np.sqrt((110.0 - betaw) / 30.0)

    # Reduce variables to the valid indices, makes the calculations for
    # q1, q2 and q3 more readable
    Hm0 = Hm0[valid_ind]
    Tm = Tm[valid_ind]
    Rc = Rc[valid_ind]
    slope = slope[valid_ind]
    ybeta = ybeta
    yb = yb
    yf = yf
    yv = yv
    # Calculate L0, sm and zeta
    L0    = g * Tm**2 / 2.0 / np.pi
    sm    = Hm0 / L0
    zeta[valid_ind]  = slope / np.sqrt(sm)
    q1[valid_ind] = par.C1a / np.sqrt(slope) * np.sqrt(g * Hm0**3) * yb * zeta[valid_ind]
    q1[valid_ind] *= np.exp(-(par.C1b * Rc / (zeta[valid_ind] * Hm0 * yb * yf * ybeta * yv))**par.C1c)

    q2[valid_ind] = par.C2a * np.sqrt(g * Hm0**3)
    q2[valid_ind] *= np.exp(-(par.C2b * Rc / (Hm0 * yf * ybeta))**par.C2c)

    q3[valid_ind] = 10.0**par.C3a * np.sqrt(g * Hm0**3)
    q3[valid_ind] *= np.exp(-Rc / (yf * ybeta * Hm0 * (par.C3b + par.C3c * zeta[valid_ind])))

    # Zeta conditionals
    zeta_smal = valid_ind & (zeta < 5)
    q[zeta_smal] = np.minimum(q1[zeta_smal], q2[zeta_smal])

    zeta_larg = valid_ind & (zeta > 7)
    q[zeta_larg] = q3[zeta_larg]

    zeta_between = valid_ind & (zeta <= 7) & (zeta >= 5)
    lb = np.minimum(q1[zeta_between], q2[zeta_between])
    q[zeta_between] = (zeta[zeta_between] - 5.0) / (7.0 - 5.0) * (q3[zeta_between] - lb) + lb

    return q

if __name__ == '__main__':  
    # fill in function which corresponds to results of JORL2
    Hm0 = 4.07 # m
    Tm = 8.11 # s Tm-1,0 (s)
    slope = 0.25 # mTAW
    Rc = 1.09
    betaw = 0.0
    
    yb = 0.8
    yf = 0.9
    yv = 0.7
    
    q = overtopping(np.array(Hm0),np.array(Tm),np.array(slope),np.array(Rc), 
                    betaw = betaw, yf = yf, yb = yb, yv = yv, 
                    ed = 2007, ctype = 'det')

    print(q*1000) # result JORL2 sheet = 561.2 l/s/m