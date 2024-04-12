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

path_main   = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\tests\batch_03'
dirs        = list_files_folders.list_folders(path_main, dir_incl='WS', startswith = True, endswith = False)

#%% Read output for selected locations and export to Excel

OKids   = [29001012, 29001013, 29001014, 29001015, 29001016, 29003001, 30003022, 32003005]
X       = [30004, 29279, 29053, 28542, 28005, 22640, 46655, 56465]
Y       = [385052, 384936, 384859, 385066, 385787, 391705, 378812, 380452]

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
appended_data.to_excel(os.path.join(path_main,'output_batch_03_compleet.xlsx'))    

#%% Read output for pilot locations and upload to ANT



