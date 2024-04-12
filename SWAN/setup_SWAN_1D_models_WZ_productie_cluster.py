# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts generates SWAN1D runs for the Waddenzee for specified scenarios.

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 

--- Version --- 
Created on Tue Sep 27 12:32:23 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: setup_SWAN_1D_models_WZ_productie.py

--- Revision --- 
Status: Unverified 

Witteveen+Bos Consulting Engineers 
Leeuwenbrug 8
P.O. box 233 
7411 TJ Deventer
The Netherlands 
		
"""

#%% load modules

import os
import pandas as pd
from hmtoolbox.WB_basic import replace_keywords
from hmtoolbox.WB_basic import deg2uv
import numpy as np

#%% Settings

dirs = {'main':     r'/project/130991_Systeemanalyse_ZSS/3.Models/SWAN/1D/Waddenzee/02_productie/serie_02/iter_01',
        'bathy':    r'/project/130991_Systeemanalyse_ZSS/3.Models/SWAN/1D/Waddenzee/02_productie/serie_02/_bodem',
        'input':    r'/project/130991_Systeemanalyse_ZSS/3.Models/SWAN/1D/Waddenzee/02_productie/serie_02/iter_01/input'}

files = {'swan_templ':  'template.swn',
         'qsub_templ':  'dummy.qsub',
         'scen_xlsx':   'scenarios_SWAN_2D_WZ_v02.xlsx',
         'swan_output': 'output_productie_SWAN2D_WZ_v3.xlsx'}

outloc = 'HRext01_300m'

node = 'despina'
ppn = 1

#%% Read scenario input

xl_scen = pd.ExcelFile(os.path.join(dirs['input'],files['scen_xlsx']),engine='openpyxl')
df_scen = xl_scen.parse()

#%% Read SWAN 2D output

xl_input  = pd.ExcelFile(os.path.join(dirs['input'],files['swan_output']),engine='openpyxl')
df_input = xl_input.parse(sheet_name = outloc)

prof_not_found = []

profile_info = []

#%% loop over scenario's

for ss in range(len(df_scen)):
    
    # change machine in qsub depending on scenario
    if ss <= 7:
        node    = 'despina'
    elif 7 < ss <= 15:
        node    = 'despina'
    
    # make scenario directory
    dir_scen = os.path.join(dirs['main'], str(df_scen.Naam[ss]))
    if not os.path.exists(dir_scen):
        os.makedirs(dir_scen)

    # scenario input
    scenid  = df_scen.Naam[ss]
    zss     = df_scen.ZSS[ss]
    
    print(scenid)
    
    # condition input
    is_scen =  df_input['Scenario']==df_scen['Naam'][ss]

    df_input_scen = df_input[is_scen]
    
    # loop over OKADER vakken 
    
    for cc, row in df_input_scen.iterrows():
        
        # check if there is a 1D profile available
        bot         = df_scen.Bodem[ss] + '_' + str(df_input_scen['OkaderId'][cc]) + '_bottom.txt'
        profile     = df_scen.Bodem[ss] + '_' + str(df_input_scen['OkaderId'][cc]) + '_profile.txt'
        
        if os.path.exists(os.path.join(dirs['bathy'],profile)):      
       
            # load 1D profile              
            df_prof     = pd.read_csv(os.path.join(dirs['bathy'],profile), sep=',')
            
            # get profile orientation
            dx = df_prof['x'].iloc[0] - df_prof['x'].iloc[-1]
            dy = df_prof['y'].iloc[0] - df_prof['y'].iloc[-1]
            dir_profile= deg2uv.uv2deg(dx, dy, 'nautical')
            
            output = {'OkaderId':       df_input_scen['OkaderId'][cc],
                      'Scenario':       df_input_scen['Scenario'][cc],
                      'dir_profile':    dir_profile}
            profile_info.append(output)
            
            # determine wind direction relative to 1D profile
            uu = df_input_scen['X-Windv'][cc]
            vv = df_input_scen['Y-Windv'][cc]
            dir_wind = round(deg2uv.uv2deg(uu, vv, 'nautical'))
            dir_wind_rel = dir_wind - dir_profile
            dir_wind_swan = 90 + dir_wind_rel # 90 degrees is orientaion 1D profile in SWAN
            if dir_wind_swan >= 360:
                dir_wind_swan = dir_wind_swan - 360
            elif dir_wind_swan < 0:
                dir_wind_swan = dir_wind_swan + 360
            
            # determine wind speed
            speed_wind = np.sqrt(uu**2 + vv**2)
            
            # determine wave direction relative to 1D profile
            dir_wave = df_input_scen['Dir'][cc]
            dir_wave_rel = dir_wave - dir_profile
            dir_wave_swan = 90 + dir_wave_rel # 90 degrees is orientaion 1D profile in SWAN
            if dir_wave_swan >= 360:
                dir_wave_swan = dir_wave_swan - 360
            elif dir_wave_swan < 0:
                dir_wave_swan = dir_wave_swan + 360
                   
            # get dimensions of computational grid
            xlenc       = df_prof['distance'].iloc[-1]
            mxc         = len(df_prof['distance'])-1
            # get dimensions of bottom input
            mxinp       = mxc
            dxinp       = df_prof['distance'].iloc[1] - df_prof['distance'].iloc[0]
            
            # other input
            wl          = df_input_scen['Watlev'][cc]
            ws          = speed_wind
            wd          = dir_wind_swan
            wd_name     = dir_wind
            hs          = df_input_scen['Hsig'][cc]
            tp          = df_input_scen['TPsmoo'][cc]
            dirw        = dir_wave_swan
            dspr        = df_input_scen['Dspr'][cc]
            gamma       = 3.3
            locid       = str(df_input_scen['OkaderId'][cc])
            
            # replace nans
            if np.isnan(wl) or np.isnan(ws) or np.isnan(wd) or np.isnan(hs) or np.isnan(tp) or np.isnan(dirw):
                wl      = 0
                ws      = 0
                wd      = 0
                hs      = 0
                tp      = 0
                dirw    = 0            
            
            conid       = "WZ%02dWD%03dHS%02dTP%02dDIR%03d" % (ws, wd_name, hs, tp, dirw)
            runid       = 'ID' + locid + '_' + conid
            swan_out    = runid + '.swn'
            qsub_out    = runid + '.qsub'
            
            print(runid)
                   
            # make scenario directory
            dir_run = os.path.join(dir_scen, runid)
            if not os.path.exists(dir_run):
                os.makedirs(dir_run)
                
            keyword_dict = {'LOCID': locid,
                            'RUNID': runid,
                            'LEVEL': wl,
                            'XLENC': xlenc,
                            'MXC': mxc,
                            'MXINP':mxinp,
                            'DXINP': dxinp, 
                            'BOT': bot,
                            'WS': ws,
                            'WD': wd,
                            'GAMMA': gamma,
                            'HS': hs,
                            'TP': tp,
                            'DIR': dirw,
                            'DSPR': dspr}
    
            # make *swn-files
            
            replace_keywords.replace_keywords(os.path.join(dirs['input'], files['swan_templ']), 
                                              os.path.join(dir_run, swan_out), 
                                              keyword_dict, '<', '>')
            
            # make qsub files
            
            keyword_dict2 = {'NODE': node,
                             'PPN': ppn,
                             'RUNID': runid}
            
            replace_keywords.replace_keywords(os.path.join(dirs['input'], files['qsub_templ']), 
                                              os.path.join(dir_run, qsub_out), 
                                              keyword_dict2, '<', '>')
            
        else:   
            print('profile for %s not found' % row['OkaderId'])
            prof_not_found.append(row['OkaderId'])
            
output_df = pd.DataFrame(profile_info)
output_df.to_excel(os.path.join(dirs['bathy'],'profile_info_SWAN1D_WZ.xlsx')) 
        