# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 09:49:27 2022

@author: ENGT2
"""

#%% General

import sys
import os
import pandas as pd
import geopandas as gp
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
from hmtoolbox.WB_SWAN import SWAN_read_tab
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot
from ant import ant_helper_functions as ant_funcs

# make api connection
ant_connection = ant_funcs.get_api_connection()

# specify project and get id
project_name = 'Systeemanalyse Waterveiligheid'
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)

#%% Settings

dirs = {'main':     r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\tests\batch_03',
        'input':    r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\tests\batch_03\input'}

files = {'locaties': 'selectie_ill_pilot_v02_WS.shp'}

paths = list_files_folders.list_folders(dirs['main'], dir_incl='WS', startswith = True, endswith = False)

#%% Read shapefile with locations

# read locaties (OKADER vak id's)
df_locs = gp.read_file(os.path.join(dirs['input'],files['locaties']))

#%% Read output for selected locations

output = []
for diri in paths:
    ix = 0
    dirname = os.path.basename(os.path.normpath(diri))
    for OKid in df_locs['VakId']:
        subdir = list_files_folders.list_folders(diri, dir_incl="ID%d" % OKid)
        subdir = subdir[0]
        files = list_files_folders.list_files('.TAB', subdir, startswith = False, endswith = True)
        subdirname = os.path.basename(os.path.normpath(subdir))
        for file in files:
            f = os.path.basename(os.path.normpath(file))
            if f.startswith('HRbasis'):
                print(f)
                tab_file = f
                data, headers = SWAN_read_tab.Freadtab(os.path.join(subdir,f))  
            else:
                print('.TAB-file skipped')                  
        xx = int(df_locs['XCoordinat'][ix])
        yy = int(df_locs['YCoordinat'][ix])
        result  = data[(data['Xp'] == xx) & (data['Yp'] == yy)]
        bodem_name = dirname[:5] + dirname[-3:]
        ZSS = int(dirname[-6:-3])
        result['OkaderId'] = df_locs['VakId'][ix]
        result['Geometrie'] = df_locs['geometry'][ix]
        result['Scenario'] = dirname
        result['ZSS'] = ZSS
        result['Bodem'] = bodem_name
        result['TAB_file'] = os.path.join(subdir,tab_file)
        output.append(result)
        ix = ix + 1
            
output = pd.concat(output)

#%% Loop over all SWAN simulations and push to ANT

for index, row in output.iterrows(): #range(len(output)):

    # OKid    = '29001016'
    # ZSS     = 0
    # Bodem   = 'VT_A1' # dummy test because stuff is not in ANT yet
    # tab_file = 'test.TAB'
        
    # # create a dict with a result. columns should have name of columns in output table
    # result_dict = {'Hs' : 1,
    #                'Tp' : 5,
    #                'Tm-1,0' : 5,
    #                'Golfrichting' : 300,
    #                'Geometrie' : 'POINT(20,200)'}
    
    # SWAN_1D_required = True
    
    OKid    = str(row['OkaderId'])
    ZSS     = row['ZSS']
    # Bodem   = 'VT_A1' # needs to be updated in ANT (VERA7)
    Bodem   = row['Bodem']
    tab_file = row['TAB_file']

    a = Point(row['Xp'], row['Yp'])
    Geometry = f'{a}'
        
    # create a dict with a result. columns should have name of columns in output table
    result_dict = {'Hs' : row['Hsig'],
                   'Tp' : row['TPsmoo'],
                   'Tm-1,0' : row['Tm_10'],
                   'Golfrichting' : row['Dir'],
                   'Geometrie' : Geometry}
    
    SWAN_1D_required = True
   
       #%% Get id of IPM_bodemhoogte_grid_file
    
    # specify where to get record id
    table_name      = 'IPM_bodemhoogte_grid_file'
    
    # get the table id
    table_id        = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    
    # get records grid_files   
    records_Grids   = ant_connection.records_read(project_id, table_id)
    
    # seacrch records grids for Bodem scenario name
    cols_to_search  = ['Naam']
    items_to_find   = [Bodem]      
    record_id_grid  = ant_funcs.find_id(records_Grids, cols_to_search, items_to_find)
    
    #%% Get record id of specified OKADER vak
    
    # specify where to get record id
    table_name      = 'Locatie_Vakken'
    
    # get the table id
    table_id        = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    
    # get records vakken   
    records_Vakken  = ant_connection.records_read(project_id, table_id)
    
    # seacrch records vakken for OKADER vak id
    cols_to_search  = ['OKADER_vak_id']
    items_to_find   = [OKid]        
    record_id_vak   = ant_funcs.find_id(records_Vakken, cols_to_search, items_to_find)
    
    #%% Get id of HRD-berekening
    
    # specify where to get record id
    table_name      = 'DBM_HRD_berekening'
    
    # get the table id
    table_id        = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    
    # get records HRD-berekeningen 
    records_HRD     = ant_connection.records_read(project_id, table_id)
    
    # seacrch records HRD for OKADER vak id and ZSS
    cols_to_search  = ['Vak_id','Zeespiegelstijging_CM']
    items_to_find   = [record_id_vak,ZSS]
    record_id_HRD   = ant_funcs.find_id(records_HRD, cols_to_search, items_to_find)
    
    #%% stap 3 get IP id for HRD berekening
    
    # specify where to get record id
    table_name      = 'IPM_illustratiepunten'
    
    # get the table id
    table_id        = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    
    # get records illustratiepunten
    records_IPs     = ant_connection.records_read(project_id, table_id)
    
    # seacrch records illustratiepunten for HRD id
    cols_to_search  = ['HRD_berekening_id']
    items_to_find   = [record_id_HRD]
    record_id_IP    = ant_funcs.find_id(records_IPs, cols_to_search, items_to_find)
    
    #%% IPM_uitvoerlocaties_golfcondities 
    ### Add record with wave output at selected location and selected scenario 
    
    # specify where to put it
    table_name = 'IPM_uitvoerlocatie_golfcondities'
    
    # get the table id
    table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    
    # create wave output record and get id
    record_id_wave = ant_connection.record_create(project_id, table_id, result_dict)
    
    #%% IPM_SWAN_2D
    ### Add record with SWAN2D output coupled to record in IPM_uitvoerlocaties_golfcondities
    
    # specify where to put it
    table_name = 'IPM_SWAN_2D'
    
    # get the table id
    table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    
    # create a dict with a result. columns should have name of columns in output table
    result_dict = {'Uitvoer_HR_basis_id' : record_id_wave['id'],
                   'Uitvoer_HR_voorland_id' : record_id_wave['id'],
                   'Uitvoer_HR_voorland_300_id' : record_id_wave['id'],
                   'Tab_file' : ant_connection.parse_document(tab_file,os.path.basename(tab_file))}
    
    # create SWAN2D record and get id
    record_id_SWAN2D = ant_connection.record_create(project_id, table_id, result_dict)
    
    #%% IPM_SWAN_berekening 
    ### Add record of SWAN2D run with refernce to location and output (IPM_SWAN_2D)
    
    # specify where to put it
    table_name = 'IPM_SWAN_berekening'
    
    # get the project and table id
    table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    
    # create a dict with a result columns should have name of columns in output table
    result_dict = {'Bodemhoogte_grid_file_id' : record_id_grid,
                   'Illustratiepunt_id' : record_id_IP,
                   'Zeespiegelstijging_CM' : ZSS,
                   'SWAN_2D_id' : record_id_SWAN2D['id'],
                   'SWAN_1D_required' : SWAN_1D_required}
    
    # create SWAN_berekening record and get id
    record_id_SWANberekening = ant_connection.record_create(project_id, table_id, result_dict)
