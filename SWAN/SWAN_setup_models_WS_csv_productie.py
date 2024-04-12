# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts generates SWAN2D runs for the Westerschelde for specified scenarios.

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 
    Determine offshore wave boundary conditions: interp_offshore_waves.py

--- Version --- 
Created on Mon September 26 08:34:50 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: SWAN_setup_models_WS_csv_productie.py 

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

dirs = {'main':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\03_productiesommen\serie_02',
        'bathy':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\03_productiesommen\_bodem',
        'grid':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\03_productiesommen\_rooster',
        'input':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\03_productiesommen\serie_02\input',
        'golfrand': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\03_productiesommen\_rvw'}

files = {'swan_templ':  'template.swn',
         'qsub_templ':  'dummy.qsub',
         'scen_xlsx':   'scenarios_SWAN_2D_WS_v02.xlsx',
         'ips':         'IP_binning_WZ_KPZSS_2023_Referentie.xlsx',
         'grid':        'swan_grid_cart_4.grd',
         'HRbasis':     'HRbasis_WS_Hydra.pnt',
         'HRext01':     'profielen_300m_int.pnt',
         'HRext02':     'HRbasis_WS_Hydra_300m.pnt',
         'HRext03':     'HRbasis_WS_Hydra_600m.pnt',
         'HRext04':     'HRextra_WS.pnt',
         'diepwaterrandvoorwaarden': 'HKV2010_diepwaterrandvoorwaarden.xlsx'}

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
df_golfrand = xl_golfrand.parse(sheet_name = 'SCW',skiprows=1).drop([0,1])

# loop over scenario's

for ss in range(len(df_scen)):
    
    # change machine in qsub depending on scenario
    if ss <= 5:
        node    = 'despina'
        ppn     = 4
    elif 5 < ss <= 10:
        node    = 'naiad'
        ppn     = 4
    elif 10 < ss <= 15:
        node    = 'galatea'
        ppn     = 4            
    
    # make scenario directory
    dir_scen = os.path.join(dirs['main'], str(df_scen.Naam[ss]))
    if not os.path.exists(dir_scen):
        os.makedirs(dir_scen)

    # scenario input
    grd     = files['grid']
    bot     = df_scen.Bodem[ss]+'.bot'
    scenid  = df_scen.Naam[ss]
    zss     = df_scen.ZSS[ss]
      
    # Loop over conditions
    
    for cc, row in df_ips_prod.iterrows():
        wl          = df_ips_prod['h_mean'][cc] + zss
        ws          = df_ips_prod['ws_mean'][cc]
        wd          = df_ips_prod['wdir'][cc]
        
        # determine offshore wave boundary
        locid       = '%03d' % cc
        savename    = os.path.join(dir_scen, locid + '_wave_conditions.png')
        Hs_offshore, Tp_offshore, fig = interp_offshore_waves.interp_offshore_waves(df_golfrand, wd, ws, savename)
        
        hs_zn       = 0.01 # zero boundary
        tp_zn       = Tp_offshore # dummy
        dirw_zn     = wd # dummy
        dspr_zn     = 30 # dummy
        
        hs_d        = Hs_offshore # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        tp_d        = Tp_offshore # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        dirw_d      = wd # assumption same as wind direction
        dspr_d      = 30 # default
        
        hs_s        = Hs_offshore # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        tp_s        = Tp_offshore # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        dirw_s      = wd # assumption same as wind direction
        dspr_s      = 30 # default
        
        hs_zs       = 0.01 # zero boundary
        tp_zs       = Tp_offshore # dummy
        dirw_zs     = wd # dummy
        dspr_zs     = 30 # dummy
        
        gamma       = 3.3 # default for all boundary conditions
        
        conid       = "WS%02dWD%03dHS%02dTP%02dDIR%03d" % (ws, wd, hs_s, tp_s, dirw_s)
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
                        'WS': ws,
                        'WD': wd,
                        'GAMMA': gamma,
                        'HS_ZN': hs_zn,
                        'TP_ZN': tp_zn,
                        'DIR_ZN': dirw_zn,
                        'DSPR_ZN': dspr_zn,
                        'HS_D': hs_d,
                        'TP_D': tp_d,
                        'DIR_D': dirw_d,
                        'DSPR_D': dspr_d,
                        'HS_S': hs_s,
                        'TP_S': tp_s,
                        'DIR_S': dirw_s,
                        'DSPR_S': dspr_s,
                        'HS_ZS': hs_zs,
                        'TP_ZS': tp_zs,
                        'DIR_ZS': dirw_zs,
                        'DSPR_ZS': dspr_zs,
                        'HRbasis': files['HRbasis'],
                        'HRext01': files['HRext01'],
                        'HRext02': files['HRext02'],
                        'HRext03': files['HRext03'],
                        'HRext04': files['HRext04']}

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