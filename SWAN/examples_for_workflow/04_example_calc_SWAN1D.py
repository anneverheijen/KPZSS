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
task_name = "Calc SWAN 1D"
input_table = 'IPM_SWAN_2D'
output_table = 'IPM_SWAN_1D'
table_name_bers = 'IPM_SWAN_berekening'

# specify a local temporary folder to store all calculations in 
temp_folder = os.path.join(os.getcwd(), f'tmp_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')

# check if this folder exists, otherwise make it
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

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
berekening_records = ant_connection.records_read(project_id, table_id_bers, session=job['session'])

# ant_connection.record_create(project_id, table_id, result_dict, session=job['session'])
for swan_berekening in berekening_records:
     
    # get the 2D calculation to base the 1D on
    swan_2D_record = ant_connection.record_read(project_id, input_table_id, swan_berekening['SWAN_2D_id'])
    
    # download example tab file
    example_tab_file = ant_connection.download_document(project_id, input_table_id, 
                                                   swan_2D_record['Tab_file']['id'],
                                                   temp_folder)
    location_tab_file = os.path.join(temp_folder, 
                                    f"{swan_2D_record['Tab_file']['name']}.{swan_2D_record['Tab_file']['extension']}")

    
    # make dict for swan 1d data to make record later    
    swan1d_dict = {'Uitvoer_HR_basis_id': 'dad0e4c7-817e-489f-8511-179fda3a49ba',
                   'Tab_file': ant_connection.parse_document(location_tab_file, os.path.basename(location_tab_file)),
                   'Goedgekeurd': True}
        
    swan1d_record = ant_connection.record_create(project_id, output_table_id, swan1d_dict, session=job['session'])
    
    # IMPORTANT: to update the swan berekening record we need to remove it
    #               first and then make a new one, updating fields with relations
    #               is not possible... made a ticket: https://portal.collaborall.net/tickets/33ad7b67-a311-43a4-8823-9a8e9b69834f
    
    # make swan calculation dict to make record later
    new_swan_berekening = swan_berekening.copy()
    # remove id
    new_swan_berekening.pop('id')
    new_swan_berekening['SWAN_1D_id'] = 'e6040020-62bc-498c-b435-a0bb1eab21e2'
    
    # remove old one
    ant_connection.record_delete(project_id, table_id_bers, swan_berekening['id'])
    # make new one
    ant_connection.record_create(project_id, table_id_bers, new_swan_berekening, 
                                 session=job['session'])
    
# %% step 5: finish the task
ant_connection.job_finish(project_id, job['id'])
