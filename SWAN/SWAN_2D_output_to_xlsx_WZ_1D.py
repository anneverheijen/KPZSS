# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 10:48:51 2022

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
dirs        = list_files_folders.list_folders(path_main, dir_incl='WZ', startswith = True, endswith = False)

#%% Read output for selected locations and export to Excel

OKids   = [6004026]
# OKids   = [6003036]

# # HR basis
# outloc = 'HRbasis'
# X       = [28005]
# Y       = [385787]

# 300 m vanaf teen dijk
# outloc = 'HRext02'
# X       = [271048]
# Y       = [585593]

# 600 m vanaf teen dijk
outloc = 'HRext03'
X       = [271175]
Y       = [585865]

appended_data = []
for diri in dirs:
    ix = 0
    dirname = os.path.basename(os.path.normpath(diri))
    for OKid in OKids:
        subdir = list_files_folders.list_folders(diri, dir_incl="ID%d" % OKid)
        subdir = subdir[0]
        files = list_files_folders.list_files('.TAB', subdir, startswith = False, endswith = True)
        subdirname = os.path.basename(os.path.normpath(subdir))
        for file in files:
            f = os.path.basename(os.path.normpath(file))
            if f.startswith(outloc):
                print(f)
                data, headers = SWAN_read_tab.Freadtab(os.path.join(subdir,f))  
            else:
                print('.TAB-file skipped')                  
        xx = X[ix]
        yy = Y[ix]
        result  = data[(data['Xp'] == xx) & (data['Yp'] == yy)]
        result['OkaderId'] = OKids[ix]
        result['Scenario'] = dirname
        appended_data.append(result)
        ix = ix + 1
            
appended_data = pd.concat(appended_data)      
fname = os.path.join(path_main,"output_batch_03_1D_input_%s_%s.xlsx" % (OKid,outloc))
appended_data.to_excel(fname)    
