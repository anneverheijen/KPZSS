# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts computes Hs, Tp and Dir offshore based on windspeed and wind direction, using linear inter/extrapolation.

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 

--- Version --- 
Created on Tue Aug  9 08:43:31 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: interp_offshore_waves.py

--- Revision --- 
Status: Unverified 

Witteveen+Bos Consulting Engineers 
Leeuwenbrug 8
P.O. box 233 
7411 TJ Deventer
The Netherlands 
		
"""

import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
from hmtoolbox.WB_basic import save_plot

def interp_offshore_waves(df_offshore, windrichting, windsnelheid, savename):
    '''
    function to obtain offshore waves
    using both interpolation and extrapolation

    Parameters
    ----------
    df_offshore : Dataframe
        Transformation matrix with the following parameters:
            Windrichting
            Golfperiode Tp
            Golfhoogte
    windrichting : float
        wind direction for which offshore wave conditions need to be determined
        assumption is that wave and wind direction are equal
    windsnelheid : float
        wind speed for which offshore wave conditions need to be determined
    savename : string
        DESCRIPTION.

    Returns
    -------
    Hs : interpolated or extrapolated wave height
    Tp : interpolated or extrapolated wave period

    '''
    # select directions
    df_golfrand_richting_selected = df_offshore[df_offshore['Windrichting'] == windrichting].reset_index()

    # perform interpolation and allow for extrapolation
    Hs = interpolate.interp1d(df_golfrand_richting_selected['Windsnelheid'].values, 
               df_golfrand_richting_selected['Golfhoogte'].values,fill_value='extrapolate')(windsnelheid)
    
    Tp = interpolate.interp1d(df_golfrand_richting_selected['Windsnelheid'].values, 
               df_golfrand_richting_selected['Golfperiode Tp'].values,fill_value='extrapolate')(windsnelheid)
    
    # print some data
    if windsnelheid > np.max(df_golfrand_richting_selected['Windsnelheid'].values):
        print(f'we extrapolated the windsnelheid of {windsnelheid:.2f} with richting of {windrichting:.2f}, resulting Hs {Hs:.2f} m and Tp {Tp:.2f} s')
    else:
        print(f'we interpolated the windsnelheid of {windsnelheid:.2f} with richting of {windrichting:.2f}, resulting Hs {Hs:.2f} m and Tp {Tp:.2f} s')
    
    # plot
    fig = plt.figure()
    plt.scatter(df_offshore['Golfperiode Tp'],df_offshore['Golfhoogte'],
                label='Alle windrichtingen')
    plt.scatter(df_golfrand_richting_selected['Golfperiode Tp'], df_golfrand_richting_selected['Golfhoogte'].values,
                label="Windrichting = %d graden" % windrichting)
    plt.scatter(Tp,Hs, c='red',label='Inter/extrapolatie')
    plt.text(Tp,Hs,"Hs = %.2f m, Tp = %.2f s" % (Hs, Tp))
    plt.legend()
    plt.title("Windrichting = %d graden, Windsnelheid = %.1f m/s\n" % (windrichting, windsnelheid))
    plt.xlabel('Golfperiode Tp (s)')
    plt.ylabel('Golfhoogte Hm0 (m)')
    plt.show()
    save_plot.save_plot(fig, savename)

    return float(Hs), float(Tp), fig