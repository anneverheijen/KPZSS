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
import os
import numpy as np
import datetime

# import own modules
from ant import ant_helper_functions as ant_funcs
# import kp zss functions
from reader import lees_invoerbestand, lees_uitvoerhtml, lees_illustratiepunten, lees_ofl

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'

# step 1: specify 
session_name = 'testmetdaan'
task_name = "Get IP's"
input_table = 'DBM_HRD_berekening'
output_table = 'IPM_illustratiepunten'
table_name_vak = 'Locatie_Vakken'

# specify a local temporary folder
temp_folder = 'tmp'

# check if this folder exists, otherwise make it
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
output_table_id = ant_funcs.get_table_id(ant_connection, project_id, output_table)
input_table_id = ant_funcs.get_table_id(ant_connection, project_id, input_table)
table_id_vak = ant_funcs.get_table_id(ant_connection, project_id, table_name_vak)
records_vak = ant_connection.records_read(project_id, table_id_vak)

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
hydra_nl_input_records = ant_connection.records_read(project_id, input_table_id, session=job['session'])

# ant_connection.record_create(project_id, table_id, result_dict, session=job['session'])
for calc_record in hydra_nl_input_records:
        
    # find the right vak
    vak_id, vak_result_records = ant_funcs.find_ids_or_records(records_vak, 
                                      ['id'],
                                      [calc_record['Vak_id']], 
                                      return_records=True)
    vak = vak_result_records[0]
    
    # now we are processing a calculation, download the outcome
    ant_connection.download_document(project_id, input_table_id, 
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
    
    ant_connection.record_create(project_id, output_table_id, illustratiepunten_dict, session=job['session'])
    
    # remove output, just for sanity
    os.remove(location_uitvoer)

# %% step 5: finish the task
ant_connection.job_finish(project_id, job['id'])
