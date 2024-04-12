# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 13:07:02 2022

This is a script to plot the processed waterstandsfrequentielijnen for the Westerschelde

@author: ENGT2

1. Import modules
2. Set paths and variables
3. Plot waterstandsfrequentielijnen based on timelines and scenarionames
"""
# import modules
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hmtoolbox.WB_basic import save_plot

#%% Settings

path_input = r'z:\130991_Systeemanalyse_ZSS\5.Results\Hydra-NL_WS\Frequentielijnen'
filename = 'Waterlevel_frequencies_processed_waddenzee.xlsx'

path_out = r'Z:\130991_Systeemanalyse_ZSS\5.Results\Hydra-NL_WS\Frequentielijnen\figures_WZ'

H = ['H001', 'H002', 'H003', 'H004', 'H005', 'H006', 'H007', 'H008', 'H009', 'H010',
     'H011', 'H012', 'H013', 'H014', 'H015', 'H016', 'H017', 'H018', 'H019', 'H020', 
     'H021', 'H022', 'H023', 'H024', 'H025', 'H026', 'H027', 'H028', 'H029']


F = ['F001', 'F002', 'F003', 'F004', 'F005', 'F006', 'F007', 'F008', 'F009', 'F010',
     'F011', 'F012', 'F013', 'F014', 'F015', 'F016', 'F017', 'F018', 'F019', 'F020', 
     'F021', 'F022', 'F023', 'F024', 'F025', 'F026', 'F027', 'F028', 'F029']

Namen = ['Laag','Gematigd','Extreem','Zeer extreem']

switch_plot = True

#%% Read tijdlijnen

tijdlijnen = pd.read_excel(os.path.join(path_input,filename))

#%% Plot tijdlijnen

OKids = tijdlijnen['vakid'].unique()

for Naam in Namen:

    for OKid in OKids:
        
        vaksubset = tijdlijnen[tijdlijnen['vakid']==OKid]
    
        scensubset = vaksubset[vaksubset['berekening'].str.contains(Naam)]
    
        x = np.zeros(len(F)) 
        y = np.zeros(len(H)) 
        
        fig = plt.figure()
        
        for index, row in scensubset.iterrows():
            ix = 0
            for ff in F:
                x[ix] = row[ff]
                ix = ix + 1
            ix = 0
            for hh in H:
                y[ix] = row[hh]
                ix = ix + 1
            plt.plot(x,y,label=row['berekening'])
            plt.xscale('log');
            plt.gca().invert_xaxis()
            plt.legend(loc = 'upper left')
            plt.xlabel('Frequentie')
            plt.ylabel('Waterstand (m) +NAP')
            plt.title("%s | WS | %s"% (OKid, Naam))
            plt.ylim(2, 15)
            plt.yticks(np.arange(2, 15.1, 1))
            plt.style.use('ggplot')
        
        # save plot
        if switch_plot:
            fname = "wl_freqs_%s_%s.png" % (OKid, Naam)
            savename = os.path.join(path_out,fname)
            save_plot.save_plot(fig, savename, incl_wibo = False, dpi = 300, 
                      change_size = False, figwidth = 8, figheight = 6)
        plt.close('all')

