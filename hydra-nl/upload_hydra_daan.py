# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 12:04:36 2022

@author: VERA7 + BADD
The following steps are done
1. Specify:
   1. Which session you are working on (name);
   2. Which task (block) you are working on (name);
   3. which table you want to put your results in at top of the script;
2. Get the task in the session;
3. Set it on processing (just because we can);
4. Upload the data:
    TODO: be more specific @ BADD
5. Close the task. 
"""
# import python modules
# from curses import nl
import datetime
import os
from re import X
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from pathlib import Path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import own modules
from ant import ant_helper_functions as ant_funcs
from hydra_ant_berekeningen import zss_scenario

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'

# step 1: specify 
session_name = 'dummy'
task_name = 'Hydra Berekeningen'
output_table = 'DBM_HRD_berekening'


# %% step 2: get the job in the session
# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
signed_in_user_uuid = ant_connection._make_api_request('user', 'GET')['id']

table_id = ant_funcs.get_table_id(ant_connection, project_id, output_table)
region_records = ant_connection.records_read(project_id, ant_funcs.get_table_id(ant_connection, project_id, 'Locatie_Regio'))
vakken_records = ant_connection.records_read(project_id, ant_funcs.get_table_id(ant_connection, project_id, 'Locatie_Vakken'))
stack_records = ant_connection.records_read(project_id, ant_funcs.get_table_id(ant_connection, project_id, 'STACK_file'))
DBM_HR_database_records = ant_connection.records_read(project_id, ant_funcs.get_table_id(ant_connection, project_id, 'DBM_HR_database'))

task_dict, job = ant_funcs.find_task(ant_connection, project_id, signed_in_user_uuid, session_name,
             task_name)

# %% step 3: set task to pending
datestring = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
ant_connection.task_respond(task_id=task_dict['id'], 
                          status='processing',
                          response=f"processing at {datestring}", 
                          appendix=None,
                          assigned_user=signed_in_user_uuid, #can be removed once implemented in ANT
                          due_date=task_dict['due_date']) #can be removed once implemented in ANT

# # %% step x: import needed files
okader_norm_csv = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\koppelingen\Pf_Vak_Eis_20220718.csv")
df_hydra_definition = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\koppelingen\OKADER_FC_Hydra_attributes_filtered.csv")
hydra_output = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\output\HBN\hydra_output_totaal_dsn_edit.csv", delimiter=';')
afvoerstatistiek = r"D:\Users\BADD\Desktop\KP ZSS\overig\test.txt"
base_folder = r"C:\MyPrograms\Hydra-NL_KP_ZSS\backup werkmap 13092022 - WZ KW dsn-eis"

# # %% step 4: do a simple upload to output table
# table_id = ant_funcs.get_table_id(ant_connection, project_id, output_table)


for i in range(len(hydra_output)):
    zichtjaar, zss = zss_scenario(hydra_output['ZSS-scenario'].loc[i])    
    
    if Path(hydra_output['Uitvoerbestand'].loc[i]).exists():

    # freq_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\ffq.txt')
    # invoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\invoer.hyd')
    # uitvoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.html')
    # log_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.log')
    # print((hydra_output['Uitvoerbestand'].loc[i].split('\\')[-5] + '.zip'))
    # print(str(hydra_output['OKADER VakId'].loc[i]))
   
        if 'Waddenzee' in hydra_output['Uitvoerbestand'].loc[i]:
            
                string_to_match = ['_KW', '_WS']

                # for substring in string_to_match:
                #     if not substring in hydra_output['Uitvoerbestand'].loc[i].split('\\')[-1]:
                if not any(x in hydra_output['Uitvoerbestand'].loc[i].split('\\')[-1] for x in string_to_match):
                        freq_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\ffq.txt')
                        invoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\invoer.hyd')
                        uitvoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.html')
                        log_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.log')               


                        result_dict = {
                                'Naam'  : 'WZ_' + hydra_output['Uitvoerbestand'].loc[i].split('\\')[-2],
                                'Vak_id'  : ant_funcs.find_ids_or_records(vakken_records, ['HRD_locatie_id', 'OKADER_vak_id'], [hydra_output['HYD_location_name'].loc[i], hydra_output['OKADER VakId'].loc[i]]),
                                'HR_database_id' : ant_funcs.find_ids_or_records(DBM_HR_database_records, ['STACK_file_ID'], [ant_funcs.find_ids_or_records(stack_records, ['filename'], [(hydra_output['Uitvoerbestand'].loc[i].split('\\')[-5] + '.zip')])]),
                                'Zeespiegelstijging_CM'  : float(zss),
                                'Afvoerstatistiek'  : ant_connection.parse_document(afvoerstatistiek, 'test.txt'),
                                'Type berekening'  : 'HBN',
                                'Basis of Gevoeligheid'  : 'Basis',
                                'Zichtjaar'  :  zichtjaar,
                                'Bijzonderheden'  : 'n.v.t.',
                                'freq_file'  : ant_connection.parse_document(freq_file, 'ffq.txt'),
                                'Invoer_file'  : ant_connection.parse_document(invoer_file, 'invoer.hyd'),
                                'Uitvoer_file'  : ant_connection.parse_document(uitvoer_file, 'uitvoer.html'), 
                                'Log_file'  : ant_connection.parse_document(log_file, 'uitvoer.log'),
                                'Goedgekeurd'  :  False,
                                'Opmerkingen'  : 'Pilot Waddenzee'}

                        ant_connection.record_create(project_id, table_id, result_dict, session=job['session'])

    #toevoegen elif voor Hollandse Kust
    print('Record', i+1, 'toegevoegd')
    break


# # create a dict with a result. columns should have name of columns in output table
# result_dict = {'id': '0f91fcab-7c8d-4ab1-abea-da6b8328ba2b',
#              'Naam': 'Westerschelde_32001001_KPZSS_2200_Laag_5',
#              'Vak_id': '2360914e-5a52-4064-9d6b-80a9926bbfdb',
#              'HR_database_id': '6eda1d16-952f-412b-81c1-22edfe03c92f',
#              'Zeespiegelstijging_CM': 100,
#              'Afvoerstatistiek': None,
#              'Type berekening': 'HBN',
#              'Basis of Gevoeligheid': 'Basis',
#              'Zichtjaar': 2200,
#              'Bijzonderheden': 'n.v.t.',
#              'Goedgekeurd': False,
#              'Opmerkingen': 'testdata',
#              'Uitvoer_file' : ant_connection.parse_document(r'd:\Users\VERA7\Downloads\uitvoer.html', 'uitvoer.html')}

# ant_connection.record_create(project_id, table_id, result_dict, session=job['session'])

# %% step 5: finish the task
# ant_connection.job_finish(project_id, job['id'])
