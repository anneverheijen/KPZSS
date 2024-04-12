import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import ant functions
from ant import ant_helper_functions as ant_funcs


# make api connection
ant_connection = ant_funcs.get_api_connection()

# specify where to put it
project_name = 'Systeemanalyse Waterveiligheid'
table_name = 'Locatie_Vakken'
region_table = 'Locatie_Regio'
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
region_table_id = ant_funcs.get_table_id(ant_connection, project_id, region_table)

# get the project and table id
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)
region_records = ant_connection.records_read(project_id, region_table_id)

# import needed files
okader_norm_csv = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\koppelingen\Vakken_OKADER_norm_csv_v2.csv")
df_hydra_definition = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\koppelingen\OKADER_FC_Hydra_attributes.csv")
hydra_output = pd.read_csv(r"D:\Users\BADD\Desktop\KP ZSS\kust\output\HBN\hydra_output_totaal.csv", delimiter=';')

hyd_location_shp = gpd.read_file(r'D:\Users\BADD\Desktop\KP ZSS\GIS\uitvoerpunten_hydra-nl\HRD_locations_hydra.shp')
okader_norm_shp = gpd.read_file(r'D:\Users\BADD\Desktop\KP ZSS\GIS\okader_vakindeling_norm\Vakken_OKADER_norm_v2.shp')

# create a dict with a result. columns should have name of columns in output table

for i in range(len(df_hydra_definition)):

    # get profile file, profile files are based on VakId
    profile_file = 'D:\\Users\\BADD\\Desktop\\KP ZSS\\kust\\profielen\\' + str(df_hydra_definition['VakId'].loc[i]) + '.prfl'


    # get returnperiod for specific okader-vak
    for j in range(len(okader_norm_shp)):
        if str(df_hydra_definition['VakId'].loc[i]) == okader_norm_shp['VakId'].loc[j]:
            terugkeertijd = okader_norm_shp['V2_NORM_OG'].loc[j]
            okader_vak_geometry = okader_norm_shp['geometry'][j].wkt

    for k in range(len(hyd_location_shp)):
        if str(df_hydra_definition['Name'].loc[i]) == hyd_location_shp['Name'].loc[k]:
            hyd_geometry = hyd_location_shp['geometry'][k].wkt

    okader_geometry_file = 'D:\\Users\\BADD\Desktop\\KP ZSS\\kust\\okader_geometry\\' + str(df_hydra_definition['VakId'].loc[i]) + '_geometry.txt'
    with open(okader_geometry_file, 'w') as file:
        file.write(okader_vak_geometry)
    

    if 'WZ' in df_hydra_definition['Name'].loc[i]:
        result_dict = {'Regio_id' : ant_funcs.find_id(region_records, ['Naam', 'Methode'], ['Waddenzee', 'IPM']),
                'HRD_locatie_id' : df_hydra_definition['Name'].loc[i],
               'OKADER_vak_id' : str(df_hydra_definition['VakId'].loc[i]),
            #    'Geometry_vak' : okader_vak_geometry,
               'Geometry_OKADER_vak' : ant_connection.parse_document(okader_geometry_file, (str(df_hydra_definition['VakId'].loc[i]) + '_geometry.txt')),
               'Geometry_HRD_locatie' : hyd_geometry,
               'Profiel' : ant_connection.parse_document(profile_file, (str(df_hydra_definition['VakId'].loc[i]) + '.prfl')), 
               'Type_vak'  : 'Dijkvak',
               'Norm_frequentie'  : terugkeertijd}
        ant_connection.record_create(project_id, table_id, result_dict)

    elif 'WS' in df_hydra_definition['Name'].loc[i]:
        result_dict = {'Regio_id' : ant_funcs.find_id(region_records, ['Naam', 'Methode'], ['Westerschelde', 'IPM']),
                'HRD_locatie_id' : df_hydra_definition['Name'].loc[i],
               'OKADER_vak_id' : str(df_hydra_definition['VakId'].loc[i]),
            #    'Geometry_vak' : okader_vak_geometry,
               'Geometry_OKADER_vak' : ant_connection.parse_document(okader_geometry_file, (str(df_hydra_definition['VakId'].loc[i]) + '_geometry.txt')),
               'Geometry_HRD_locatie' : hyd_geometry,
               'Profiel' : ant_connection.parse_document(profile_file, (str(df_hydra_definition['VakId'].loc[i]) + '.prfl')), 
               'Type_vak'  : 'Dijkvak',
               'Norm_frequentie'  : terugkeertijd}
        ant_connection.record_create(project_id, table_id, result_dict)

    #toevoegen elif voor Hollandse Kust
    # del okader_geometry_file
    print('Record', i+1, 'toegevoegd')
