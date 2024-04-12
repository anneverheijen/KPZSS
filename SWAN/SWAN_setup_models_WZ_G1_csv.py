# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:35:37 2022

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

dirs = {'main':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\G1_01_zeegat',
        'bathy':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\_bodem\G1_01_zeegat',
        'grid':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\_rooster',
        'input':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\01_bodem\input',
        'golfrand': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\04_sensitivity\_randvoorwaarden'}

files = {'swan_templ':  'template_G1_01_zeegat.swn',
         'qsub_templ':  'dummy.qsub',
         'scen_xlsx':   'scenarios_SWAN_2D_WZ_v01_zeegat.xlsx',
         'hyd_output':  'hydra_output_totaal_dsn_mod.csv',
         'grid':        'WADOUT1A.GRD',
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
    dir_scen = os.path.join(dirs['main'], str(df_scen.Naam[ss]))
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
        
        hs_eld_w    = Hs_offshore_ELD # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        tp_eld_w    = Tp_offshore_ELD # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        dirw_eld_w  = wd # assumption same as wind direction
        dspr_eld_w  = 30 # default
        
        hs_eld_sw   = 0.01 # zero boundary
        tp_eld_sw   = Tp_offshore_ELD # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        dirw_eld_sw = wd # dummy
        dspr_eld_sw = 30 # dummy
        
        hs_eld      = Hs_offshore_ELD # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        tp_eld      = Tp_offshore_ELD # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        dirw_eld    = wd # assumption same as wind direction
        dspr_eld    = 30 # default
        
        hs_son      = Hs_offshore_SON # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        tp_son      = Tp_offshore_SON # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        dirw_son    = wd # assumption same as wind direction
        dspr_son    = 30 # default
        
        hs_son_se   = 0.01 # zero boundary
        tp_son_se   = Tp_offshore_SON # dummy
        dirw_son_se = wd # dummy
        dspr_son_se = 30 # dummy
        
        hs_son_e   = Hs_offshore_SON # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        tp_son_e   = Tp_offshore_SON # obtained using linear interpolation on offshore diepwaterrandvoorwaarden
        dirw_son_e = wd # assumption same as wind direction
        dspr_son_e = 30 # default
        
        gamma       = 3.3 # default for all boundary conditions
        
        # conid       = "WZ%02dWD%03dHS%02dTP%02dDIR%03d" % (ws, wd, hs_eld, tp_eld, dirw_eld)
        conid       = "WS%02dWD%03dHS%02dTP%02dDIR%03d" % (ws, wd, hs_eld, tp_eld, dirw_eld)
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
                        'WS': ws,
                        'WD': wd,
                        'GAMMA': gamma,
                        'HS_ELD_W': hs_eld_w,
                        'TP_ELD_W': tp_eld_w,
                        'DIR_ELD_W': dirw_eld_w,
                        'DSPR_ELD_W': dspr_eld_w,
                        'HS_ELD_SW': hs_eld_sw,
                        'TP_ELD_SW': tp_eld_sw,
                        'DIR_ELD_SW': dirw_eld_sw,
                        'DSPR_ELD_SW': dspr_eld_sw,
                        'HS_ELD': hs_eld,
                        'TP_ELD': tp_eld,
                        'DIR_ELD': dirw_eld,
                        'DSPR_ELD': dspr_eld,
                        'HS_SON': hs_son,
                        'TP_SON': tp_son,
                        'DIR_SON': dirw_son,
                        'DSPR_SON': dspr_son,
                        'HS_SON_SE': hs_son_se,
                        'TP_SON_SE': tp_son_se,
                        'DIR_SON_SE': dirw_son_se,
                        'DSPR_SON_SE': dspr_son_se,
                        'HS_SON_E': hs_son_e,
                        'TP_SON_E': tp_son_e,
                        'DIR_SON_E': dirw_son_e,
                        'DSPR_SON_E': dspr_son_e}

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