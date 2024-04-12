 # -*- coding: utf-8 -*-
"""
Created on Thu May 14 08:32:24 2020

This is a script to create hydra-nl profiles (.PRFL-files, based on a csv) and the accompanied csv-file used by hydra-nl

@author: BADD

The following steps are done:
1. Specify:
   1. Output location
   2. The location of the csv
2. Create .PRFL
3. Create .csv

"""

# Import modules
from pathlib import Path
import csv
import os
import pandas
import numpy as np


# Set paths
profile_dir = Path(r'C:\MyPrograms\Hydra-NL_KP_ZSS\profielen_productie_WZ')
os.chdir(profile_dir)
data_profielen = pandas.read_csv(r'D:\Users\BADD\Desktop\KP ZSS\GIS-WZ\okader_fc_hydra_unique_handedit_WZ_v2.csv')

# modify data, for example talud: '1op5' naar 5
data_profielen['FC_Tld'] = data_profielen['FC_Tld'].str[-1:]

count = 0

# loop over input csv to create profiles    
for i in range(0,len(data_profielen)):
    count += 1

    file = open(f"%s.prfl" %data_profielen['VakId'].loc[i],"w")
    txt=['VERSIE    4.0',
        'ID'  f'   %s' %data_profielen['VakId'].loc[i],
        '',
        f'RICHTING	%.2f'  %data_profielen['FC_DN'].loc[i],
        '',
        'DAM   0',
        'DAMHOOGTE     0',
        '',
        'VOORLAND     0',  
        '',    
        'DAMWAND  0',           

        f'KRUINHOOGTE  %.2f'   %data_profielen['FC_KH'].loc[i],


        'DIJK     2',

        f'-%.2s0.000  0.000 1.000' %data_profielen['FC_Tld'].loc[i],
        '0.000	10.000	1.000',
        '', 
        'MEMO', 
        '', 
        '']
    file.write('\n'.join(txt))    
    file.close()

    del file, txt    
        

# loop over input csv to create hydra-nl csv to 'call' the profiles
filecsv = r"D:\Users\BADD\Desktop\KP ZSS\profielen_productie_WZ.csv"
with open(filecsv, 'w') as f:
    f.write("Locatie;X-coordinaat;Y-coordinaat;Profiel;Directory\n")

    for i in range(0,len(data_profielen)):
        f.write(f"{data_profielen['Name'].loc[i]};{data_profielen['XCoordinat'].loc[i]};{data_profielen['YCoordinat'].loc[i]};{data_profielen['VakId'].loc[i]};")
        f.write("..\\profielen_productie_WZ\n")
