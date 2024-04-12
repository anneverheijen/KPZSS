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
import datetime

# import own modules
from ant import ant_helper_functions as ant_funcs

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'

# step 1: specify 
session_name = 'test004'
task_name = "Overslag Berekening"
swan_1d_table = 'IPM_SWAN_1D'
swan_2d_table = 'IPM_SWAN_2D'
output_table = 'IPM_SWAN_berekening'
hr_table = 'IPM_uitvoerlocatie_golfcondities'
illustratiepunten_tabel = 'IPM_illustratiepunten'

# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
output_table_id = ant_funcs.get_table_id(ant_connection, project_id, output_table)
swan_1d_table_id = ant_funcs.get_table_id(ant_connection, project_id, swan_1d_table)
swan_2d_table_id = ant_funcs.get_table_id(ant_connection, project_id, swan_2d_table)
hr_table_id = ant_funcs.get_table_id(ant_connection, project_id, hr_table)
illustratiepunten_tabel_id = ant_funcs.get_table_id(ant_connection, project_id, illustratiepunten_tabel)

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
berekening_records = ant_connection.records_read(project_id, output_table_id, session=job['session'])

# ant_connection.record_create(project_id, table_id, result_dict, session=job['session'])
for swan_berekening in berekening_records:
    
    # if 1D is required, we want to read these wave conditions
    if swan_berekening['SWAN_1D_required']:
        swan_1d_ber = ant_connection.record_read(project_id, swan_1d_table_id, swan_berekening['SWAN_1D_id'])
        hr_item_id = swan_1d_ber['Uitvoer_HR_basis_id']
        
    # otherwise we want to read the 2D wave conditions
    else:
        swan_2d_ber = ant_connection.record_read(project_id, swan_2d_table_id, swan_berekening['SWAN_2D_id'])
        hr_item_id = swan_2d_ber['Uitvoer_HR_basis_id']
        
    hr_record = ant_connection.record_read(project_id, hr_table_id, hr_item_id)
    illustratiepunt_record = ant_connection.record_read(project_id, illustratiepunten_tabel_id, swan_berekening['Illustratiepunt_id'])
    # IMPORTANT: to update the swan berekening record we need to remove it
    #               first and then make a new one, updating fields with relations
    #               is not possible... made a ticket: https://portal.collaborall.net/tickets/33ad7b67-a311-43a4-8823-9a8e9b69834f
    
    # make swan calculation dict to make record later (after filling results of overslag ber)
    new_swan_berekening = swan_berekening.copy()
    # remove id
    new_swan_berekening.pop('id')
    new_swan_berekening['HBN_final_from_SWAN'] = hr_record['Hs'] # TODO: add real calculation
    new_swan_berekening['HBN_final'] = new_swan_berekening['HBN_final_from_SWAN']* 0.9 # TODO: add real calculation
    new_swan_berekening['HBN_delta_tov_ref'] = illustratiepunt_record['HBN_referentie'] - new_swan_berekening['HBN_final']
    
    # remove old one
    ant_connection.record_delete(project_id, output_table_id, swan_berekening['id'])
    # make new one
    ant_connection.record_create(project_id, output_table_id, new_swan_berekening, 
                                 session=job['session'])
    
# %% step 5: finish the task
ant_connection.job_finish(project_id, job['id'])
