# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 14:59:48 2022

@author: BEMC
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_SWAN import SWAN_read_tab
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot

path = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Westerschelde\tests\test_04_wind_perp'
output_path = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Westerschelde\tests\test_04_wind_perp'
files = list_files_folders.list_files('.TAB',path)

save_fig = True

Xp_comp= 165

for file in files:
    
    scene = file.split('\\')[-3]
    simulation = file.split('\\')[-2]
    
    data, headers = SWAN_read_tab.Freadtab(file)
    
    data['Hsig'][data['Hsig']<=0] = np.nan
    data['Hsig'][data['Hsig']==0] = np.nan
    data['Tm_10'][data['Tm_10']<=0] = np.nan
    data['TPsmoo'][data['TPsmoo']<=0] = np.nan
    data['Wlen'][data['Wlen']<=0] = np.nan
    data['Botlev'][data['Botlev']<-20] = -10
    Wlen = float(data['Lwavp'].iloc[-1])
    
    #%% Determine location toe of dike
    ii = 0
    slope = list()
    for x1, x2, y1, y2 in zip(data['Xp'][1:-1], data['Xp'][:-2], data['Botlev'][1:-1], data['Botlev'][:-2]):
        dx = x1 - x2
        dy = y1 - y2
        if dy == 0:
            dydx = 0
        else:
            dydx = dy/dx
            if dydx >= 0.10 and ii == 0:
                Xpteen = x1
                Ypteen = y2
                ii = ii +1
        slope.append(dydx)

    #%% Get output at uutput location (1/2 wavelength from toe of dike)
    Xpout = float(Xpteen) + Wlen*0.5
    Ypout = 0
    Hs_out = data['Hsig'][data['Xp'] > Xpout].iloc[0]
    Tm10_out = data['Tm_10'][data['Xp'] > Xpout].iloc[0]
    
    #%% get output at SWAN 2D location
    Hs_comp = data['Hsig'][data['Xp'] >= Xp_comp].iloc[0]
    Tm10_comp = data['Tm_10'][data['Xp'] >= Xp_comp].iloc[0]

    #%% plotting
    fig = plt.figure(figsize=(8,7))
    ax1 = plt.subplot(2,1,1)
    ax1_copy = ax1.twinx()
    
    ax1.plot(data['Xp'],-data['Botlev'],'k', linewidth = 1.5, label = 'bodem')
    ax1.plot(data['Xp'], data['Watlev'], 'b-', linewidth = 1.5, label = 'waterstand')
    ax1.axvline(x = Xpteen, color = 'k', linestyle='--', label = 'teen')
    ax1.axvline(x = Xpout, color = 'r', linestyle='--', label = 'teen + 1/2*L')
    ax1.axvline(x = Xp_comp, color = 'tab:orange', linestyle='--', label = 'HRbasis')
    ax1.set_ylabel('hoogte [m+NAP]')
    ax1.set_xlabel('afstand [m]')
    ax1.legend(loc = 'lower right')
    # ax1.set_xlim(30,100)
    # ax1.set_ylim(-20,10)

    ax1_copy.plot(data['Xp'], data['Hsig'],'g', linewidth = 3, label = '$H_s$ [m]')
    ax1_copy.set_ylabel('$H_s$ [m]',color='g')
    ax1_copy.tick_params(labelcolor='g')
    ax1_copy.text(Xpout+10,Hs_out,f'Hs = {Hs_out:.2f} m',color='r',fontweight = 'bold')
    ax1_copy.text(Xp_comp+10,Hs_comp,f'Hs = {Hs_comp:.2f} m',color='tab:orange',fontweight = 'bold')
    plt.title(f'{scene}\n{simulation}')
    ax1_copy.legend(loc = 'center right')
    # ax1_copy.set_ylim(0,4)
    
    ax2 = plt.subplot(2,1,2)
    ax2_copy = ax2.twinx()
    ax2.plot(data['Xp'],-data['Botlev'],'k', linewidth = 1.5, label = 'bodem')
    ax2.plot(data['Xp'], data['Watlev'], 'b-', linewidth = 1.5, label = 'waterstand')
    ax2.axvline(x = Xpteen, color = 'k', linestyle='--', label = 'teen')
    ax2.axvline(x = Xpout, color = 'r', linestyle='--', label = 'teen + 1/2*L')
    ax2.axvline(x = Xp_comp, color = 'tab:orange', linestyle='--', label = 'HRbasis')
    ax2.set_ylabel('hoogte [m+NAP]')
    ax2.set_xlabel('afstand [m]')
    ax2.legend(loc = 'lower right')
    # ax2.set_xlim(30,100)
    # ax2.set_ylim(-20,10)


    # ax2_copy.plot(data['Xp'], data['Tm_10'],color='orange')
    ax2_copy.plot(data['Xp'], data['Tm_10'],'g', linewidth = 3,label = '$T_m-1,0$ [m]')
    ax2_copy.set_ylabel('$H_s$ [m]',color='g')
    ax2_copy.tick_params(labelcolor='g')
    ax2_copy.text(Xpout+10,Tm10_out,f'Tm_10 = {Tm10_out:.2f} s',color='r',fontweight = 'bold')
    ax2_copy.text(Xp_comp+10,Tm10_comp,f'Tm_10 = {Tm10_comp:.2f} s',color='tab:orange',fontweight = 'bold')
    ax2_copy.set_ylabel('$T_{m-1.0}$ [s]')
    ax2_copy.legend(loc = 'center right')
    # ax2_copy.set_ylim(4,8)
       
    if save_fig:
        save_name = os.path.join(output_path, scene+'_'+simulation+'.png')
        save_plot.save_plot(fig,save_name,ax = ax1_copy, dx = -0.05)


