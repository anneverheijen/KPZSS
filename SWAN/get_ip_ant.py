# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 14:09:43 2022

@author: ENGT2
"""

import sys
from ant import ant_helper_functions as ant_funcs

def get_ip_ant(project_name, OKid, ZSS):
    """
    returns illustratiepunt voor geselecteerde OKid and ZSS
    Args:
        None
    Kwargs:
       project_name - name of ant project
        OKid - id of OKADER vak
        ZSS - zeespiegelstijging in cm's

    Returns:
        IP - illustratiepunt voor geselecteerde OKid and ZSS
        indices of Vak, HRD berekening en illustratiepunt
    """
    
    # make api connection
    ant_connection = ant_funcs.get_api_connection()

    # get the project and table id
    project_id  = ant_funcs.get_project_id(ant_connection, project_name=project_name)
    
    #%% stap 1 get okader vak + id 
    table_name      = 'Locatie_Vakken'
    table_id        = ant_funcs.get_table_id(ant_connection, project_id, table_name)   
    records_Vakken  = ant_connection.records_read(project_id, table_id)

    cols_to_search  = ['OKADER_vak_id']
    items_to_find   = [OKid]
            
    index_Vak       = ant_funcs.find_id(records_Vakken, cols_to_search, items_to_find)

    #%% stap 2 get HRD berekening for okadervak
    table_name      = 'DBM_HRD_berekening'
    table_id        = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    records_HRD     = ant_connection.records_read(project_id, table_id)

    cols_to_search  = ['Vak_id','Zeespiegelstijging_CM']
    items_to_find   = [index_Vak,ZSS]
    index_HRD       = ant_funcs.find_id(records_HRD, cols_to_search, items_to_find)

    # include filtering on scenario (ZSS)

    #%% stap 3 get IPM results for HRD berekening
    table_name      = 'IPM_illustratiepunten'
    table_id        = ant_funcs.get_table_id(ant_connection, project_id, table_name)
    records_IPM     = ant_connection.records_read(project_id, table_id)

    cols_to_search  = ['HRD_berekening_id']
    items_to_find   = [index_HRD]
    index_IPM       = ant_funcs.find_id(records_IPM, cols_to_search, items_to_find)

    result_IPM = next(item for item in records_IPM if item["id"] == index_IPM)
    
    return result_IPM, index_Vak, index_HRD, index_IPM