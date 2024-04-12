# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 13:27:19 2022

@author: VERA7
downloads the freq files we need for pilot
"""

# import python modules
import os
import pathlib
import pandas

# import ant functions
from ant import ant_helper_functions as ant_funcs
# make api connection
ant_connection = ant_funcs.get_api_connection()

# specify where to get pilot ids from
ill_pilot_file = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\tests\batch_03\input\selectie_ill_pilot_v02_WS.csv'
base_save_dir = pathlib.Path(os.getcwd()) / 'freq_files'

# %% specify where to read, to fill, etc
project_name = 'Systeemanalyse Waterveiligheid'
vakken_table_name = 'Locatie_Vakken'
berekeningen_table_name = 'DBM_HRD_berekening'

project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
vakken_table_id = ant_funcs.get_table_id(ant_connection, project_id, vakken_table_name)
berekeningen_table_id = ant_funcs.get_table_id(ant_connection, project_id, berekeningen_table_name)

# %% read all vakken
vakken_records = ant_connection.records_read(project_id, vakken_table_id)
berekeningen_records = ant_connection.records_read(project_id, berekeningen_table_id)

# read locations we need
ill_pilot_df = pandas.read_csv(ill_pilot_file)

# %% loop over all rows and find the freq files we need

# make a dict to keep track
exported_dict = {'vak_id' : [],
                 'zss_cm' : [],
                 'zichtjaar' : [],
                 'relative_file_loc' : []}

for index, row in ill_pilot_df.iterrows():
    
    vak_id = ant_funcs.find_ids_or_records(vakken_records, ['OKADER_vak_id'], 
                                           [str(row['VakId'])])
    print(f'processing {vak_id}')
    # we need to loop since vakken have been filled multiple times...
    ber_ids = []
    ber_records = []
    for vak in vak_id:
        result = ant_funcs.find_ids_or_records(berekeningen_records,
                                               ['Vak_id'], [vak], return_records=True)
        ber_ids.extend(result[0])
        ber_records.extend(result[1])
    
    # now loop over all the calculations
    for ber_record in ber_records:
        # fill some meta data
        exported_dict['vak_id'].append(row['VakId'])
        exported_dict['zss_cm'].append(ber_record['Zeespiegelstijging_CM'])
        exported_dict['zichtjaar'].append(ber_record['Zichtjaar'])
        
        # construct file path
        save_dir = base_save_dir / f"{row['VakId']}" / f"{ber_record['Zeespiegelstijging_CM']}_{ber_record['Zichtjaar']}"
        if not save_dir.exists():
            save_dir.mkdir(parents=True)
        
        # download the files
        ant_connection.download_document(project_id, berekeningen_table_id, 
                                                   ber_record['freq_file']['id'],
                                                   str(save_dir))
        ant_connection.download_document(project_id, berekeningen_table_id, 
                                                   ber_record['Invoer_file']['id'],
                                                   str(save_dir))
        ant_connection.download_document(project_id, berekeningen_table_id, 
                                                   ber_record['Uitvoer_file']['id'],
                                                   str(save_dir))
        ant_connection.download_document(project_id, berekeningen_table_id, 
                                                   ber_record['Log_file']['id'],
                                                   str(save_dir))
        
        # now append 
        exported_dict['relative_file_loc'].append(str(save_dir.relative_to(base_save_dir)))
    
df = pandas.DataFrame(exported_dict)  
df.to_csv(str(base_save_dir / 'freq_files.csv'), index=False, sep=';')