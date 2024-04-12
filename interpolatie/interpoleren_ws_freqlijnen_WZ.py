# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 14:54:31 2022

@author: ESB
"""

#%% Modules

import os
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.interpolate

#%% Settings

path_locations = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\01_tests\batch_01\input\selectie_ill_pilot_v03_WZ.shp'
path_ws = r'z:\130991_Systeemanalyse_ZSS\5.Results\Hydra-NL_WS\Waddenzee_WS.xlsx'

path_out = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\01_tests\batch_03'

switch_excel = False
switch_plot = False

corr_2023_1995 = 0.05

# Frequencies to extrapolate
freqs = [1/10, 1/30, 1/42, 1/50, 1/100, 1/300, 1/417, 1/500, 1/833, 1/1000, 
         1/1250, 1/2500, 1/3000, 1/4167, 1/5000, 1/8333, 1/10000, 1/12500, 
         1/25000, 1/30000, 1/37500, 1/41667, 1/50000, 1/83333, 1/1.00E+05, 
         8.00E-06, 4.00E-06, 1.20E-06, 1.20E-07]

scenarios = ['Laag_2023_0', 'Laag_2050_25', 'Laag_2100_50', 'Laag_2150_75', 
             'Laag_2200_100', 'Gematigd_2023_0', 'Gematigd_2050_25', 
             'Gematigd_2100_75', 'Gematigd_2150_131', 'Gematigd_2200_200', 
             'Extreem_2023_0', 'Extreem_2050_25', 'Extreem_2100_100', 
             'Extreem_2150_180', 'Extreem_2200_300', 'Zeer extreem_2023_0', 
             'Zeer extreem_2050_50', 'Zeer extreem_2100_200', 
             'Zeer extreem_2150_350', 'Zeer extreem_2200_500']

#%% Import data

# Import input data
locations = gpd.read_file(path_locations)

# Import results
df_water = pd.read_excel(path_ws)

# Create output Excel
freq_result = pd.DataFrame({'werkmap': [], 'database': [], 'vakid': [], 
                          'locatie': [], 'bertype': [], 'profiel': [], 
                          'berekening': [], 'F001': [], 'H001': [], 'F002': [],
                          'H002': [], 'F003': [], 'H003': [], 'F004': [], 
                          'H004': [], 'F005': [], 'H005': [], 'F006': [], 
                          'H006': [], 'F007': [], 'H007': [], 'F008': [], 
                          'H008': [], 'F009': [], 'H009': [], 'F010': [], 
                          'H010': [], 'F011': [], 'H011': [], 'F012': [], 
                          'H012': [], 'F013': [], 'H013': [], 'F014': [], 
                          'H014': [], 'F015': [], 'H015': [], 'F016': [], 
                          'H016': [], 'F017': [], 'H017': [], 'F018': [], 
                          'H018': [], 'F019': [], 'H019': [], 'F020': [], 
                          'H020': [], 'F021': [], 'H021': [], 'F022': [], 
                          'H022': [], 'F023': [], 'H023': [], 'F024': [], 
                          'H024': [], 'F025': [], 'H025': [], 'F026': [], 
                          'H026': [], 'F027': [], 'H027': [], 'F028': [], 
                          'H028': [], 'F029': [], 'H029': []})

def interpolate(x, x_interpolate, y_interpolate):
    interp = scipy.interpolate.interp1d(x_interpolate, y_interpolate, fill_value="extrapolate")
    return np.round(interp(np.log10(x)), 3)

for index, row in locations.iterrows():
    print(index)
    location = row.FC_VakID
    hydraulic = df_water[df_water.Locatie==row.Name]
    # if len(location) > 1:
    #     print(f'Error at row {index}')
    for scenario in scenarios:
        data = {}
        data['werkmap'] = 'werkmap'
        data['database'] = hydraulic.Randvoorwaardendatabase
        data['vakid'] = str(row.FC_VakID)
        data['locatie'] = hydraulic.Locatie.iloc[0]
        data['bertype'] = 'waterstand'
        data['profiel'] = '-'
        data['berekening'] = scenario
        
        break
        
        # Create prob's and wl (correct for sealevel rise (in cm))
        x_interpolate = list(reversed(sorted((1/hydraulic.iloc[:,9]).tolist())))
        x_log_interpolate = np.log10(x_interpolate)
        
        if '2023' in scenario:
            zss = 0
        else:
            zss = float(scenario.split('_')[-1])/100 - corr_2023_1995
            
        y_interpolate = sorted((hydraulic.iloc[:,10] + float(scenario.split('_')[-1])/100).tolist())
        x = []
        y = []
        for i, freq in enumerate(freqs):
            data['F{:03d}'.format(i+1)] = freq
            data['H{:03d}'.format(i+1)] = interpolate(freq, x_log_interpolate, y_interpolate)
            x.append(freq)
            y.append(data['H{:03d}'.format(i+1)])
        
        if switch_plot:
            plt.figure()
            plt.plot(x,y);plt.plot(x_interpolate,y_interpolate);plt.xscale('log');plt.gca().invert_xaxis()
            plt.show()

        freq_result = freq_result.append(data, ignore_index=True)

if switch_excel:
    freq_result.to_excel(os.path.join(path_out,'Waterlevel_frequencies_processed_waddenzee.xlsx'), index=False)
