# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:14:52 2022

This is a script to calculate the DikeHeight (HBN) based on the overtopping formula for the Waddenzee (production)

@author: ESB

1. Import modules
2. Set paths
3. Load variables and create new dataframe for output
4. For every combination of variables the overtopping discharge is calculated
5. For every combination a DikeHeight is determined
6. Save excel

"""

# import modules
import os
import geopandas as gpd
import pandas as pd
import numpy as np
from overtopping import overtopping

# settings
path_input      = r'/project/130991_Systeemanalyse_ZSS/5.Results/SWAN/WZ/concept02/output_productie_combined_WZ_v02.xlsx'
path_locations  = r'/project/130991_Systeemanalyse_ZSS/2.Data/GIS_TEMP/okader_fc_hydra_unique_handedit_WZ_v3_coords.shp'
path_out        = r'/project/130991_Systeemanalyse_ZSS/5.Results/SWAN/WZ/concept02'

save_excel = True

# load data
combinations = pd.read_excel(path_input)
locations = gpd.read_file(path_locations)

# create new dataframe
dikeheight = pd.DataFrame({'OkaderId':[],
                           'FC_VakID':[],
                           'Scenario':[],
                           'DikeHeight':[]})

for index, combination in combinations.iterrows():
    print(f'Calculating combination {index}')

    # Combine with locations (could be multiple)
    vakid = locations[locations['VakId']==str(combination.OkaderId)]
    for location_index in range(len(vakid)):
        location = vakid.iloc[location_index]

        # Variables for overtopping discharge formula
        Hm0 = combination.Hsig
        Tm = combination.Tm_10
        slope = 1/float(location.FC_Tld[-1])
        yb = float(location.y_b)
        betaw = abs(int(location.FC_DN)-combination.Dir)
        yf = 1
        yv = 1
        
        # Estimate overtopping discharge every cm 
        Rc = np.arange(25,-0.02,-0.01)
        q = np.zeros(Rc.shape)
        
        # if set water-level to zero if -99 value
        if combination.Watlev < 0:
            combination.Watlev = 0

        # Calculate overtopping
        for i, RC in enumerate(Rc):
            q[i] = overtopping(np.array(Hm0),np.array(Tm),np.array(slope),np.array(RC), 
                        betaw = betaw, yf = yf, yb = yb, yv = yv, 
                        ed = 2007, ctype = 'det')

            # Stop if overtopping discharge reaches limit as given in input
            if q[i] > location.FC_q/1000:
                break
        
        #Calculate dikeheight
        DikeHeight = combination.Watlev + Rc[i-1]
        dikeheight = dikeheight.append({'OkaderId':combination.OkaderId,
                                        'FC_VakID': location.FC_VakID,
                                        'Scenario': combination.Scenario,
                                        'DikeHeight': DikeHeight}, ignore_index=True)

# Write results
if save_excel: 
    dikeheight.to_excel(os.path.join(path_out,'DikeHeight.xlsx'), index=False)