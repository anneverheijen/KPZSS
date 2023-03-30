# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:35:37 2022

@author: ENGT2
"""

# load modules

import os
import sys
import pandas as pd
import geopandas as gp
from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
from hmtoolbox.WB_basic import replace_keywords
from hmtoolbox.WB_basic import save_plot
from SWAN import interp_offshore_waves
from SWAN import get_ip_ant

#%% Settings

dirs = {'main':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\02_pilot\batch_03',
        'bathy':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\02_pilot\_bodem',
        'grid':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\02_pilot\_rooster',
        'input':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\02_pilot\batch_03\input',
        'golfrand': r'z:\130991_Systeemanalyse_ZSS\2.Data\dummy\randvoorwaarden'}

files = {'swan_templ':  'template.swn',
         'qsub_templ':  'dummy.qsub',
         'scen_xlsx':   'scenarios_SWAN_2D_WS_v02.xlsx',
         'grid':        'swan_grid_cart_4.grd',
         'HRbasis':     'HRbasis.pnt',
         'HRext01':     'HR_voorland_rand.pnt',
         'HRext02':     'HR_voorland_rand_300m_pilot.pnt',
         'diepwaterrandvoorwaarden': 'HKV2010_diepwaterrandvoorwaarden.xlsx',
         'locaties':    'selectie_ill_pilot_v02_WS.shp'}

node    = 'triton'
ppn     = 4

project_name = 'Systeemanalyse Waterveiligheid'

#%% Read input

# read scenario input
xl_scen = pd.ExcelFile(os.path.join(dirs['input'],files['scen_xlsx']),engine='openpyxl')
df_scen = xl_scen.parse()

# read locaties (OKADER vak id's)
df_locs = gp.read_file(os.path.join(dirs['input'],files['locaties']))
   
# read diepwaterrandvoorwaarden
xl_golfrand = pd.ExcelFile(os.path.join(dirs['golfrand'],files['diepwaterrandvoorwaarden']),engine='openpyxl')
df_golfrand = xl_golfrand.parse(sheet_name = 'SCW',skiprows=1).drop([0,1])

#%% loop over scenario's and vakken and make SWAN input

for ss in range(len(df_scen)):
    
    # make scenario directory
    dir_scen = os.path.join(dirs['main'], str(df_scen.Naam[ss]))
    if not os.path.exists(dir_scen):
        os.makedirs(dir_scen)

    # scenario input
    grd     = files['grid']
    bot     = df_scen.Bodem[ss]+'.bot'
    scenid  = df_scen.Naam[ss]
    zss     = df_scen.ZSS[ss]*100 # in cm's!
    
    # loop over OKADER vakken

    for vakid in df_locs['VakId']:
        vakid = str(vakid)
        ip_resuls, index_Vak, index_HRD, index_IPM = get_ip_ant.get_ip_ant(project_name,vakid,zss)
   
        wl          = ip_resuls['Waterstand']
        ws          = ip_resuls['Windsnelheid']
        wd          = ip_resuls['Windrichting']
        
        # determine offshore wave boundary
        savename    = os.path.join(dir_scen, vakid + '_wave_conditions.png')
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
        runid       = 'ID' + vakid + '_' + conid
        swan_out    = runid + '.swn'
        qsub_out    = runid + '.qsub'
        
        #
        # FILTERING NEEDS TO BE DONE ON WAVE CONDITIONS, REMOBE DUBPLICATE CONDITIONS
        #
        
        # make scenario directory
        dir_run = os.path.join(dir_scen, runid)
        if not os.path.exists(dir_run):
            os.makedirs(dir_run)
            
        keyword_dict = {'LOCID': vakid,
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
                        'HRext02': files['HRext02']}

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


# f'{df_locs.loc[0]["geometry"]}'

# from shapely.geometry import Point
# a = Point(10, 300.0)
# f'{a}'
# dict_met_uitvoer = {'geometry' : f'{a}'}
