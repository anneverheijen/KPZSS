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

dirs    = {'data': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\01_tests\batch_03',
           'hydra': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\01_tests\batch_03\input',
           'interpolatie': r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\01_tests\batch_03\interpolatie'}

files   = {'swan': 'DikeHeight.xlsx',
           'hydra': 'hydra_output_totaal_dsn_mod.xlsx',
           'interpolatie': 'interpolatie_new.xlsx',
           'scenarios': 'scenarios.xlsx'}

switch_plot = True
switch_excel = False

#%% Load input files

hbn_swan_all = pd.read_excel(os.path.join(dirs['data'], files['swan']))

hbn_hydra_all = pd.read_excel(os.path.join(dirs['hydra'], files['hydra']))

interpolatie = pd.read_excel(os.path.join(dirs['interpolatie'], files['interpolatie']),sheet_name = 'combined')

scenarios = pd.read_excel(os.path.join(dirs['interpolatie'], files['scenarios']),sheet_name = 'combined')

#%% Interpolatie 

# Get unique OKADER id's
OKids = hbn_swan_all['OkaderId'].unique()

output = pd.DataFrame()

### Loop over unique OKADER id's
for OKid in OKids: 
    
    # HBN values for computed scenarios
    hbn_swan_loc = hbn_swan_all[hbn_swan_all['OkaderId'] == OKid]
    
    # Get HBN hydra
    hbn_hydra_loc = hbn_hydra_all[hbn_hydra_all['OKADER VakId'] == OKid]
    
    # Prep interpolation matrix for selected OKADER id
    interpolatie_vak = interpolatie
    interpolatie_vak['vakid'] = OKid
    interpolatie_vak['Scenario'] = 0
    interpolatie_vak['Referentie'] = 0
    interpolatie_vak['Referentie_punt'] = 0
    interpolatie_vak['Werkmap'] = 'werkmap'
    interpolatie_vak['Database'] = ''
    interpolatie_vak['Locatie'] = ''
    interpolatie_vak['bertype'] = 'HBN'
    interpolatie_vak['profiel'] = '-'
    interpolatie_vak['HBN_Hydra'] = 0
    interpolatie_vak['HBN_SWAN'] = 0
    interpolatie_vak['HBN_ref'] = 0
    interpolatie_vak['delta_HBN'] = 0
    interpolatie_vak['HBN1'] = 0
    interpolatie_vak['HBN2'] = 0
    interpolatie_vak['HBN_final'] = 0
    interpolatie_vak['berekening'] = 0
    
    ### Loop over all timelines and fill scenario name and HBN
    
    # First loop over points that do not require interpolation
    for index, tijdpunt in interpolatie_vak.iterrows():
        
        if tijdpunt['IE'] == 0:
            
            # scenario name
            scen_bodem = scenarios[scenarios['Bodem'] == tijdpunt['Bodem']]
            scen = scen_bodem[scen_bodem['Punt'] == tijdpunt['Punt']]['Naam'].values[0]
            interpolatie_vak['Scenario'][index] = scen
            
            # reference scenario (to determined delta HBN)
            ref = scenarios[scenarios['Punt'] == tijdpunt['Punt']]['Referentie'].values[0]
            ref_punt = scenarios[scenarios['Naam'] == ref]['Punt'].values[0]
            interpolatie_vak['Referentie'][index] = ref
            interpolatie_vak['Referentie_punt'][index] = ref_punt
            
            # HBN from Hydra-NL
            scenstr = str(tijdpunt['Naam_Hydra'])
            hbn_hydra = hbn_hydra_loc[hbn_hydra_loc['ZSS-scenario'] == "'%s'" % scenstr]['HBN [m+NAP]']
            hbn_hydra = hbn_hydra.iloc[0]
            interpolatie_vak['HBN_Hydra'][index] = hbn_hydra        

            # HBN from SWAN 
            hbn_swan = hbn_swan_loc[hbn_swan_loc['Scenario'] == scen]['DikeHeight']
            hbn_swan = hbn_swan.iloc[0]
            interpolatie_vak['HBN_SWAN'][index] = hbn_swan
            
            # reference HBN
            hbn_ref = interpolatie_vak[interpolatie_vak['Scenario'] == ref]['HBN_SWAN'].values[0]
            interpolatie_vak['HBN_ref'][index] = hbn_ref
            
            # delta HBN
            interpolatie_vak['delta_HBN'][index] = interpolatie_vak['HBN_SWAN'][index] - interpolatie_vak['HBN_ref'][index]
            
            # for NM bodem: final HBN is HBN from Hydra
            if tijdpunt['Bodem'] == 'NM':
                interpolatie_vak['HBN_final'][index] = hbn_hydra
            else:
                interpolatie_vak['HBN_final'][index] = interpolatie_vak['HBN_Hydra'][index] + interpolatie_vak['delta_HBN'][index]    
                            
        elif tijdpunt['IE'] == 1:
            scen = 'IE'
            interpolatie_vak['Scenario'][index] = scen
 
    # First: do interpolation for INT02
    for index, tijdpunt in interpolatie_vak.iterrows():
        if tijdpunt['IE'] == 1 and tijdpunt['Punt'] == 'INT02':
            hbnsall = interpolatie_vak[interpolatie_vak['Bodem'] == tijdpunt['Bodem']]
            hbn1s = hbnsall[hbnsall['Punt'] == tijdpunt['P1']]['HBN_final']
            hbn1 = hbn1s.iloc[0]
            hbn2s = hbnsall[hbnsall['Punt'] == tijdpunt['P2']]['HBN_final']
            hbn2 = hbn2s.iloc[0]
            interpolatie_vak['HBN1'][index] = hbn1
            interpolatie_vak['HBN2'][index] = hbn2
            interpolatie_vak['HBN_final'][index]  = interpolatie_vak['HBN1'][index]*interpolatie_vak['Fac1'][index] + interpolatie_vak['HBN2'][index]*interpolatie_vak['Fac2'][index]
    
    # Second: do interpolation for EXT02
    for index, tijdpunt in interpolatie_vak.iterrows():
        if tijdpunt['IE'] == 1 and tijdpunt['Punt'] == 'EXT02':
            hbnsall = interpolatie_vak[interpolatie_vak['Bodem'] == tijdpunt['Bodem']]
            hbn1s = hbnsall[hbnsall['Punt'] == tijdpunt['P1']]['HBN_final']
            hbn1 = hbn1s.iloc[0]
            hbn2s = hbnsall[hbnsall['Punt'] == tijdpunt['P2']]['HBN_final']
            hbn2 = hbn2s.iloc[0]
            interpolatie_vak['HBN1'][index] = hbn1
            interpolatie_vak['HBN2'][index] = hbn2
            interpolatie_vak['HBN_final'][index]  = interpolatie_vak['HBN1'][index]*interpolatie_vak['Fac1'][index] + interpolatie_vak['HBN2'][index]*interpolatie_vak['Fac2'][index]
    
    # Third: do inter/extrapolation for other points
    for index, tijdpunt in interpolatie_vak.iterrows():
        if tijdpunt['IE'] == 1 and tijdpunt['Punt'] !='INT02' and tijdpunt['Punt'] !='EXT02':
            hbnsall = interpolatie_vak[interpolatie_vak['Bodem'] == tijdpunt['Bodem']]
            hbn1s = hbnsall[hbnsall['Punt'] == tijdpunt['P1']]['HBN_final']
            hbn1 = hbn1s.iloc[0]
            hbn2s = hbnsall[hbnsall['Punt'] == tijdpunt['P2']]['HBN_final']
            hbn2 = hbn2s.iloc[0]
            interpolatie_vak['HBN1'][index] = hbn1
            interpolatie_vak['HBN2'][index] = hbn2
            interpolatie_vak['HBN_final'][index]  = interpolatie_vak['HBN1'][index]*interpolatie_vak['Fac1'][index] + interpolatie_vak['HBN2'][index]*interpolatie_vak['Fac2'][index]
    
    # add berekening name
    for index, tijdpunt in interpolatie_vak.iterrows():
        tijdlijn = tijdpunt['Tijdlijn']
        zichtjaar = tijdpunt['Zichtjaar']
        ZSS = tijdpunt['ZSS']
        berekening = "%s_%s_%d_%s" % (tijdlijn, zichtjaar, ZSS, tijdpunt['Bodem'])
        interpolatie_vak['berekening'][index] = berekening
        
    # plot results
    tijdlijnen = interpolatie_vak.Tijdlijn.unique()
    bodems = interpolatie_vak.Bodem.unique()
    for bodem in bodems:
        fig = plt.figure()
        for tijdlijn in tijdlijnen:
            tl_all = interpolatie_vak[interpolatie_vak['Bodem'] == bodem]
            x = tl_all[tl_all['Tijdlijn'] == tijdlijn]['Zichtjaar']
            y = tl_all[tl_all['Tijdlijn'] == tijdlijn]['HBN_final']
            y_hydra = tl_all[tl_all['Tijdlijn'] == tijdlijn]['HBN_Hydra']
            plt.plot(x,y,label=tijdlijn)
            plt.plot(x,y_hydra,'k.')
        plt.plot(2023,0,'k.',label='Hydra-NL')
        plt.legend(loc = 'upper left')
        plt.xlabel('Zichtjaar')
        plt.ylabel('HBN (m) +NAP')
        # plt.title("%s | HBN | %s"% (OKid, bodem))
        plt.title("%s | HBN | %s"% (OKid, bodem))
        plt.style.use('ggplot')
        if OKid == 3003002 or OKid == 6003036:
            plt.ylim(3, 15)
            plt.yticks(np.arange(3, 15.01, 1)) 
        else:
            plt.ylim(8, 20)
            plt.yticks(np.arange(8, 20.01, 1)) 
        # save plot
        if switch_plot:
            fname = "output_%s_%d.png" % (bodem, OKid)
            savename = os.path.join(dirs['data'],fname)
            save_plot.save_plot(fig, savename, incl_wibo = False, dpi = 300, 
                      change_size = False, figwidth = 8, figheight = 6)
            
        plt.close()
        
    output = output.append(interpolatie_vak, ignore_index=True)

if switch_excel:      
    fname = 'HBN_tijdlijnen_combined.xlsx'
    output.to_excel(os.path.join(dirs['data'],fname))  
