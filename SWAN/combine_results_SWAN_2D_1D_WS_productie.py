# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts combines the results of SWAN2D and SWAN1D runs for the Westerschelde.

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 
    Script to write SWAN1D output to Excel: read_SWAN_1D_model_WS_iteratie_productie.py
    Script to write SWAN2D output to Excel: SWAN_2D_output_to_xlsx_WS_productie.py

--- Version --- 
Created on Mon Oct  3 16:43:04 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: combine_results_SWAN_2D_1D_WS_productie.py 

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
import numpy as np

#%% Settings

# SWAN 2D output
path_output_2d      = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\03_productiesommen\serie_01\output_productie_SWAN2D_WS.xlsx'

# SWAN 1D output
path_output_1d      = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Westerschelde\02_productie\iter_03\output_productie_SWAN1D_WS.xlsx'

# Shapefile with info for each okader vak, minimal info: 
#   VakId (int): okader vakid
#   1D (1/0): switch to use 1D results (y/n)
#   harbour (boolean): switch to interpret as harbour (y/n)
#   D: average bed level in harbour (float), only applies if harbour = True
path_shape_vakken   = r'd:\Users\ENGT2\Documents\Projects\130991 - SA Waterveiligheid ZSS\GIS\illustratiepunten_methode\shape + 1d-flag\okader_fc_hydra_unique_handedit_WS_havens_berm_1d-flag.shp'

# Path to save output
path_output = r'z:\130991_Systeemanalyse_ZSS\5.Results\SWAN\WS'

# Output location to use in SWAN2D output files
outloc = 'HRbasis'

# Switch to save results to Excel
save_excel = True

#%% Read data

# SWAN2D output
xl_2d  = pd.ExcelFile(path_output_2d,engine='openpyxl')
df_2d = xl_2d.parse(outloc)

# SWAN1D ouput
xl_1d  = pd.ExcelFile(path_output_1d,engine='openpyxl')
df_1d = xl_1d.parse()

# info on which output to use for each okader vak
df_vakken = gp.read_file(path_shape_vakken)

#%% Combine 2D and 1D results

appended_data = []

OKids = df_2d['OkaderId'].unique()
scenarios = df_2d['Scenario'].unique()

# loop over all okader vakken and combine results
for OKid in OKids:
    
    for scenario in scenarios:
        
        ZSS = float(scenario.split('_')[-2])/100
        bot_scen = scenario.split('_')[-4]
        
        # OKADEr vak info
        info_vak        = df_vakken[df_vakken['VakId']==str(OKid)]
        x_okader_mp     = info_vak['xcoord'].iloc[0]
        y_okader_mp     = info_vak['ycoord'].iloc[0]
        
        # get criteria from shapefile
        switch_1d       = info_vak['1D'].iloc[0]
        switch_haven    = info_vak['Haven'].iloc[0]
        
        # look for matching SWAN2D and SWAN1D output
        match_2d = (df_2d['OkaderId']==OKid) & (df_2d['Scenario']==scenario)   
        match_1d = (df_1d['OkaderId']==OKid) & (df_1d['Scenario']==scenario)
        
        if match_2d.any() == False:
            raise Warning(f'no match found in SWAN2D output for {OKid} and {scenario}')
        else:
            output_2d   = df_2d[match_2d]
            
        if match_1d.any() == True:
            output_1d       = df_1d[match_1d]
            Hs_D            = output_1d['Hs_D'].iloc[0]
            Hs_decr_rel     = output_1d['Hs_decr_rel'].iloc[0]
            z_200m_avg      = output_1d['z_200m_avg'].iloc[0]
            Hs_300m_diff    = output_1d['Hs_300m_diff'].iloc[0]
            Tm10_300m_diff  = output_1d['Tm10_300m_diff'].iloc[0]
        
        # determine which output to use (2D, 1D, haven) for reference scenario
        if scenario == 'WS_NM_01_000_RF':  
            if switch_1d == 0 and switch_haven == 'Nee':
                use_2d      = 1
                use_1d      = 0
                use_haven   = 0
            elif switch_1d == 0 and switch_haven == 'Ja':
                use_2d      = 0
                use_1d      = 0
                use_haven   = 1
            # elif switch_1d == 1 and switch_haven == 'Nee' and Hs_300m_diff <= 0.2 and Tm10_300m_diff <= 0.25: 
            elif switch_1d == 1 and switch_haven == 'Nee' and abs(Hs_300m_diff) <= 0.2 and abs(Tm10_300m_diff) <= 0.25: 
                if Hs_decr_rel <= -0.10 or z_200m_avg >= 1:
                    use_2d      = 0
                    use_1d      = 1
                    use_haven   = 0
                else:
                    use_2d      = 1
                    use_1d      = 0
                    use_haven   = 0
            else:
                use_2d      = 1
                use_1d      = 0
                use_haven   = 0
                            
        if use_2d == 1:
            print(f'{scenario} {OKid}: use 2D result')
            output = {'OkaderId': OKid,
                      'x_okader_middelpunt': x_okader_mp,
                      'y_okader_middelpunt': y_okader_mp,
                      'Scenario': scenario,
                      'Depth':    output_2d['Depth'].iloc[0],
                      'Watlev':   output_2d['Watlev'].iloc[0],
                      'Hsig':     output_2d['Hsig'].iloc[0],
                      'Tpsmoo':   output_2d['TPsmoo'].iloc[0],
                      'Tm_10':    output_2d['Tm_10'].iloc[0],
                      'Dir':      output_2d['Dir'].iloc[0],
                      'SWAN2D':   1,
                      'SWAN1D':   0,
                      'Haven':    0,
                      'z_avg':    z_200m_avg}
        elif use_haven == 1:
            print(f'{scenario} {OKid}: use harbour correction')
            if bot_scen == 'VM':
                z_haven = float(info_vak['D'].iloc[0]) + ZSS
            else:
                z_haven = float(info_vak['D'].iloc[0])
            WL = output_2d['Watlev'].iloc[0] 
            D  = WL - z_haven 
            if D <= 0:
                Hsig = 0
            else:
                Hsig    = 0.5 * D
            output = {'OkaderId': OKid,
                      'x_okader_middelpunt': x_okader_mp,
                      'y_okader_middelpunt': y_okader_mp,
                      'Scenario': scenario,
                      'Depth':    output_2d['Depth'].iloc[0],
                      'Watlev':   output_2d['Watlev'].iloc[0],
                      'Hsig':     Hsig,
                      'Tpsmoo':   output_2d['TPsmoo'].iloc[0],
                      'Tm_10':    output_2d['Tm_10'].iloc[0],
                      'Dir':      output_2d['Dir'].iloc[0],
                      'SWAN2D':   1,
                      'SWAN1D':   0,
                      'Haven':    1,
                      'z_avg':    z_200m_avg}
        elif use_1d == 1:
            print(f'{scenario} {OKid}: use 1D result')
            dir_swan2d =  output_2d['Dir'].iloc[0]
            dir_swan1d =  output_1d['Dir_abs'].iloc[0]
            if dir_swan2d < 0:
                dir_use_1d = dir_swan1d
            else:
                dir_use_1d = dir_swan2d
            output = {'OkaderId': OKid,
                      'x_okader_middelpunt': x_okader_mp,
                      'y_okader_middelpunt': y_okader_mp,
                      'Scenario': scenario,
                      'Depth':    output_1d['Dep'].iloc[0],
                      'Watlev':   output_2d['Watlev'].iloc[0],
                      'Hsig':     output_1d['Hsig'].iloc[0],
                      'Tpsmoo':   output_1d['TPsmoo'].iloc[0],
                      'Tm_10':    output_1d['Tm_10'].iloc[0],
                      # 'Dir':      output_1d['Dir_abs'].iloc[0],
                      'Dir':      dir_use_1d,
                      'SWAN2D':   0,
                      'SWAN1D':   1,
                      'Haven':    0,
                      'z_avg':    z_200m_avg}
        
        if output['Depth'] <= 0:
            output['Depth'] = 0
            output['Hsig'] = 0
            output['Tpsmoo'] = 0
            output['Tm_10'] = 0
            output['Dir'] = 0
        elif np.isnan(output['Tpsmoo']):
            output['Tpsmoo'] = 0
           
        # append data
        appended_data.append(output)
    
#%% convert to dataframe and export to Excel

output_df = pd.DataFrame(appended_data)

if save_excel:
    output_df.to_excel(os.path.join(path_output,'output_productie_combined_WS_v04.xlsx'))