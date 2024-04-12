# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts generates SWAN2D runs for the Waddenzee (G2 domain) for specified scenarios.

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 

--- Version --- 
Created on Tue Aug 30 09:05:56 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: SWAN_setup_models_WZ_G2_csv_productie.py

--- Revision --- 
Status: Unverified 

Witteveen+Bos Consulting Engineers 
Leeuwenbrug 8
P.O. box 233 
7411 TJ Deventer
The Netherlands 
		
"""

#%% Load modules

import os
import sys
import pandas as pd
from scipy import interpolate
import numpy as np
import geopandas
import matplotlib.pyplot as plt
from hmtoolbox.WB_basic import replace_keywords
from hmtoolbox.WB_basic import save_plot
from SWAN import interp_offshore_waves

#%% Settings

dirs = {'main':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\03_productiesommen\serie_01\G2',
        'bathy':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\03_productiesommen\_bodem\G2',
        'grid':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\03_productiesommen\_rooster',
        'input':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\03_productiesommen\serie_01\input',
        'golfrand': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\03_productiesommen\_rvw'}

files = {'swan_templ':  'template_G2.swn',
         'qsub_templ':  'dummy.qsub',
         'scen_xlsx':   'scenarios_SWAN_2D_WZ_v02.xlsx',
         'ips':         'IP_binning_WZ_KPZSS_2023_Referentie.xlsx',
         'grid':        'WADIN1A.GRD',
         'diepwaterrandvoorwaarden': 'HKV2010_diepwaterrandvoorwaarden.xlsx',
         'HRbasis':     'HRbasis_WZ_Hydra.pnt',
         'HRext01':     'profielen_300m_int.pnt',
         'HRext02':     'HRbasis_WZ_Hydra_300m.pnt',
         'HRext03':     'HRbasis_WZ_Hydra_600m.pnt',
         'HRext04':     'HRextra_WZ.pnt',
         'HRext05':     'HRvoorlanden_WZ.pnt'}

# qsub settings
node    = 'despina'
ppn     = 4

#%% Read scenario input

xl_scen = pd.ExcelFile(os.path.join(dirs['input'],files['scen_xlsx']),engine='openpyxl')
df_scen = xl_scen.parse()

#%% Read illustratiepunten (wind and water level) input

df_ips_prod = pd.ExcelFile(os.path.join(dirs['input'],files['ips']),engine='openpyxl')
df_ips_prod = df_ips_prod.parse()

#%% Read diepwaterrandvoorwaarden

xl_golfrand = pd.ExcelFile(os.path.join(dirs['golfrand'],files['diepwaterrandvoorwaarden']),engine='openpyxl')
df_golfran_ELD = xl_golfrand.parse(sheet_name = 'ELD',skiprows=1).drop([0,1])
df_golfran_SON = xl_golfrand.parse(sheet_name = 'SON',skiprows=1).drop([0,1])

# loop over scenario's

for ss in range(len(df_scen)):
    
    # change machine in qsub depending on scenario
    if ss <= 5:
        node    = 'despina'
        ppn     = 4
    elif 5 < ss <= 10:
        node    = 'despina'
        ppn     = 4
    elif 10 < ss <= 15:
        node    = 'despina'
        ppn     = 4
       
    # make scenario directory
    bot_scen = str(df_scen.Naam[ss])
    dir_scen = os.path.join(dirs['main'], bot_scen)
    if not os.path.exists(dir_scen):
        os.makedirs(dir_scen)

    # scenario input
    grd     = files['grid']
    bot     = df_scen.Bodem[ss]+'.bot'
    scenid  = df_scen.Naam[ss]
    zss     = df_scen.ZSS[ss]
       
    # Loop over conditions/locations
    
    for cc, row in df_ips_prod.iterrows():
        wl          = df_ips_prod['h_mean'][cc] + zss
        ws          = df_ips_prod['ws_mean'][cc]
        wd          = df_ips_prod['wdir'][cc]
        
        # determine offshore wave boundary
        locid       = '%03d' % cc   
        savename_ELD    = os.path.join(dir_scen, locid + '_ELD_wave_conditions.png')
        savename_SON    = os.path.join(dir_scen, locid + '_SON_wave_conditions.png')
        Hs_offshore_ELD, Tp_offshore_ELD, fig = interp_offshore_waves.interp_offshore_waves(df_golfran_ELD, wd, ws, savename_ELD)
        Hs_offshore_SON, Tp_offshore_SON, fig = interp_offshore_waves.interp_offshore_waves(df_golfran_SON, wd, ws, savename_SON)
        
        conid       = "WZ%02dWD%03dHS%02dTP%02dDIR%03d" % (ws, wd, Hs_offshore_ELD, Tp_offshore_ELD, wd)
        runid       = 'ID' + locid + '_' + conid
        swan_out    = runid + '.swn'
        qsub_out    = runid + '.qsub'
               
        # make scenario directory
        dir_run = os.path.join(dir_scen, runid)
        if not os.path.exists(dir_run):
            os.makedirs(dir_run)
            
        keyword_dict = {'LOCID': locid,
                        'RUNID': runid,
                        'LEVEL': wl,
                        'GRD': grd,
                        'BOT': bot,
                        'BOT_SCEN': bot_scen,
                        'WS': ws,
                        'WD': wd,
                        'HRbasis': files['HRbasis'],
                        'HRext01': files['HRext01'],
                        'HRext02': files['HRext02'],
                        'HRext03': files['HRext03'],
                        'HRext04': files['HRext04'],
                        'HRext05': files['HRext05']}

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