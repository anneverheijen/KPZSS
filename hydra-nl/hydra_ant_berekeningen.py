import os
from re import X
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from pathlib import Path

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import ant functions
from ant import ant_helper_functions as ant_funcs


# make api connection
ant_connection = ant_funcs.get_api_connection()

# specify where to put it
project_name = 'Systeemanalyse Waterveiligheid'
table_name = 'DBM_HRD_berekening'
region_table = 'Locatie_Regio'
vakken_table = 'Locatie_Vakken'
STACK_table = 'STACK_file'
DBM_HR_database_table = 'DBM_HR_database'
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
region_table_id = ant_funcs.get_table_id(ant_connection, project_id, region_table)
vakken_table_id = ant_funcs.get_table_id(ant_connection, project_id, vakken_table)
STACK_table_id = ant_funcs.get_table_id(ant_connection, project_id, STACK_table)
DBM_HR_database_table_id = ant_funcs.get_table_id(ant_connection, project_id, DBM_HR_database_table)

# get the project and table id
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)
region_records = ant_connection.records_read(project_id, region_table_id)
vakken_records = ant_connection.records_read(project_id, vakken_table_id)
STACK_records = ant_connection.records_read(project_id, STACK_table_id)
DBM_HR_database_records = ant_connection.records_read(project_id, DBM_HR_database_table_id)

# import needed files
okader_norm_csv = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\koppelingen\Vakken_OKADER_norm_csv_v2.csv")
df_hydra_definition = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\koppelingen\OKADER_FC_Hydra_attributes_filtered.csv")
hydra_output = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\output\HBN\hydra_output_totaal.csv", delimiter=';')


# func voor scenario en zeespiegelstijging
def zss_scenario(naam_scenario):

    if '2023' in naam_scenario:
        zichtjaar = 2023
        zss = 0
    
    if '2100' in naam_scenario:
        zichtjaar = 2100

        if 'Laag' in naam_scenario:
            zss = 50
        elif 'Gematigd' in naam_scenario:
            zss = 75
        elif 'Extreem' in naam_scenario:
            zss = 100
        elif 'Zeer_extreem' in naam_scenario:
            zss = 200
    
    if '2200' in naam_scenario:
        zichtjaar = 2200

        if 'Laag' in naam_scenario:
            zss = 100
        elif 'Gematigd' in naam_scenario:
            zss = 200
        elif 'Extreem' in naam_scenario:
            zss = 300

    return zichtjaar, zss

afvoerstatistiek = r"D:\Users\BADD\Desktop\KP ZSS\overig\test.txt"
base_folder = r"C:\MyPrograms\Hydra-NL_KP_ZSS\werkmap"

# create a dict with a result. columns should have name of columns in output table

for i in range(len(hydra_output)):
    zichtjaar, zss = zss_scenario(hydra_output['ZSS-scenario'].loc[i])    
    
    if Path(hydra_output['Uitvoerbestand'].loc[i]).exists():

    # freq_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\ffq.txt')
    # invoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\invoer.hyd')
    # uitvoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.html')
    # log_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.log')
    # print((hydra_output['Uitvoerbestand'].loc[i].split('\\')[-5] + '.zip'))
    # print(str(hydra_output['OKADER VakId'].loc[i]))
   
        if 'Waddenzee' in hydra_output['Uitvoerbestand'].loc[i]:
            
                string_to_match = ['_KW', '_WS']

                # for substring in string_to_match:
                #     if not substring in hydra_output['Uitvoerbestand'].loc[i].split('\\')[-1]:
                if not any(x in hydra_output['Uitvoerbestand'].loc[i].split('\\')[-1] for x in string_to_match):
                        freq_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\ffq.txt')
                        invoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\invoer.hyd')
                        uitvoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.html')
                        log_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.log')               


                        result_dict = {
                                'Naam'  : hydra_output['Uitvoerbestand'].loc[i].split('\\')[-2],
                                'Vak_id'  : ant_funcs.find_id(vakken_records, ['HRD_locatie_id', 'OKADER_vak_id'], [hydra_output['HYD_location_name'].loc[i], str(hydra_output['OKADER VakId'].loc[i])]),
                                'HR_database_id' : ant_funcs.find_id(DBM_HR_database_records, ['STACK_file_ID'], [ant_funcs.find_id(STACK_records, ['filename'], [(hydra_output['Uitvoerbestand'].loc[i].split('\\')[-5] + '.zip')])]),
                                'Zeespiegelstijging_CM'  : float(zss),
                                # 'Afvoerstatistiek'  : ant_connection.parse_document(afvoerstatistiek, 'test.txt'),
                                'Type berekening'  : 'HBN',
                                'Basis of Gevoeligheid'  : 'Basis',
                                'Zichtjaar'  :  zichtjaar,
                                'Bijzonderheden'  : 'n.v.t.',
                                'freq_file'  : ant_connection.parse_document(freq_file, 'ffq.txt'),
                                'Invoer_file'  : ant_connection.parse_document(invoer_file, 'invoer.hyd'),
                                'Uitvoer_file'  : ant_connection.parse_document(uitvoer_file, 'uitvoer.html'), 
                                'Log_file'  : ant_connection.parse_document(log_file, 'uitvoer.log'),
                                'Goedgekeurd'  :  False,
                                'Opmerkingen'  : '-'}

                        ant_connection.record_create(project_id, table_id, result_dict)

        elif 'Westerschelde' in hydra_output['Uitvoerbestand'].loc[i]:
                # for substring in string_to_match:
                #     if not substring in hydra_output['Uitvoerbestand'].loc[i].split('\\')[-1]:
                if not any(x in hydra_output['Uitvoerbestand'].loc[i].split('\\')[-1] for x in string_to_match):

                        freq_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\ffq.txt')
                        invoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\invoer.hyd')
                        uitvoer_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.html')
                        log_file = os.path.join(os.path.dirname(hydra_output['Uitvoerbestand'].loc[i]) + '\\uitvoer.log')    


                        result_dict = {
                                'Naam'  : hydra_output['Uitvoerbestand'].loc[i].split('\\')[-2],
                                'Vak_id'  : ant_funcs.find_id(vakken_records, ['HRD_locatie_id', 'OKADER_vak_id'], [hydra_output['HYD_location_name'].loc[i], str(hydra_output['OKADER VakId'].loc[i])]),
                                'HR_database_id' : ant_funcs.find_id(DBM_HR_database_records, ['STACK_file_ID'], [ant_funcs.find_id(STACK_records, ['filename'], [(hydra_output['Uitvoerbestand'].loc[i].split('\\')[-5] + '.zip')])]),
                                'Zeespiegelstijging_CM'  : float(zss),
                                # 'Afvoerstatistiek'  : ant_connection.parse_document(afvoerstatistiek, 'test.txt'),
                                'Type berekening'  : 'HBN',
                                'Basis of Gevoeligheid'  : 'Basis',
                                'Zichtjaar'  :  zichtjaar,
                                'Bijzonderheden'  : 'n.v.t.',
                                'freq_file'  : ant_connection.parse_document(freq_file, 'ffq.txt'),
                                'Invoer_file'  : ant_connection.parse_document(invoer_file, 'invoer.hyd'),
                                'Uitvoer_file'  : ant_connection.parse_document(uitvoer_file, 'uitvoer.html'), 
                                'Log_file'  : ant_connection.parse_document(log_file, 'uitvoer.log'),
                                'Goedgekeurd'  :  False,
                                'Opmerkingen'  : '-'}

                        ant_connection.record_create(project_id, table_id, result_dict)

    #toevoegen elif voor Hollandse Kust

    print('Record', i+1, 'toegevoegd')


