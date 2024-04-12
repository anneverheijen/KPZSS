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
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_SWAN import SWAN_read_tab
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot
import shutil
import numpy as np

# %pylab qt
import gc
import xlsxwriter

#%% Settings

# main
path_main = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\iter_01'
path_results_1D = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\iter_01\WZ_NM_01_000_RF'
path_profile_info = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\_bodem'
file_profile_info = 'profile_info_SWAN1D_WZ.xlsx'

tab_files = list_files_folders.list_files('.TAB',path_results_1D)

save_result = True

# path output file
path_out = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\_bodem'


#%% Load tab_file with simulation input

# Excel with info on 1D profiles (orientation)
xl_profile  = pd.ExcelFile(os.path.join(path_profile_info,file_profile_info),engine='openpyxl')
df_profile  = xl_profile.parse()
df_profile['Xp_teen'] = np.nan

#%% loop trough SWAN1D simulations, plot results, prepare input for new simulations (new iteration)

appended_output = []


for tab_file in tab_files:

    if 'WZ_NM_01_000_RF' in tab_file:
        
        # get relevant names from filename
        scene = tab_file.split('\\')[-3]
        simulation = tab_file.split('\\')[-2]
        loc = simulation.split('_')[0][2:]
        
        if scene == 'WZ_NM_01_000_RF':
            # output path 
            output_path = os.path.join(path_main,scene)

            data, headers = SWAN_read_tab.Freadtab(tab_file)
            data['Botlev'][data['Botlev']<-20] = -10
            
            #%% Determine location toe of dike (defined as first location where slope < 1/10, as seen from dyke)
            
            ii = 0
            slope = list()
            Xpteen = data['Xp'].iloc[0]
            for x1, x2, y1, y2 in zip(data['Xp'][1:40], data['Xp'][:41], data['Botlev'][1:40], data['Botlev'][:41]):
                dx = x1 - x2
                dy = y1 - y2
                if dy == 0:
                    dydx = 0
                else:
                    dydx = dy/dx
                    if dydx <= 1/10 and x2 > 10 and ii == 0:
                        Xpteen = x2
                        ii = ii + 1
                if np.isnan(Xpteen) or Xpteen == 0:
                    Xpteen = 10
                slope.append(dydx)
            if ii == 0:
                slope_max = np.nanmax(slope)
                slope_max_ind = np.nanargmax(slope)
                Xpteen = data['Xp'][slope_max_ind]

        df_profile['Xp_teen'].loc[(df_profile['OkaderId']==float(loc)) & (df_profile['Scenario'] == scene)] = Xpteen

if save_result:
    savename = os.path.join(path_out, 'profile_info_SWAN1D_WZ_xteen.xlsx')
    df_profile.to_excel(savename, index = False)
