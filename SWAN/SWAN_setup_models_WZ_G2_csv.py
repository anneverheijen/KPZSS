# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 09:05:56 2022

@author: ENGT2
"""

# load modules

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

dirs = {'main':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G2_zeegat',
        'bathy':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\_bodem\G2_zeegat',
        'grid':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\_rooster',
        'input':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\input',
        'golfrand': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\_randvoorwaarden'}

files = {'swan_templ':  'template_G2_01_zeegat.swn',
         'qsub_templ':  'dummy.qsub',
         'scen_xlsx':   'scenarios_SWAN_2D_WZ_v01_zeegat.xlsx',
         'hyd_output':  'hydra_output_totaal_dsn_mod.csv',
         'grid':        'WADIN1A.GRD',
         'diepwaterrandvoorwaarden': 'HKV2010_diepwaterrandvoorwaarden.xlsx',
         'locaties':    'selectie_ill_pilot_v03_WZ.shp'}

node    = 'galatea'
ppn     = 4

#%% Read scenario input

xl_scen = pd.ExcelFile(os.path.join(dirs['input'],files['scen_xlsx']),engine='openpyxl')
df_scen = xl_scen.parse()

#%% Read Hydra-NL output

df_hyd  = pd.read_csv(os.path.join(dirs['input'],files['hyd_output']), sep=';',
                      dtype={'ZSS-scenario':str,
                             'Zeewaterstand [m+NAP]':np.float32,
                             'windsnelheid [m/s]': np.float32,
                             'windrichting [graden N]': np.float32})

#%% Read locaties (OKADER vak id's)

df_locs = geopandas.read_file(os.path.join(dirs['input'],files['locaties']))

#%% Filter Hydra-NL output for pilot locaties

df_hyd_pilot = pd.merge(df_hyd,df_locs, left_on = 'OKADER VakId', right_on = 'VakId')

#%% Read diepwaterrandvoorwaarden

xl_golfrand = pd.ExcelFile(os.path.join(dirs['golfrand'],files['diepwaterrandvoorwaarden']),engine='openpyxl')
df_golfran_ELD = xl_golfrand.parse(sheet_name = 'ELD',skiprows=1).drop([0,1])
df_golfran_SON = xl_golfrand.parse(sheet_name = 'SON',skiprows=1).drop([0,1])

# loop over scenario's

for ss in range(len(df_scen)):
       
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
    
    # filter on ZSS
    is_scen =  df_hyd_pilot['ZSS-scenario']==df_scen.ZSS_scenario[ss]
    df_hyd_scen = df_hyd_pilot[is_scen]
    
    # Loop over conditions/locations
    
    for cc, row in df_hyd_scen.iterrows():
        wl          = df_hyd_scen['Zeewaterstand [m+NAP]'][cc]
        ws          = df_hyd_scen['windsnelheid [m/s]'][cc]
        wd          = df_hyd_scen['windrichting [graden N]'][cc]
        
        # determine offshore wave boundary
        locid       = str(df_hyd_scen['OKADER VakId'][cc])
        savename_ELD    = os.path.join(dir_scen, locid + '_ELD_wave_conditions.png')
        savename_SON    = os.path.join(dir_scen, locid + '_SON_wave_conditions.png')
        Hs_offshore_ELD, Tp_offshore_ELD, fig = interp_offshore_waves.interp_offshore_waves(df_golfran_ELD, wd, ws, savename_ELD)
        Hs_offshore_SON, Tp_offshore_SON, fig = interp_offshore_waves.interp_offshore_waves(df_golfran_SON, wd, ws, savename_SON)
        
        conid       = "WS%02dWD%03dHS%02dTP%02dDIR%03d" % (ws, wd, Hs_offshore_ELD, Tp_offshore_ELD, wd)
        runid       = 'ID' + locid + '_' + conid
        swan_out    = runid + '.swn'
        qsub_out    = runid + '.qsub'
        
        #
        # FILTERING NEEDS TO BE DONE ON WAVE CONDITIONS, REMOVE DUBPLICATE CONDITIONS
        #
        
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
                        'WD': wd}

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