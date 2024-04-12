# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:08:21 2022

@author: VERA7
script contains functionality to index all files in a specific folder from stack 
to ANT table "STACK_file"
"""
# import python module
import os

# import from hmtoolbox
from hmtoolbox.WB_basic import list_files_folders

# import own modules
import ant_helper_functions as ant_funcs
import file_handling

# specify folder
folder_to_index = r'o:\KP_ZSS_download_from_STACK\Werkmappen HKV en WiBo\07_data_ant\02_SWAN_2D_deps'
root_folder_stack = r'o:\KP_ZSS_download_from_STACK\Werkmappen HKV en WiBo'
stack_type = 'read-write'

# specify where to put it
project_name = 'Systeemanalyse Waterveiligheid'
table_name = 'STACK_file'

# make api connection
ant_connection = ant_funcs.get_api_connection()

# get the project and table id
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)

# get all the files
filelist = list_files_folders.list_files('.bot', folder_to_index, endswith=True)

# %%
# loop over all files, get relevant information and push to ant
for file in filelist:
    
    print(f'starting on {file}')
    fingerprint = file_handling.get_fingerprint_from_file(file)
    
    # create a dict with a result. columns should have name of columns in output table
    result_dict = {'filename' : os.path.basename(file),
                    'relative_location' : os.path.relpath(file, root_folder_stack),
                    'fingerprint' : fingerprint,
                    'STACK_type' : stack_type}

    ant_connection.record_create(project_id, table_id, result_dict)    
