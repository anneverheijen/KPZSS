 # -*- coding: utf-8 -*-
"""
Created on Thu Sep 1 12:00:00 2022

This is a script to create process the hydra-nl calculations in a format suitable for KPZSS Illustratiepuntenmethode

@author: BADD

The following steps are done:
1. Import modules
2. Set paths
3. Create empty dictionairy for results
4. Loop over Hydra-NL folders with certain keywords
5. Store input- and output variables from the Hydra-NL folders

"""

# Import modules
from cmath import nan
from operator import contains, index
import string
from reader import lees_invoerbestand, lees_uitvoerhtml, lees_illustratiepunten, lees_ofl
from pathlib import Path
import os
import pandas as pd
import numpy as np

# set paths
hydra_werkmap = r"C:\MyPrograms\Hydra-NL_KP_ZSS\werkmap"
okader_norm_csv = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\koppelingen\Pf_Vak_Eis_20220718.csv", delimiter=';')
df_hydra_definition = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\GIS-WZ\okader_fc_hydra_unique_handedit_WZ_v2.csv")

# create dictionairy to store results
hydra_results = {
    'OKADER VakId':[], 
    'Uitvoerbestand':[], 
    'Terugkeertijd':[], 
    'q [m3/s/m]':[], 
    'ZSS-scenario':[], 
    'HYD_location_name':[], 
    'HYD_location_X':[], 
    'HYD_location_Y':[], 
    'Profiel':[],
    'HBN [m+NAP]':[], 
    'Zeewaterstand [m+NAP]':[], 
    'windsnelheid [m/s]':[], 
    'h, teen [m+NAP]': [], 
    'Hm0, teen [m]':[], 
    'Tm-1.0, ts':[], 
    'golfrichting [graden]':[], 
    'windrichting [graden N]':[], 
    'bijdrage ov. freq [%]':[]}


for folder in os.listdir(hydra_werkmap):

    # specify which keywords to match in hydra-nl werkmap
    string_to_match = ["Waddenzee"]

    for substring in string_to_match:
        if substring in folder:

            # find folders with string_to_match
            for root, dirs, files in os.walk(os.path.join(hydra_werkmap, folder)):
                    for file in files:

                        # based on invoer.hyd the first columns of output dictionairy are filled
                        if file.endswith('invoer.hyd'):
                            location_invoer = os.path.join(root, file)
                            invoer, terugkeertijden = lees_invoerbestand(location_invoer)
                            
                            # the entire path of profile is included in invoer.hyd, strip it to profile-name
                            profielpath = invoer['algemeen']['PROFIEL']
                            valueprofiel = profielpath.split("\\")[-1]
                            valueprofiel = valueprofiel[:-1]
                            value = valueprofiel.split(".")[0]

                            # append first columns of output dictionairy based on invoer.hyd
                            hydra_results['OKADER VakId'].append(value)
                            hydra_results['q [m3/s/m]'].append(invoer['criterium']['QCR'])
                            hydra_results['Uitvoerbestand'].append(invoer['algemeen']['UITVOERBESTAND'])
                            hydra_results['ZSS-scenario'].append(invoer['algemeen']['SCENARIONAAM'])
                            hydra_results['HYD_location_name'].append(invoer['algemeen']['LOCATIE'])
                            hydra_results['HYD_location_X'].append(invoer['algemeen']['XCOORDINAAT'])
                            hydra_results['HYD_location_Y'].append(invoer['algemeen']['YCOORDINAAT'])
                            hydra_results['Profiel'].append(valueprofiel)
                            
                            # get ondergrens doorsnede-eis for a specific vak from excel
                            for i in range(len(okader_norm_csv['VAK'])):
                                if okader_norm_csv['VAK'].loc[i] == int(value):
                                    req_terugkeertijd = okader_norm_csv['T_eis_hbn'].loc[i]


                        # based on uitvoer.html (bij meest waarschijnlijke combinatie van illustratiepunt) the other columns of our dictionairy can be filled
                        elif file.endswith('uitvoer.html'):
                            location_uitvoer = os.path.join(root, file)
                            tekst = lees_uitvoerhtml(location_uitvoer)
                            cips, ip = lees_illustratiepunten(tekst)
                            ofl = lees_ofl(tekst)

                            # check if this results in 2 illustratiepunten, only one is needed in dictionairy
                            a = (ip['bijdrage ov. freq (%)'].loc[[req_terugkeertijd][0]])
                            if a.size > 1:
                                rel_ip = ip.loc[[req_terugkeertijd][0]]
                                rel_ip = rel_ip.iloc[np.argmax(rel_ip['h,teen m+NAP'])]
                            else:
                                rel_ip = ip.loc[[req_terugkeertijd][0]]
                        
                            hydra_results['Terugkeertijd'].append(req_terugkeertijd)

                            # append the results to the dictionairy of the most probable combination in the illustratiepunt at the doorsnede eis ondergrens at the Okader VakId
                            hydra_results['HBN [m+NAP]'].append(ofl['hoogte'].loc[[req_terugkeertijd][0]])
                            hydra_results['Zeewaterstand [m+NAP]'].append(rel_ip['zeews. m+NAP'])
                            hydra_results['windsnelheid [m/s]'].append(rel_ip['windsn. m/s'])
                            hydra_results['h, teen [m+NAP]'].append(rel_ip['h,teen m+NAP'])
                            hydra_results['Hm0, teen [m]'].append(rel_ip['Hm0,teen m'])
                            hydra_results['Tm-1.0, ts'].append(rel_ip['Tm-1,0,t s'])
                            hydra_results['golfrichting [graden]'].append(rel_ip['golfr graden'])
                            hydra_results['windrichting [graden N]'].append(rel_ip['r'])
                            hydra_results['bijdrage ov. freq [%]'].append(rel_ip['bijdrage ov. freq (%)'])

# make dataframe for saving as a csv          
df = pd.DataFrame(hydra_results)
savename = os.path.join(r"D:\Users\BADD\Desktop\KP ZSS\kust\output\HBN", f"{string_to_match}" + '_HBN_new_v2.csv')
df.to_csv(savename, sep = ';', index = False)


