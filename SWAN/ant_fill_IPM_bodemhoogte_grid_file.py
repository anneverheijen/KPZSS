# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 13:42:13 2022

@author: VERA7

folling steps are done:
    1 - read "sample_bot_relation" and create or update records in IPM_bodemhoogte_grid_file.
        to be able to create this we need 3 ids:
            1 - region_id
            2 - stack_file_id_sample
            3 - stack_file_id_dep
"""

# import python modules
import pathlib
import pandas

# import ant functions
from ant import ant_helper_functions as ant_funcs
# make api connection
ant_connection = ant_funcs.get_api_connection()

# %% specify where to read, to fill, etc
project_name = 'Systeemanalyse Waterveiligheid'
stack_files_table = 'STACK_file'
grid_file_table = 'IPM_bodemhoogte_grid_file'
region_table = 'Locatie_Regio'

# %% get the project and table ids
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
stack_files_table_id = ant_funcs.get_table_id(ant_connection, project_id, stack_files_table)
grid_file_table_id = ant_funcs.get_table_id(ant_connection, project_id, grid_file_table)
region_table_id = ant_funcs.get_table_id(ant_connection, project_id, region_table)

# %% read relevant records
all_file_records = ant_connection.records_read(project_id, stack_files_table_id)
region_records = ant_connection.records_read(project_id, region_table_id)
grid_file_records = ant_connection.records_read(project_id, grid_file_table_id)

# %% read excel table
df = pandas.read_csv('sample_bot_relation.csv', sep=';')

# loop over all these records
for index, row in df.iterrows():
    # relative location samples file from csv
    rel_loc_sample = pathlib.Path(row['Bodem bestand']).relative_to(pathlib.Path(r'z:\130991_Systeemanalyse_ZSS\2.Data\bathy\ontvangen'))
    
    # 1 ) get the region
    if str(rel_loc_sample).startswith('WS'):
        region_id = ant_funcs.find_ids_or_records(records=region_records,
                                      cols_to_search=['Naam'], 
                                      items_to_find=['Westerschelde'])
    
    elif str(rel_loc_sample).startswith('WS'):
        region_id = ant_funcs.find_ids_or_records(records=region_records,
                                      cols_to_search=['Naam'], 
                                      items_to_find=['Waddenzee'])
    else:
        raise UserWarning('Unexpected folder structure')
        
    if not len(region_id) == 1:
        raise UserWarning('expected 1 region')
    else:
        region_id = region_id[0]
    
    # we need to append some to cope with the fact this list is only part of the 
    # stack struct
    rel_loc_sample = 'SWAN\Bodems' / rel_loc_sample
    
    # 2) find stack file of samples file
    stack_file_id_sample = ant_funcs.find_ids_or_records(all_file_records, cols_to_search=['relative_location'],
                                                  items_to_find=[str(rel_loc_sample)])
    if not len(stack_file_id_sample) == 1:
        raise UserWarning('expected 1 sample file')
    else:
        stack_file_id_sample = stack_file_id_sample[0]
        
    # 3) find stack file id of dep file
    name_dep = pathlib.Path(row['SWAN BOT']).name
    stack_file_id_dep = ant_funcs.find_ids_or_records(all_file_records, cols_to_search=['filename'],
                                                  items_to_find=[str(name_dep)])
    if not len(stack_file_id_dep) == 1 :
        raise UserWarning('expected 1 dep file')
    elif len(stack_file_id_dep) == 1:
        stack_file_id_dep = stack_file_id_dep[0]
    
    # create dict with record items
    record_dict = {'STACK_file_id_sample_file': stack_file_id_sample,
                  'STACK_file_id_SWAN_bot': stack_file_id_dep,
                  'Regio_id': region_id,
                  'Naam': name_dep.replace('.bot', ''),
                  'zss_CM_in_scenario' : row['zss'],
                  'Scenario' : row['Scenario']}
    
    # check if there is already an file with the stack_file_id of the samples, if
    # so we want to upgrade it
    grid_file_id, grid_file_record = ant_funcs.find_ids_or_records(grid_file_records, cols_to_search=['STACK_file_id_sample_file'],
                                                  items_to_find=[stack_file_id_sample], return_records=True)
    
    if len(grid_file_record) == 0:
        ant_connection.record_create(project_id, grid_file_table_id, record_dict)
    elif len(grid_file_record) == 1:
        print('update record not done because it did not work')
        
        # # update current values in dict
        # grid_file_record_new = deepcopy(grid_file_record[0])
        # for key, item in record_dict.items():
        #     grid_file_record_new[key] = item
        
        # # get the difference
        # diff_dict = dict(set(grid_file_record_new.items()) - set(grid_file_record[0].items()))
        
        # # update
        # ant_connection.record_update(project_id=project_id, table_id=grid_file_table_id, 
        #                              record_id=grid_file_id[0], updated_record_values=diff_dict)
    else:
        raise UserWarning('unexpected')
    
    ant_connection.parse_document
    