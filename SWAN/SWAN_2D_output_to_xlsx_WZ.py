# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 14:25:57 2022

@author: ENGT2
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_SWAN import SWAN_read_tab
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot
import pandas as pd

path_main   = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\01_tests\batch_03\G2'
path_out = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\01_tests\batch_03'
dirs        = list_files_folders.list_folders(path_main, dir_incl='WZ', startswith = True, endswith = False)

#%% Read output for selected locations and export to Excel

OKids   = [6005025, 6004015, 6004026, 6003036, 6003016, 3003002, 2010011]
X       = [270942, 225993, 244563, 182402, 158069, 155197, 146346]
Y       = [585367, 604547, 609695, 595475, 579713, 601794, 562459]

appended_data = []
for diri in dirs:
    ix = 0
    dirname = os.path.basename(os.path.normpath(diri))
    print(f'== processing {dirname}')
    for OKid in OKids:
        subdir = list_files_folders.list_folders(diri, dir_incl="ID%d" % OKid)
        subdir = subdir[0]
        files = list_files_folders.list_files('.TAB', subdir, startswith = False, endswith = True)
        subdirname = os.path.basename(os.path.normpath(subdir))
        for file in files:
            f = os.path.basename(os.path.normpath(file))
            if f.startswith('HRbasis'):
                print(f)
                data, headers = SWAN_read_tab.Freadtab(os.path.join(subdir,f))  
            else:
                print('.TAB-file skipepd')                  
        xx = X[ix]
        yy = Y[ix]
        result  = data[(data['Xp'] == xx) & (data['Yp'] == yy)]
        result['OkaderId'] = OKids[ix]
        result['Scenario'] = dirname
        appended_data.append(result)
        ix = ix + 1
            
appended_data = pd.concat(appended_data)        
appended_data.to_excel(os.path.join(path_out,'output_batch_03_compleet.xlsx'))    
