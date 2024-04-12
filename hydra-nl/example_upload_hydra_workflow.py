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
import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import own modules
from ant import ant_helper_functions as ant_funcs

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'

# step 1: specify 
session_name = 'test-hbn'
task_name = 'Hydra Berekeningen'
output_table = 'DBM_HRD_berekening'

# %% step 2: get the job in the session
# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
signed_in_user_uuid = ant_connection._make_api_request('user', 'GET')['id']

task_dict, job = ant_funcs.find_task(ant_connection, project_id, signed_in_user_uuid, session_name,
             task_name)

# # %% step 3: set task to pending
# datestring = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
# ant_connection.task_respond(task_id=task_dict['id'], 
#                           status='processing',
#                           response=f"processing at {datestring}", 
#                           appendix=None,
#                           assigned_user=signed_in_user_uuid, #can be removed once implemented in ANT
#                           due_date=task_dict['due_date']) #can be removed once implemented in ANT

# %% step 4: do a simple upload to output table
table_id = ant_funcs.get_table_id(ant_connection, project_id, output_table)

# create a dict with a result. columns should have name of columns in output table
result_dict = {'id': '0f91fcab-7c8d-4ab1-abea-da6b8328ba2b',
             'Naam': 'Westerschelde_32001001_KPZSS_2200_Laag_5',
             'Vak_id': '2360914e-5a52-4064-9d6b-80a9926bbfdb',
             'HR_database_id': '6eda1d16-952f-412b-81c1-22edfe03c92f',
             'Zeespiegelstijging_CM': 100,
             'Afvoerstatistiek': None,
             'Type berekening': 'HBN',
             'Basis of Gevoeligheid': 'Basis',
             'Zichtjaar': 2200,
             'Bijzonderheden': 'n.v.t.',
             'Goedgekeurd': False,
             'Opmerkingen': 'testdata',
             'Uitvoer_file' : 'test' }
            #  ant_connection.parse_document(r'd:\Users\VERA7\Downloads\uitvoer.html', 'uitvoer.html')}

ant_connection.record_create(project_id, table_id, result_dict, session=job['session'])

#%% step 5: finish the task
ant_connection.job_finish(project_id, job['id'])
