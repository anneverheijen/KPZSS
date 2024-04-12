# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 12:04:36 2022

@author: VERA7
The following steps are required to read session data
1. Specify:
   1. Which session you are working on (name);
   2. which table you want to read data from;
2. Get the session id
3. read the data
"""
# import python modules
import numpy as np

# import own modules
from ant import ant_helper_functions as ant_funcs

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'

# step 1: specify 
session_name = 'test_new'
read_table = 'Calc_output'

# %% step 2: get session id
# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)

session = ant_funcs.find_session(ant_connection, project_id, session_name)  

# %% step 3: read the data
table_id = ant_funcs.get_table_id(ant_connection, project_id, read_table)
records = ant_connection.records_read(project_id, table_id, session=session['id'])

print(f'Found records:\n{records}')