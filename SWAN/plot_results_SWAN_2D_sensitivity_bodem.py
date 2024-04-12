# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 14:25:16 2022

@author: ENGT2
"""

#%% import

import os
#import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot, create_colormap
import datetime
from hmtoolbox.WB_basic import deg2uv
import scipy.io
from mpl_toolkits.axes_grid1 import make_axes_locatable
import gc

#%% settings

test = 'refractie'

save_switch = True

figsize = (8,4)

if test == 'bodem':
    #bodem
    #referentie (_01)
    path_main_G1_01 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G1_01'
    path_main_G2_01 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G2_01'
    
    #bodem (_02)
    path_main_G1_02 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G1_02'
    path_main_G2_02 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G2_02'
    output_path = r'z:\130991_Systeemanalyse_ZSS\5.Results\SWAN\sensitivity\bodem'

if test == 'refractie':
    #refractie
    #referentie (_01), note that G1_01 still reads the _02 bottoms, mail Tim 30-9-2022
    path_main_G1_01 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G1_02'
    path_main_G2_01 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G2_02'
    
    #refractie (_02), note that the refractie simulations were performed with 01 bottom, naming of folder is not correct
    path_main_G1_02 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\02_refractie\G1_01'
    path_main_G2_02 = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\02_refractie\G2_01'
    output_path = r'z:\130991_Systeemanalyse_ZSS\5.Results\SWAN\sensitivity\refractie'

#%% get directions with output data

dirs_G1_01 = list_files_folders.list_files('.mat',path_main_G1_01, endswith = True)
dirs_G2_01 = list_files_folders.list_files('.mat',path_main_G2_01, endswith = True)

dirs_G1_02 = list_files_folders.list_files('.mat',path_main_G1_02, endswith = True)
dirs_G2_02 = list_files_folders.list_files('.mat',path_main_G2_02, endswith = True)

if len(dirs_G1_01) == len(dirs_G2_01) == len(dirs_G1_02) == len(dirs_G2_02):
    print('== list of dirs for G1 is the same length as for G2 and bottoms')
else:
    print('== list of dirs for G1 is not the same length as for G2!')

vmin = -0.5
vmax = 0.5
cmap = create_colormap.diff_colormap(vmin,vmax,0.05,0.01)

#%% loop over directions and plot output
    
for d in range(len(dirs_G1_01)):
    
    run_id = dirs_G1_01[d].split('\\')[-3]
    
    #check if we have the same run ID
    if dirs_G1_01[d].split('\\')[-3] != dirs_G2_01[d].split('\\')[-3] != dirs_G1_02[d].split('\\')[-3] != dirs_G2_02[d].split('\\')[-3]:
        print('error check run IDs')
        break
    else:
        print(f'processing run: {run_id}')        
    #%% Read G1 and G2 output
    mat_G1_01 = dict(scipy.io.loadmat(dirs_G1_01[d]))
    mat_G2_01 = dict(scipy.io.loadmat(dirs_G2_01[d]))
    
    mat_G1_02 = dict(scipy.io.loadmat(dirs_G1_02[d]))
    mat_G2_02 = dict(scipy.io.loadmat(dirs_G2_02[d]))
    
    # Read Xp Yp
    Xp_G1 = mat_G1_01['Xp'][:,:]
    Yp_G1 = mat_G1_01['Yp'][:,:]
                    
    Xp_G2 = mat_G2_01['Xp'][:,:]
    Yp_G2 = mat_G2_01['Yp'][:,:]
    
    Hsig_G1_01 = mat_G1_01['Hsig'][:,:]
    Hsig_G2_01 = mat_G2_01['Hsig'][:,:]
    Hsig_G1_02 = mat_G1_02['Hsig'][:,:]
    Hsig_G2_02 = mat_G2_02['Hsig'][:,:]
            
    delta_Hsig_G1 = Hsig_G1_01-Hsig_G1_02
    delta_Hsig_G2 = Hsig_G2_01-Hsig_G2_02
    #%% Plot results
    fig = plt.figure(figsize=figsize)

    # Hsig
    plt.gca().set_aspect('equal')
    pcol = plt.pcolor(Xp_G1,Yp_G1,delta_Hsig_G1,cmap=cmap.cmap,vmin=vmin,vmax=vmax)
    vmin, vmax = plt.gci().get_clim()
    pcol = plt.pcolor(Xp_G2,Yp_G2,delta_Hsig_G2,cmap=cmap.cmap,vmin=vmin,vmax=vmax)
    pcol = plt.pcolor(Xp_G2,Yp_G2,delta_Hsig_G2,cmap=cmap.cmap,vmin=vmin,vmax=vmax)
    plt.xlabel('x-coordinate [m]')
    plt.ylabel('y-coordinate [m]')
    
    plt.xlim(np.nanmin(Xp_G1)-3e3,np.nanmax(Xp_G1)+3e3)
    plt.ylim(np.nanmin(Yp_G1)-3e3,np.nanmax(Yp_G1)+3e3)
    plt.grid(visible=True, which='major', axis='both')
    
    plt.colorbar(pcol)
    plt.ylabel('$\delta$Hsig (m)')
    
    plt.title(run_id)
            
    #%% Save figure
    if save_switch:
        save_name = os.path.join(output_path, f'delta_Hsig_G1_G2_{run_id}.png')
        save_plot.save_plot(fig, save_name, incl_wibo = False, dpi = 300, 
                  change_size = True, figwidth = 8, figheight = 4)
    plt.close('all')
    del fig
    print('End at {} doing stuff'.format(datetime.datetime.now()))
    gc.collect()