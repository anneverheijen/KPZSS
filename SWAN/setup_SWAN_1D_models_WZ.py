# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 10:57:49 2022

@author: ENGT2
"""

# load modules

import os
import pandas as pd
from hmtoolbox.WB_basic import replace_keywords
from hmtoolbox.WB_basic import deg2uv

# Settings

dirs = {'main':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\test_04_veg_layers',
        'bathy':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\_bodem',
        'input':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\test_04_veg_layers\input'}

files = {'swan_templ':  'template.swn',
         'qsub_templ':  'dummy.qsub',
         'scen_xlsx':   'scenarios_SWAN_1D_WZ.xlsx',
         'hyd_output':  'SWAN2D_output_WZ_6004026_HRext03.csv'}

node = 'naiad'
ppn = 1

# Read scenario input

xl_scen = pd.ExcelFile(os.path.join(dirs['input'],files['scen_xlsx']),engine='openpyxl')
df_scen = xl_scen.parse()

# Read Hydra-NL output

df_hyd  = pd.read_csv(os.path.join(dirs['input'],files['hyd_output']), sep=';',dtype={'ZSS-scenario':str})

# loop over scenario's

for ss in range(len(df_scen)):
       
    # make scenario directory
    dir_scen = os.path.join(dirs['main'], str(df_scen.Naam[ss]))
    
    if not os.path.exists(dir_scen):
        os.makedirs(dir_scen)

    # scenario input
    scenid  = df_scen.Naam[ss]
    zss     = df_scen.ZSS[ss]
    
    # condition input
    is_scen =  df_hyd['ZSS-scenario']==df_scen.ZSS_scenario[ss]

    df_hyd_scen = df_hyd[is_scen]
    
    is_bot =  df_hyd_scen['Bodem']==df_scen.Bodem[ss]
    
    df_hyd_scen = df_hyd_scen[is_bot]
       
    # loop over OKADER vakken 
    
    for cc, row in df_hyd_scen.iterrows():
                
        # load 1D profile
        bot         = df_scen.Bodem[ss] + '_' + str(df_hyd_scen['OKADER VakId'][cc]) + '_bottom.txt'
        profile     = df_scen.Bodem[ss] + '_' + str(df_hyd_scen['OKADER VakId'][cc]) + '_profile.txt'
        df_prof     = pd.read_csv(os.path.join(dirs['bathy'],profile), sep=',')
        
        # get profile orientation
        dx = df_prof['x'].iloc[0] - df_prof['x'].iloc[-1]
        dy = df_prof['y'].iloc[0] - df_prof['y'].iloc[-1]
        dir_profile= deg2uv.uv2deg(dx, dy, 'nautical')
        dir_wind_rel = abs(df_hyd_scen['WD'][cc] - dir_profile) 
        dir_wind = 90 + dir_wind_rel # 90 degrees is orientaion 1D profile in SWAN
               
        # get dimensions of computational grid
        xlenc       = df_prof['distance'].iloc[-1]
        mxc         = len(df_prof['distance'])-1
        # get dimensions of bottom input
        mxinp       = mxc
        dxinp       = df_prof['distance'].iloc[1] - df_prof['distance'].iloc[0]
        
        # other input
        wl          = df_hyd_scen['WL'][cc]
        ws          = df_hyd_scen['WS'][cc]
        wd          = dir_wind
        wd_name     = df_hyd_scen['WD'][cc]
        hs          = df_hyd_scen['HS'][cc]
        tp          = df_hyd_scen['TP'][cc]
        dirw        = 90 # loodrechte inval
        dspr        = df_hyd_scen['DSPR'][cc]
        gamma       = 3.3
        locid       = str(df_hyd_scen['OKADER VakId'][cc])
        conid       = "WZ%02dWD%03dHS%02dTP%02dDIR%03d" % (ws, wd_name, hs, tp, dirw)
        runid       = 'ID' + locid + '_' + conid
        swan_out    = runid + '.swn'
        qsub_out    = runid + '.qsub'
               
        #
        # FILTERING NEEDS TO BE DONE ON WAVE CONDITIONS, REMOBE DUBPLICATE CONDITIONS
        #
        
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
    