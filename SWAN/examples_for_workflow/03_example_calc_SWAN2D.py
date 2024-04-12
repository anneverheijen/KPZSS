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
import numpy as np
import datetime

# import own modules
from ant import ant_helper_functions as ant_funcs

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'

# step 1: specify 
session_name = 'test004'
task_name = "Calc SWAN 2D"
input_table = 'IPM_illustratiepunten'
output_table = 'IPM_SWAN_2D'
table_name_bers = 'IPM_SWAN_berekening'

# specify a local temporary folder to store all calculations in 
temp_folder = os.path.join(os.getcwd(), f'tmp_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')

# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
output_table_id = ant_funcs.get_table_id(ant_connection, project_id, output_table)
input_table_id = ant_funcs.get_table_id(ant_connection, project_id, input_table)
table_id_bers = ant_funcs.get_table_id(ant_connection, project_id, table_name_bers)

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
illustratiepunten_input_records = ant_connection.records_read(project_id, input_table_id, session=job['session'])

# ant_connection.record_create(project_id, table_id, result_dict, session=job['session'])
for ip in illustratiepunten_input_records:
        
    # make an example tab file
    example_tab_file = os.path.join(temp_folder, 'example_folder', 'exampledata.TAB')
    
    # check if this folder exists, otherwise make it
    if not os.path.exists(os.path.dirname(example_tab_file)):
        os.makedirs(os.path.dirname(example_tab_file))
    
    with open(example_tab_file, 'w') as file:
        file.write(str(ip))
    
    # make dict for swan 2d data to make record later    
    swan2d_dict = {'Uitvoer_HR_basis_id': 'dad0e4c7-817e-489f-8511-179fda3a49ba',
                   'Uitvoer_HR_voorland_id': 'dad0e4c7-817e-489f-8511-179fda3a49ba',
                   'Uitvoer_HR_voorland_300_id': 'dad0e4c7-817e-489f-8511-179fda3a49ba',
                   'Tab_file': ant_connection.parse_document(example_tab_file, os.path.basename(example_tab_file)),
                   'Goedgekeurd': True}
        
    swan2d_record = ant_connection.record_create(project_id, output_table_id, swan2d_dict, session=job['session'])
    
    # make swan calculation dict to make record later
    swan_ber_dict = {'Bodemhoogte_grid_file_id': '8c048c4f-2364-424a-8ccf-367526c63e3d',
                     'Illustratiepunt_id': ip['id'],
                     'Zeespiegelstijging_CM': 0,
                     'SWAN_2D_id': swan2d_record['id'],
                     'SWAN_1D_required': False,
                     'Voorland_profiel_id': None,
                     'SWAN_1D_id': None,
                     'HBN_final_from_SWAN': None,
                     'HBN_delta_tov_ref': None,
                     'HBN_final': None,
                     'Haven_correctie': False,
                     'Goedgekeurd': True}
    
    ant_connection.record_create(project_id, table_id_bers, swan_ber_dict, session=job['session'])
    
# %% step 5: finish the task
ant_connection.job_finish(project_id, job['id'])
