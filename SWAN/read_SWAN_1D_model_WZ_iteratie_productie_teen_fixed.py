# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts does the following things:
    - reads output of SWAN1D simulations for Waddenzee
    - calculates differences between SWAN1D and SWAN2D outputat location 300m from dyke
    - changes boundary conditions of SWAN1D run based on difference at 300m location
    - generates input for new SWAN1D run
    - plots results of SWAN 1D run

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 

--- Version --- 
Created on Thu Sep 29 09:17:28 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: read_SWAN_1D_model_WZ_iteratie_productie.py 

--- Revision --- 
Status: Unverified 

Witteveen+Bos Consulting Engineers 
Leeuwenbrug 8
P.O. box 233 
7411 TJ Deventer
The Netherlands 
		
"""

#%% Import modules

import os
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_SWAN import SWAN_read_tab
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot
import shutil
# %pylab qt
import gc

#%% Settings

# main
path_main = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\iter_02'
path_results_1D = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\iter_02'
path_profile_info = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\_bodem\profile_info_SWAN1D_WZ_xteen.xlsx'

tab_files = list_files_folders.list_files('.TAB',path_results_1D)

# input SWAN 1D
path_input = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\iter_01\input'
file_input = r'output_productie_SWAN2D_WZ_v3.xlsx'

# shapefile with okader vak info (including boolean with harbour or 1D)
path_shape_vakken   = r'z:\130991_Systeemanalyse_ZSS\2.Data\GIS_TEMP\okader_fc_hydra_unique_handedit_WZ_v3_coords.shp'

save_fig = True

new_iteration = True

save_result = True

final_iteration = False

# path with new iteration
path_new = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\iter_03'

Xp_300 = 300

#%% Load tab_file with simulation input

# Output at locations 'HRext01' (see .swan-file)
outloc = 'HRext01_300m'

xl_input  = pd.ExcelFile(os.path.join(path_input, file_input),engine='openpyxl')
df_input = xl_input.parse(sheet_name = outloc)

# Output at locations 'HRbasis' (see .swan-file)
outloc = 'HRbasis'

xl_basis  = pd.ExcelFile(os.path.join(path_input, file_input),engine='openpyxl')
df_basis = xl_basis.parse(sheet_name = outloc)

# Excel with info on 1D profiles (orientation)
xl_profile  = pd.ExcelFile(path_profile_info,engine='openpyxl')
df_profile  = xl_profile.parse()

# info on which output to use for each okader vak
df_vakken = gp.read_file(path_shape_vakken)

#%% loop trough SWAN1D simulations, plot results, prepare input for new simulations (new iteration)

appended_output = []

for tab_file in tab_files:
    
    # get relevant names from filename
    scene = tab_file.split('\\')[-3]
    simulation = tab_file.split('\\')[-2]
    loc = simulation.split('_')[0][2:]
    
    # output path 
    output_path = os.path.join(path_main,scene)
    
    # OKADEr vak info
    info_vak        = df_vakken[df_vakken['VakId']==loc]
    # get criteria from shapefile (to use SWAN 1D result or to use Hs/D)
    switch_1d       = info_vak['1D'].iloc[0]
    switch_haven    = info_vak['Haven'].iloc[0]
    
    # find matching boundary conditions for run
    match = (df_input['Scenario']==scene) & (df_input['OkaderId']==int(loc))
    if match.any(axis=0) == False:
        print('Warning: no matching ID found in SWAN2D output')
        break
    # get SWAN2D output at location 300m from dyke
    Hs_300_2d = df_input[match]['Hsig'].iloc[0]
    Tp_300_2d = df_input[match]['TPsmoo'].iloc[0]
    Tm10_300_2d = df_input[match]['Tm_10'].iloc[0]
    Dir_300_2d = df_input[match]['Dir'].iloc[0]
    
    # find SWAN 2D output at HRbasis for matching run
    match2 = (df_basis['Scenario']==scene) & (df_basis['OkaderId']==int(loc))
    if match2.any(axis=0) == False:
        print('Warning: no matching ID found in SWAN2D output')
        break
    Hs_basis = df_basis[match2]['Hsig'].iloc[0]
    Tp_basis = df_basis[match2]['TPsmoo'].iloc[0]
    Tm10_basis = df_basis[match2]['Tm_10'].iloc[0]
    Dir_basis = df_basis[match2]['Tm_10'].iloc[0]

    data, headers = SWAN_read_tab.Freadtab(tab_file)
    
    data['Hsig'][data['Hsig']<=0] = np.nan
    data['Hsig'][data['Hsig']==0] = np.nan
    data['Tm_10'][data['Tm_10']<=0] = np.nan
    data['TPsmoo'][data['TPsmoo']<=0] = np.nan
    data['Wlen'][data['Wlen']<=0] = np.nan
    data['Botlev'][data['Botlev']<-20] = -10
    Wlen = float(data['Lwavp'].iloc[-1])
    

    #%% Get location of teen from file
    
    Xpteen = df_profile['Xp_teen'].loc[(df_profile['OkaderId']==float(loc)) & (df_profile['Scenario'] == 'WZ_NM_01_000_RF')]
    Xpteen = float(Xpteen)
    print(Xpteen)
       
    #%% Wave parameters at incoming boundary
    
    Xpin = data['Xp'].iloc[-1]
    Hs_in = data['Hsig'].iloc[-1]
    Tp_in = data['TPsmoo'].iloc[-1]
    Tm10_in = data['Tm_10'].iloc[-1]

    #%% Get output at output location (1/2 wavelength from toe of dike)
    
    Xpout = float(Xpteen) + Wlen*0.5
    Ypout = 0
    Dep_out = data['Depth'][data['Xp'] >= Xpout].iloc[0]
    Hs_out = data['Hsig'][data['Xp'] >= Xpout].iloc[0]
    Tp_out = data['TPsmoo'][data['Xp'] >= Xpout].iloc[0]
    Tm10_out = data['Tm_10'][data['Xp'] >= Xpout].iloc[0]
    Dir_out_rel = data['Dir'][data['Xp'] >= Xpout].iloc[0]
    
    #%% Calculate wave direction (nautical convention)
    # The 1D profiles in SWAN are all oriëntated from West to East (so along x-axis, 90 degrees nautical)
    # The wave direction in the SWAN1D output is with respect to the West-East profile
    # To determine absolute wave directoin (nautical) the wave direction from SWAN needs to be corrected
    
    # Read oriëntation of 1D profile
    Dir_profile = df_profile[df_profile['OkaderId']==int(loc)]['dir_profile'].iloc[0]
    # Determine absolute wave direction (nautical convention)
    Dir_out_abs = Dir_profile + (Dir_out_rel - 90)
    # Make sure direction is not > 360 or < 0
    if Dir_out_abs >= 360:
        Dir_out_abs = Dir_out_abs - 360
    elif Dir_out_abs < 0:
        Dir_out_abs = Dir_out_abs + 360
    elif Dir_out_abs < -360:
        Dir_out_abs = 0

    #%% Calculate Hs/D at output location (1/2 wavelength from toe of dike)
    
    Hs_D = Hs_300_2d / Dep_out
    Hs_decr_rel = (Hs_out - Hs_300_2d) / Hs_300_2d
    
    #%% Calculate average bed level in first 200m of profile
    
    z_200m = -data['Botlev'][(data['Xp'] >= Xpteen) & (data['Xp'] <= 200)]
    z_200m_avg = np.mean(z_200m)
           
    #%% y-limits for plots
    
    Hs_max = np.nanmax(data['Hsig'])
    Tm10_max = np.nanmax(data['Tm_10'])
    
    if np.isnan(Hs_max) or np.isnan(Tm10_max):
        Hs_max = 0
        Tm10_max = 0
        
    #%% Get SWAN1D output at 300m location
    
    Hs_300 = data['Hsig'][data['Xp'] >= Xp_300].iloc[0]
    Tp_300 = data['TPsmoo'][data['Xp'] >= Xp_300].iloc[0]
    Tm10_300 = data['Tm_10'][data['Xp'] >= Xp_300].iloc[0]
    Dir_300_rel = data['Dir'][data['Xp'] >= Xp_300].iloc[0]
    
    # Make sure direction is not > 360 or < 0
    Dir_300_abs = Dir_profile + (Dir_300_rel - 90)
    if Dir_300_abs >= 360:
        Dir_300_abs = Dir_300_abs - 360
    elif Dir_300_abs < 0:
        Dir_300_abs = Dir_300_abs + 360
    elif Dir_300_abs < -360:
        Dir_300_abs = -999
    
    #%% Prepare input for new SWAN 1D simulations (new iteration)
        
    # get swn-file and qsub-file
    swn_file = os.path.join(path_main,scene,simulation,simulation+'.swn')
    qsub_file = os.path.join(path_main,scene,simulation,simulation+'.qsub')
    
    # modify wave conditions in swn-file
    find_text = 'BOUN SIDE EAST CON PAR '

    with open(swn_file) as file:
        lines = file.readlines()
        
    for index, line in enumerate(lines):
        if line.startswith(find_text):
            print(f'we found {line}')
            break

    values = line.replace(find_text, '').replace('\n', '').split(' ')
    
    # wave boundary conditions of previous SWAN 1D run
    Hs_rand = float(values[0])
    Tp_rand = float(values[1])
    
    # Difference between SWAN2D and SWAN1D at 300m location       
    if Hs_300_2d <=0 or np.isnan(Hs_300):
        Hs_diff_fac = 1
        Tp_diff_fac = 1
        Tm10_diff_fac = 1
        Hs_diff = 0
        Tp_diff = 0
        Tm10_diff = 0
        Dir_diff = 0
    else:
        Hs_diff_fac = Hs_300_2d / Hs_300
        Tp_diff_fac = Tp_300_2d / Tp_300
        Tm10_diff_fac = Tm10_300_2d / Tm10_300
        Hs_diff = Hs_300_2d - Hs_300
        Tp_diff = Tp_300_2d - Tp_300
        Tm10_diff = Tm10_300_2d - Tm10_300
        Dir_diff = Dir_300_2d - Dir_300_abs
    
    # new wave boundary conditions for SWAN1D run
    Hs_bc_new = Hs_rand * Hs_diff_fac
    # Tp_bc_new = Tp_rand * Tp_diff_fac
    Tp_bc_new = Tp_rand * Tm10_diff_fac

    new_line = line.replace(values[0], f'{Hs_bc_new:.3f}')
    new_line = new_line.replace(values[1], f'{Tp_bc_new:.3f}')

    lines[index] = new_line
    
    # write SWAN1D input
    if new_iteration:
    
        # make new directory
        path_new_sim = os.path.join(path_new,scene,simulation)
        if not os.path.exists(path_new_sim):
            os.makedirs(path_new_sim)
    
         # write new swn-file
        swn_file_new = os.path.join(path_new_sim,simulation+'.swn')
    
        with open(swn_file_new, 'w') as file:
            file.writelines(lines)
        
        # copy qsub file
        qsub_file_new = os.path.join(path_new,scene,simulation,simulation+'.qsub')
        shutil.copyfile(qsub_file, qsub_file_new) 
    
    #%% Store output SWAN1D run and comparison with SWAN2D   
    
    output = {'OkaderId':   int(loc),
              'Scenario':   scene,
              'Dep':        Dep_out,
              'Hsig':       Hs_out,
              'TPsmoo':     Tp_out,
              'Tm_10':      Tm10_out,
              'Dir_profile':Dir_profile,
              'Dir_rel':    Dir_out_rel,
              'Dir_abs':    Dir_out_abs,
              'Hs_basis_2d':Hs_basis,
              'Hs_300m_2d': Hs_300_2d,
              'Hs_300m_1d': Hs_300,
              'TPsmoo_300m_2d': Tp_300_2d,
              'TPsmoo_300m_1d': Tp_300,
              'Tm_10_300m_2d': Tm10_300_2d,
              'Tm_10_300m_1d': Tm10_300,
              'Hs_D':       Hs_D,
              'Hs_decr_rel': Hs_decr_rel,
              'z_200m_avg': z_200m_avg,
              'Hs_300m_diff':    Hs_diff,
              'Tp_300m_diff':    Tp_diff,
              'Tm10_300m_diff':  Tm10_diff,
              'Dir_diff':        Dir_diff}
    
    appended_output.append(output)
              
    #%% Plot results SWAN 1D run and comparison with SWAN2D
    
    # if final iteration: determine whether SWAN 1D are used or not
    # determine which output to use (2D, 1D, haven)
    if final_iteration == True:  
        if switch_1d == 0 and switch_haven == 'Nee':
            use_2d      = 1
            use_1d      = 0
            use_haven   = 0
            title_color = 'r'
            fig_name_add = '_not_used'
        elif switch_1d == 0 and switch_haven == 'Ja':
            use_2d      = 0
            use_1d      = 0
            use_haven   = 1
            title_color = 'r'
            fig_name_add = '_not_used'
        elif switch_1d == 1 and switch_haven == 'Nee' and Hs_basis < 0 and Hs_out > 0:
            use_2d      = 0
            use_1d      = 1
            use_haven   = 0
            title_color = 'k'
            fig_name_add = '_used'
        elif switch_1d == 1 and switch_haven == 'Nee' and abs(Hs_diff) <= 0.2 and abs(Tm10_diff) <= 0.25 and Hs_out > 0 and ~np.isnan(Hs_out): 
            if Hs_decr_rel <= -0.10 or z_200m_avg >= 1:
                use_2d      = 0
                use_1d      = 1
                use_haven   = 0
                title_color = 'k'
                fig_name_add = '_used'
            else:
                use_2d      = 1
                use_1d      = 0
                use_haven   = 0
                title_color = 'r'
                fig_name_add = '_not_used'
        else:
            use_2d      = 1
            use_1d      = 0
            use_haven   = 0
            title_color = 'r'
            fig_name_add = '_not_used'
    else:
        title_color = 'k'
        fig_name_add = ''
    
    # now make the figure
    
    fig = plt.figure(figsize=(12,7))
    ax1 = plt.subplot(2,1,1)
    ax1_copy = ax1.twinx()
    
    ax1.plot(data['Xp'],-data['Botlev'],'k', linewidth = 3, label = 'bodem')
    ax1.plot(data['Xp'], data['Watlev'], 'b-', linewidth = 1.5, label = 'waterstand')
    ax1.axvline(x = Xpteen, color = 'k', linestyle='--', label = 'teen')
    ax1.axvline(x = Xpout, color = 'r', linestyle='--', label = 'teen + 1/2*L')
    ax1.axvline(x = Xp_300, color = 'tab:orange', linestyle='--', label = 'teen + 300m')
    # ax1.axvline(x = Xp_basis, color = 'y', linestyle='--', label = 'HRbasis')
    ax1.set_ylabel('hoogte [m+NAP]')
    ax1.set_xlabel('afstand [m]')
    ax1.legend(loc = 'lower right')
    # ax1.set_xlim(30,100)
    # ax1.set_ylim(-20,10)

    ax1_copy.plot(data['Xp'], data['Hsig'],'g', linewidth = 1.5, label = '$H_s$ [m]')
    ax1_copy.set_ylabel('$H_s$ [m]',color='g')
    ax1_copy.tick_params(labelcolor='g')
    t1 = ax1_copy.text(Xpin,Hs_in,f'BC: Hs = {Hs_rand:.2f} m \nIN:  Hs = {Hs_in:.2f} m',color='g',fontweight = 'bold')
    t2 = ax1_copy.text(Xpout+10,Hs_out,f'Hs = {Hs_out:.2f} m',color='g',fontweight = 'bold')
    t3 = ax1_copy.text(Xp_300+10,Hs_300,f'SWAN2D: Hs = {Hs_300_2d:.2f} m \nSWAN1D: Hs = {Hs_300:.2f} m',color='g',fontweight = 'bold')
    t1.set_bbox(dict(facecolor='white', alpha=1, edgecolor='black'))
    t2.set_bbox(dict(facecolor='white', alpha=1, edgecolor='black'))
    t3.set_bbox(dict(facecolor='white', alpha=1, edgecolor='black'))
    plt.title(f'{scene}\n{simulation}\n HRbasis: Hs = {Hs_basis:.2f} m, Tm10 = {Tm10_basis:.2f}\n L = {Wlen:.0f} m, Hs/D = {Hs_D:.2f}, z_200m_avg = {z_200m_avg:.1f} m', color = title_color)
    ax1_copy.legend(loc = 'center right')
    ax1_copy.set_ylim(0,np.ceil(Hs_max))
    
    ax2 = plt.subplot(2,1,2)
    ax2_copy = ax2.twinx()
    ax2.plot(data['Xp'],-data['Botlev'],'k', linewidth = 3, label = 'bodem')
    ax2.plot(data['Xp'], data['Watlev'], 'b-', linewidth = 1.5, label = 'waterstand')
    ax2.axvline(x = Xpteen, color = 'k', linestyle='--', label = 'teen')
    ax2.axvline(x = Xpout, color = 'r', linestyle='--', label = 'teen + 1/2*L')
    ax2.axvline(x = Xp_300, color = 'tab:orange', linestyle='--', label = 'teen + 300m')
    # ax2.axvline(x = Xp_basis, color = 'y', linestyle='--', label = 'HRbasis')
    ax2.set_ylabel('hoogte [m+NAP]')
    ax2.set_xlabel('afstand [m]')
    ax2.legend(loc = 'lower right')
    # ax2.set_xlim(30,100)
    # ax2.set_ylim(-20,10)

    # ax2_copy.plot(data['Xp'], data['Tm_10'],color='orange')
    ax2_copy.plot(data['Xp'], data['Tm_10'],'m', linewidth = 1.5,label = '$T_m-1,0$ [m]')
    ax2_copy.set_ylabel('$H_s$ [m]',color='m')
    ax2_copy.tick_params(labelcolor='m')
    t3 = ax2_copy.text(Xpin,Tm10_in,f'BC: Tp = {Tp_rand:.2f} s \nIN:  Tp = {Tp_in:.2f} s',color='m',fontweight = 'bold')
    t4 = ax2_copy.text(Xpout+10,Tm10_out,f'Tm_10 = {Tm10_out:.2f} s',color='m',fontweight = 'bold')
    t5 = ax2_copy.text(Xp_300+10,Tm10_300,f'SWAN2D: Tm_10 = {Tm10_300_2d:.2f} s \nSWAN1D: Tm_10 = {Tm10_300:.2f} s',color='m',fontweight = 'bold')
    t3.set_bbox(dict(facecolor='white', alpha=1, edgecolor='black'))
    t4.set_bbox(dict(facecolor='white', alpha=1, edgecolor='black'))
    t5.set_bbox(dict(facecolor='white', alpha=1, edgecolor='black'))
    ax2_copy.set_ylabel('$T_{m-1.0}$ [s]')
    ax2_copy.legend(loc = 'center right')
    ax2_copy.set_ylim(0,np.ceil(Tm10_max))
       
    if save_fig:
        save_name = os.path.join(output_path, scene+'_'+simulation+fig_name_add+'.png')
        save_plot.save_plot(fig,save_name,ax = ax1_copy, dx = -0.05)

    #%% Clear some memory (required when looping over multiple simulations)
    
    plt.close('all')
    del fig
    del data
    del ax1, ax1_copy, ax2, ax2_copy, t1, t2, t3, t4, t5
    gc.collect()

#%% Export output to Excel

output_df = pd.DataFrame(appended_output)
if save_result:
    output_df.to_excel(os.path.join(path_main,'output_productie_SWAN1D_WZ_iter_01.xlsx')) 