# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 09:10:05 2022

@author: VERA7
This script is used during the pilot to fill the illustratiepunten
from the berekeningen. It follows these steps:
    1 - get the berekeningen (calculations) that are relevant 
        (in pilot all, in production this should be linked to session)
    2 - per calculation we need to adhere the date we want and fill the illustratiepunten
        tabel
"""
# import python modules
import os
import numpy as np

# import ant functions
from ant import ant_helper_functions as ant_funcs

# import kp zss functions
from reader import lees_invoerbestand, lees_uitvoerhtml, lees_illustratiepunten, lees_ofl

# specify a local temporary folder
temp_folder = 'tmp'

# check if this folder exists, otherwise make it
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# make api connection
ant_connection = ant_funcs.get_api_connection()

# specify where to put it
project_name = 'Systeemanalyse Waterveiligheid'
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
table_name_illustratiepunten = 'IPM_illustratiepunten'
table_name_berekeningen = 'DBM_HRD_berekening'
table_name_database = 'DBM_HR_database'
table_name_database_set = 'DBM_HR_database_set'
table_name_region = 'Locatie_Regio'
table_name_vak = 'Locatie_Vakken'

# get these id's
table_id_illustratiepunten = ant_funcs.get_table_id(ant_connection, project_id, table_name_illustratiepunten)
table_id_berekeningen = ant_funcs.get_table_id(ant_connection, project_id, table_name_berekeningen)
table_id_database = ant_funcs.get_table_id(ant_connection, project_id, table_name_database)
table_id_database_set = ant_funcs.get_table_id(ant_connection, project_id, table_name_database_set)
table_id_region = ant_funcs.get_table_id(ant_connection, project_id, table_name_region)
table_id_vak = ant_funcs.get_table_id(ant_connection, project_id, table_name_vak)

# get the records
records_illustratiepunten = ant_connection.records_read(project_id, table_id_illustratiepunten)
records_berekeningen = ant_connection.records_read(project_id, table_id_berekeningen)
records_database = ant_connection.records_read(project_id, table_id_database)
records_database_set = ant_connection.records_read(project_id, table_id_database_set)
records_region = ant_connection.records_read(project_id, table_id_region)
records_vak = ant_connection.records_read(project_id, table_id_vak)

# %% now loop over all calculations and put relevant calculations into illustratiepunten

for calc_record in records_berekeningen:
    
    # get the region of this record and check if it is for the method ipm
    db = ant_funcs.find_id_or_record(records_database, 
                                      ['id'],
                                      [calc_record['HR_database_id']], 
                                      find_id=False)
    db_set = ant_funcs.find_id_or_record(records_database_set, 
                               ['id'],
                               [db['HR_database_set_ID']], 
                               find_id=False)
    
    region = ant_funcs.find_id_or_record(records_region, 
                               ['id'],
                               [db_set['Regio_id']], 
                               find_id=False)
    
    if not region['Methode'] == 'IPM':
        continue
    
    # find the right vak
    vak = ant_funcs.find_id_or_record(records_vak, 
                                      ['id'],
                                      [calc_record['Vak_id']], 
                                      find_id=False)
    
    # now we are processing a calculation, download the outcome
    ant_connection.download_document(project_id, table_id_berekeningen, 
                                                   calc_record['Uitvoer_file']['id'],
                                                   temp_folder)
    location_uitvoer = os.path.join(temp_folder, 
                                    f"{calc_record['Uitvoer_file']['name']}.{calc_record['Uitvoer_file']['extension']}")

    tekst = lees_uitvoerhtml(location_uitvoer)
    cips, ip = lees_illustratiepunten(tekst)
    ofl = lees_ofl(tekst)  
    
    # check if this results in 2 illustratiepunten
    if sum(ip.index == vak['Norm_frequentie']) > 1:
        # in that case, we just need the one with the heighest water level
        rel_ip = ip.loc[vak['Norm_frequentie']]
        rel_ip = rel_ip.iloc[np.argmax(rel_ip['h,teen m+NAP'])]
    # if not, we can just get the first one
    else:
        # get the relevant ip
        rel_ip = ip.loc[vak['Norm_frequentie']]
    
    # make dict to make record later    
    illustratiepunten_dict = {'HRD_berekening_id': calc_record['id'],
                              'HBN_referentie': ofl['hoogte'].loc[vak['Norm_frequentie']],
                              'Waterstand': rel_ip['h,teen m+NAP'],
                              'Windsnelheid': rel_ip['windsn. m/s'],
                              'Windrichting': rel_ip['r'],
                              'Hm0_lokaal': rel_ip['Hm0,teen m'],
                              'Tm-1,0_lokaal': rel_ip['Tm-1,0,t s'],
                              'Golfrichting_lokaal': rel_ip['golfr graden'],
                              'Bijdrage_overschrijdingsfrequentie': rel_ip['bijdrage ov. freq (%)'],
                              'Berm_aanwezig': True}
    
    ant_connection.record_create(project_id, table_id_illustratiepunten, illustratiepunten_dict)
    
    # remove output, just for sanity
    os.remove(location_uitvoer)

# remove temp folder as well
os.remove(temp_folder)
