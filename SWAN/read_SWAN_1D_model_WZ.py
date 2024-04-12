# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 14:59:48 2022

@author: BEMC
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_SWAN import SWAN_read_tab
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot

# results SWAN 1D
path_results_1D = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\test_04_veg_layers'
files = list_files_folders.list_files('.TAB',path_results_1D)

# input SWAN 1D
path_input = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\test_04_veg_layers\input'
file_input = r'SWAN2D_output_WZ_6004026_HRext03.csv'

# results SWAN 2D
path_results_2D = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\test_04_veg_layers\input'
file_output_2D = 'output_batch_03_1D_input_6004026_HRext02.xlsx'

# output path 
output_path = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\test_04_veg_layers'

save_fig = True

Xp_comp= 343
Xpteen = 43
Xp_basis = 99.8

#%% load file with simulation input

df_input = pd.read_csv(os.path.join(path_input, file_input), sep=';',dtype={'ZSS-scenario':str})

# df_swan2d = pd.read_csv(os.path.join(path_results_2D, file_output_2D), sep=';',dtype={'ZSS-scenario':str})

#%% loop trough simulations and plot results

for file in files:
    
    scene = file.split('\\')[-3]
    simulation = file.split('\\')[-2]
    
    Hs_ref = df_input[df_input['Scenario']==scene]['HS'].iloc[0]
    Tp_ref = df_input[df_input['Scenario']==scene]['TP'].iloc[0]

    data, headers = SWAN_read_tab.Freadtab(file)
    
    data['Hsig'][data['Hsig']<=0] = np.nan
    data['Hsig'][data['Hsig']==0] = np.nan
    data['Tm_10'][data['Tm_10']<=0] = np.nan
    data['TPsmoo'][data['TPsmoo']<=0] = np.nan
    data['Wlen'][data['Wlen']<=0] = np.nan
    data['Botlev'][data['Botlev']<-20] = -10
    Wlen = float(data['Lwavp'].iloc[-1])
    
    #%% Determine location toe of dike
    # ii = 0
    # slope = list()
    # Xpteen = data['Xp'].iloc[-1]
    # Ypteen = data['Yp'].iloc[-1]
    # for x1, x2, y1, y2 in zip(data['Xp'][1:-1], data['Xp'][:-2], data['Botlev'][1:-1], data['Botlev'][:-2]):
    #     dx = x1 - x2
    #     dy = y1 - y2
    #     if dy == 0:
    #         dydx = 0
    #     else:
    #         dydx = dy/dx
    #         if dydx >= 1/60 and ii == 0:
    #             Xpteen = x1
    #             Ypteen = y2
    #             ii = ii +1             
    #     slope.append(dydx)

    # # max_slope = max(slope)
    # # imax = np.argmax(slope)
    
    Xpteen = Xpteen

    #%% wave parameters at incoming boundary
    Xpin = data['Xp'].iloc[-1]
    Hs_in = data['Hsig'].iloc[-1]
    Tm10_in = data['Tm_10'].iloc[-1]

    #%% Get output at output location (1/2 wavelength from toe of dike)
    Xpout = float(Xpteen) + Wlen*0.5
    Ypout = 0
    Hs_out = data['Hsig'][data['Xp'] > Xpout].iloc[0]
    Tm10_out = data['Tm_10'][data['Xp'] > Xpout].iloc[0]
    
    # maximum values for ylimits
    Hs_max = max(data['Hsig'])
    Tm10_max = max(data['Tm_10'])
    
    #%% get output at SWAN 2D location
    Hs_comp = data['Hsig'][data['Xp'] >= Xp_comp].iloc[0]
    Tm10_comp = data['Tm_10'][data['Xp'] >= Xp_comp].iloc[0]

    #%% plotting
    fig = plt.figure(figsize=(8,7))
    ax1 = plt.subplot(2,1,1)
    ax1_copy = ax1.twinx()
    
    ax1.plot(data['Xp'],-data['Botlev'],'k', linewidth = 3, label = 'bodem')
    ax1.plot(data['Xp'], data['Watlev'], 'b-', linewidth = 1.5, label = 'waterstand')
    ax1.axvline(x = Xpteen, color = 'k', linestyle='--', label = 'teen')
    ax1.axvline(x = Xpout, color = 'r', linestyle='--', label = 'teen + 1/2*L')
    ax1.axvline(x = Xp_comp, color = 'tab:orange', linestyle='--', label = 'teen + 300m')
    ax1.axvline(x = Xp_basis, color = 'y', linestyle='--', label = 'HRbasis')
    ax1.set_ylabel('hoogte [m+NAP]')
    ax1.set_xlabel('afstand [m]')
    ax1.legend(loc = 'lower right')
    # ax1.set_xlim(30,100)
    # ax1.set_ylim(-20,10)

    ax1_copy.plot(data['Xp'], data['Hsig'],'g', linewidth = 1.5, label = '$H_s$ [m]')
    ax1_copy.set_ylabel('$H_s$ [m]',color='g')
    ax1_copy.tick_params(labelcolor='g')
    ax1_copy.text(Xpin,Hs_in,f'Hs = {Hs_in:.2f} m',color='g',fontweight = 'bold')
    ax1_copy.text(Xpout+10,Hs_out,f'Hs = {Hs_out:.2f} m',color='r',fontweight = 'bold')
    ax1_copy.text(Xp_comp+10,Hs_comp,f'Hs = {Hs_comp:.2f} m',color='tab:orange',fontweight = 'bold')
    plt.title(f'{scene}\n{simulation}\n Hs = {Hs_ref:.2f} m, Tp = {Tp_ref:.2f} s')
    ax1_copy.legend(loc = 'center right')
    ax1_copy.set_ylim(0,np.ceil(Hs_max))
    
    ax2 = plt.subplot(2,1,2)
    ax2_copy = ax2.twinx()
    ax2.plot(data['Xp'],-data['Botlev'],'k', linewidth = 3, label = 'bodem')
    ax2.plot(data['Xp'], data['Watlev'], 'b-', linewidth = 1.5, label = 'waterstand')
    ax2.axvline(x = Xpteen, color = 'k', linestyle='--', label = 'teen')
    ax2.axvline(x = Xpout, color = 'r', linestyle='--', label = 'teen + 1/2*L')
    ax2.axvline(x = Xp_comp, color = 'tab:orange', linestyle='--', label = 'teen + 300m')
    ax2.axvline(x = Xp_basis, color = 'y', linestyle='--', label = 'HRbasis')
    ax2.set_ylabel('hoogte [m+NAP]')
    ax2.set_xlabel('afstand [m]')
    ax2.legend(loc = 'lower right')
    # ax2.set_xlim(30,100)
    # ax2.set_ylim(-20,10)

    # ax2_copy.plot(data['Xp'], data['Tm_10'],color='orange')
    ax2_copy.plot(data['Xp'], data['Tm_10'],'m', linewidth = 1.5,label = '$T_m-1,0$ [m]')
    ax2_copy.set_ylabel('$H_s$ [m]',color='m')
    ax2_copy.tick_params(labelcolor='m')
    ax2_copy.text(Xpin,Tm10_in,f'Tm_10 = {Tm10_in:.2f} s',color='m',fontweight = 'bold')
    ax2_copy.text(Xpout+10,Tm10_out,f'Tm_10 = {Tm10_out:.2f} s',color='r',fontweight = 'bold')
    ax2_copy.text(Xp_comp+10,Tm10_comp,f'Tm_10 = {Tm10_comp:.2f} s',color='tab:orange',fontweight = 'bold')
    ax2_copy.set_ylabel('$T_{m-1.0}$ [s]')
    ax2_copy.legend(loc = 'center right')
    ax2_copy.set_ylim(0,np.ceil(Tm10_max))
       
    if save_fig:
        save_name = os.path.join(output_path, scene+'_'+simulation+'.png')
        save_plot.save_plot(fig,save_name,ax = ax1_copy, dx = -0.05)