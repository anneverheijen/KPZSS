# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 12:04:36 2022

@author: VERA7 + ENGT2
The following steps are done
1. Specify:
   1. Which session you are working on (name);
   2. Which task (block) you are working on (name);
   3. which table you want to put your results in at top of the script;
2. Get the task in the session;
3. Set it on processing (just because we can);
4. Do calculations and upload the data:
    TODO: be more specific @ ENGT2
5. Close the task. 
"""
# import python modules
import os
import datetime

# import own modules
from ant import ant_helper_functions as ant_funcs

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'

# step 1: specify 
session_name = 'test004'
task_name = "Genereer Tijdlijnen"
swan_1d_table = 'IPM_SWAN_1D'
swan_2d_table = 'IPM_SWAN_2D'
swan_ber_table = 'IPM_SWAN_berekening'
hr_table = 'IPM_uitvoerlocatie_golfcondities'
illustratiepunten_tabel = 'IPM_illustratiepunten'
hrd_berekeningen_tabel = 'DBM_HRD_berekening'
tijdlijn_tabel = 'TL_tijdlijnen'
frequentielijnen_tabel = 'TL_Frequentielijnen'

# specify a local temporary folder to store all calculations in 
temp_folder = os.path.join(os.getcwd(), f'tmp_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')

# check if this folder exists, otherwise make it
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
swan_ber_table_id = ant_funcs.get_table_id(ant_connection, project_id, swan_ber_table)
swan_1d_table_id = ant_funcs.get_table_id(ant_connection, project_id, swan_1d_table)
swan_2d_table_id = ant_funcs.get_table_id(ant_connection, project_id, swan_2d_table)
hr_table_id = ant_funcs.get_table_id(ant_connection, project_id, hr_table)
illustratiepunten_tabel_id = ant_funcs.get_table_id(ant_connection, project_id, illustratiepunten_tabel)
hrd_berekeningen_tabel_id = ant_funcs.get_table_id(ant_connection, project_id, hrd_berekeningen_tabel)
tijdlijn_tabel_id = ant_funcs.get_table_id(ant_connection, project_id, tijdlijn_tabel)
frequentielijnen_tabel_id = ant_funcs.get_table_id(ant_connection, project_id, frequentielijnen_tabel)

# %% step 2: get the job in the session
signed_in_user_uuid = ant_connection._make_api_request('user', 'GET')['id']
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

# %% step 4: get the data of this session and then upload some stuff
berekening_records = ant_connection.records_read(project_id, swan_ber_table_id, session=job['session'])

# adhere vak id's that were relevant in this session
vak_ids = []
for swan_berekening in berekening_records:
    
    illustratiepunt_record = ant_connection.record_read(project_id, illustratiepunten_tabel_id, 
                                                        swan_berekening['Illustratiepunt_id'])
    hrd_berekening_record = ant_connection.record_read(project_id, hrd_berekeningen_tabel_id, 
                                                       illustratiepunt_record['HRD_berekening_id'])
    vak_ids.append(hrd_berekening_record['Vak_id'])

unique_vak_ids = list(set(vak_ids))

# TODO: add logic how tijdlijnen should be constructed, this is just a dummy
for vak_id in unique_vak_ids:
    
    # make dict and record
    tijdlijn_dict = {'Vak_id' : vak_id,
                     'tijdlijn_def_id' : 'e26c2494-b675-4432-9dc4-c62bacd75a86',
                     "Bodem_scenario" : 'trend'}
    tijdlijn_record = ant_connection.record_create(project_id, tijdlijn_tabel_id, tijdlijn_dict, 
                                                   session=job['session'])
    
    # create frequentie dict and add to Ant
    for zichtjaar in [2023, 2050, 2100, 2150, 200]:
        # make a dummy freq_file
        dummy_freq_file = os.path.join(temp_folder, 'wl_freq_file.csv')
        with open(dummy_freq_file, 'w') as file:
            file.write('lorem ipsum')
        
        frequentielijn_dict = {'Tijdlijn_id' : tijdlijn_record['id'],
                               'wl_freq_file' : ant_connection.parse_document(dummy_freq_file, 
                                                                              os.path.basename(dummy_freq_file)),
                               'HBN_waarde' : 4,
                               'zichtjaar': zichtjaar}
        ant_connection.record_create(project_id, frequentielijnen_tabel_id, frequentielijn_dict, 
                                                   session=job['session'])

# %% step 5: finish the task
ant_connection.job_finish(project_id, job['id'])
