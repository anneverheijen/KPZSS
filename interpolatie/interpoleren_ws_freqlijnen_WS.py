# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 14:54:31 2022

@author: ESB
"""
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

switch_excel = False
switch_plot = False

# Import input data
combinations = pd.read_excel('..\output_batch_03_compleet_c01.xlsx')
locations = gpd.read_file('..\selectie_ill_pilot_v02_WS.shp')

# Import results
dikeheight = pd.read_excel('..\Scenarios.xlsx')
freq = pd.read_excel('Waterstand_overzicht.xlsx')

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

# Frequencies to extrapolate
extrapolate_freqs = [8.00E-06, 4.00E-06, 1.20E-06, 1.20E-07]

for index, row in dikeheight.iterrows():
    print(index)
    location = locations[locations['FC_VakID'] == row.FC_VakID]
    if len(location) > 1:
        print(f'Error at row {index}')
    data = {}
    data['werkmap'] = 'werkmap'
    data['database'] = 'WBI2017_Westerschelde_29-2_v03' if '29' in location.FC_VakID else 'WBI2017_Westerschelde_32-4_v03' if '32' in location.FC_VakID else 'WBI2017_Westerschelde_30-3_v03'
    data['vakid'] = str(row.OkaderId)
    data['locatie'] = location.Name.iloc[0]
    data['bertype'] = 'waterstand'
    data['profiel'] = '-'
    data['berekening'] = row.Naam
    freqs = freq[freq['Locatie'] == location.Name.iloc[0]]
    
    # Create prob's and wl (correct for sealevel rise (in cm))
    prob = 1/freqs.iloc[:,9]
    wl = freqs.iloc[:,10] + float(row.ZSS)/100
    for i, value in enumerate(prob):
        data['F{:03d}'.format(i+1)] = prob.iloc[i]
        data['H{:03d}'.format(i+1)] = wl.iloc[i]
    
    prob = prob.values
    wl = wl.values
    prob_old = prob
    wl_old = wl
    wl_end = wl[-1]
    
    dwl = wl[-1] - wl[0]
    dt_log = np.log10(prob[-1]) - np.log10(prob[0])
    
    for i, extrapolate_freq in enumerate(extrapolate_freqs):
        data['F{:03d}'.format(i+26)] = extrapolate_freq
        prob = np.append(prob, [extrapolate_freq])
        data['H{:03d}'.format(i+26)] = wl_end + (np.log10(extrapolate_freq) - np.log10(1/freqs.iloc[-1,9]))/dt_log*dwl
        wl = np.append(wl, [wl_end + (np.log10(extrapolate_freq) - np.log10(1/freqs.iloc[-1,9]))/dt_log*dwl])
    plt.plot(prob, wl);plt.xscale('log');plt.gca().invert_xaxis()
    plt.plot(prob_old, wl_old)
    plt.show()
    freq_result = freq_result.append(data, ignore_index=True)
    # plt.plot(prob, wl);plt.xscale('log');plt.gca().invert_xaxis()

if switch_excel:
    freq_result.to_excel('Waterlevel_frequencies_processed_engt2.xlsx', index=False)
