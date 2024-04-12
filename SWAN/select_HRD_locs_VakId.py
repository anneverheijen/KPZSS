# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:48:13 2022

@author: ENGT2
"""

# import modules

import os
import pandas as pd
import geopandas as gpd

# settings

dirs    = {'input':     r'd:\Users\ENGT2\Documents\Projects\130991 - SA Waterveiligheid ZSS\GIS\illustratiepunten_methode',
           'output':    r'd:\Users\ENGT2\Documents\Projects\130991 - SA Waterveiligheid ZSS\GIS\illustratiepunten_methode'}

files   = {'okader':    'okader_fc_hydra_unique_handedit_WS.shp',
           'hydra':     'HRD_locations_hydra_WS.shp',
           'result':    'HRD_locations_selectie_WS.csv'}

# Read locaties (OKADER vak id's)

df_okader   = gpd.read_file(os.path.join(dirs['input'],files['okader']))
df_hydra    = gpd.read_file(os.path.join(dirs['input'],files['hydra']))

# Select Hydra locs based on okader

df_hydra_sel = pd.merge(df_hydra, df_okader, left_on = 'Name', right_on = 'Name')

# Export to excel

df_hydra_sel.to_csv(os.path.join(dirs['output'],files['result']))
