# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 10:47:51 2022

@author: ENGT2
"""

#%% Import 

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from hmtoolbox.WB_basic import save_plot

#%% Settings

dirs    = {'data': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\tests\batch_03',
           'interpolatie': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\tests\batch_03\interpolatie'}

files   = {'HBN_raw': 'DikeHeight.xlsx',
           'interpolatie': 'interpolatie.xlsx',
           'scenarios': 'scenarios.xlsx'}

Hydra = {'OkaderId': [29001012, 29001013, 29001014, 29001015, 29001016, 29003001, 30003022, 32003005],
            'HBN':      [8.448, 6.831, 7.016, 11.838, 7.865, 8.864, 6.511, 7.442]}

Hydr = pd.DataFrame.from_dict(Hydra)

bodem = 'NM' # alle bodemscenario's

switch_plot = True
switch_excel = False

#%% Load input files

HBN_raw = pd.read_excel(os.path.join(dirs['data'], files['HBN_raw']))

interpolatie = pd.read_excel(os.path.join(dirs['interpolatie'], files['interpolatie']),sheet_name = bodem)

scenarios = pd.read_excel(os.path.join(dirs['interpolatie'], files['scenarios']),sheet_name = bodem)

#%% Interpolatie 

# Get unique OKADER id's
OKids = HBN_raw['OkaderId'].unique()

output = pd.DataFrame()

### Loop over unique OKADER id's
for OKid in OKids: 
    
    # HBN values for computed scenarios
    result = HBN_raw[HBN_raw['OkaderId'] == OKid]
    
    # Get HBN hydra
    hbn_hydra = Hydr[Hydr['OkaderId'] == OKid]['HBN']
    hbn_hydra = hbn_hydra.iloc[0]
    
    # Prep interpolation matrix for selected OKADER id
    interpolatie_vak = interpolatie
    interpolatie_vak['vakid'] = OKid
    interpolatie_vak['Scenario'] = 0
    interpolatie_vak['HBN1'] = 0
    interpolatie_vak['HBN2'] = 0
    interpolatie_vak['Bodem'] = bodem
    interpolatie_vak['Werkmap'] = 'werkmap'
    interpolatie_vak['Database'] = ''
    interpolatie_vak['Locatie'] = ''
    interpolatie_vak['bertype'] = 'HBN'
    interpolatie_vak['profiel'] = '-'
    interpolatie_vak['berekening'] = 0
    interpolatie_vak['delta_HBN'] = 0
    interpolatie_vak['HBN_final'] = 0
    
    ### Loop over all timelines and fill scenario name and HBN
    
    # No inter/extrapolation needed
    for index, tijdpunt in interpolatie_vak.iterrows():
        if tijdpunt['IE'] == 0:
            scen = scenarios[scenarios['Punt'] == tijdpunt['Punt']]['Naam'].values[0] 
            hbn = result[result['Scenario'] == scen]['DikeHeight']
        elif tijdpunt['IE'] == 1:
            scen = 'IE'
            hbn = 0
        interpolatie_vak['Scenario'][index] = scen
        interpolatie_vak['HBN'][index] = hbn

    # First: do inter/extrapolation for INT02!
    ix = interpolatie_vak[interpolatie_vak['Punt'] == 'INT02'].index.values
    hbn1s = interpolatie_vak[interpolatie_vak['Punt'] == interpolatie_vak['P1'][ix[0]]]['HBN']
    hbn1 = hbn1s.iloc[0]
    hbn2s = interpolatie_vak[interpolatie_vak['Punt'] == interpolatie_vak['P2'][ix[0]]]['HBN']
    hbn2 = hbn2s.iloc[0]
    interpolatie_vak['HBN1'][[ix[0]]] = hbn1
    interpolatie_vak['HBN2'][[ix[0]]] = hbn2
    interpolatie_vak['HBN'][[ix[0]]]  = interpolatie_vak['HBN1'][[ix[0]]]*interpolatie_vak['Fac1'][[ix[0]]] + interpolatie_vak['HBN2'][[ix[0]]]*interpolatie_vak['Fac2'][[ix[0]]]

    # Second: do inter/extrapolation for other points
    for index, tijdpunt in interpolatie_vak.iterrows():
        if tijdpunt['IE'] == 1 and tijdpunt['Punt'] !='INT02':
            hbn1s = interpolatie_vak[interpolatie_vak['Punt'] == tijdpunt['P1']]['HBN']
            hbn1 = hbn1s.iloc[0]
            hbn2s = interpolatie_vak[interpolatie_vak['Punt'] == tijdpunt['P2']]['HBN']
            hbn2 = hbn2s.iloc[0]
            interpolatie_vak['HBN1'][index] = hbn1
            interpolatie_vak['HBN2'][index] = hbn2
            interpolatie_vak['HBN'][index]  = interpolatie_vak['HBN1'][index]*interpolatie_vak['Fac1'][index] + interpolatie_vak['HBN2'][index]*interpolatie_vak['Fac2'][index]
    
    hbn_ref = interpolatie_vak['HBN'][0]
    # add berekening name and determine delta_HBN
    for index, tijdpunt in interpolatie_vak.iterrows():
        tijdlijn = tijdpunt['Tijdlijn']
        zichtjaar = tijdpunt['Zichtjaar']
        ZSS = tijdpunt['ZSS']
        berekening = "%s_%s_%d_%s" % (tijdlijn, zichtjaar, ZSS, bodem)
        delta_hbn = tijdpunt['HBN'] - hbn_ref
        interpolatie_vak['delta_HBN'][index] = delta_hbn
        interpolatie_vak['berekening'][index] = berekening
        interpolatie_vak['HBN_final'][index] = interpolatie_vak['delta_HBN'][index] + hbn_hydra
        
    # plot results
    tijdlijnen = interpolatie_vak.Tijdlijn.unique()
    fig = plt.figure()
    for tijdlijn in tijdlijnen:
        x = interpolatie_vak[interpolatie_vak['Tijdlijn'] == tijdlijn]['Zichtjaar']
        y = interpolatie_vak[interpolatie_vak['Tijdlijn'] == tijdlijn]['HBN']
        plt.plot(x,y,label=tijdlijn)
        plt.legend(loc = 'upper left')
        plt.xlabel('Zichtjaar')
        plt.ylabel('HBN (m) +NAP')
        plt.title("%s | HBN | %s"% (OKid, bodem))
        plt.style.use('ggplot')
        plt.ylim(5, 15)
        plt.yticks(np.arange(5, 15, 1)) 

    # save plot
    if switch_plot:
        fname = "output_%s_%d.png" % (bodem, OKid)
        savename = os.path.join(dirs['data'],fname)
        save_plot.save_plot(fig, savename, incl_wibo = False, dpi = 300, 
                  change_size = False, figwidth = 8, figheight = 6)
    plt.close()
    
    output = output.append(interpolatie_vak, ignore_index=True)

if switch_excel:      
    fname = "HBN_tijdlijnen_%s.xlsx" % (bodem)
    output.to_excel(os.path.join(dirs['data'],fname))  
