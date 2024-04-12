# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts reads output from SWAN2D runs and writes it to an Excel.

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 

--- Version --- 
Created on Mon Sep 26 09:21:51 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: SWAN_2D_output_to_xlsx_WZ_productie_mod_MAT_cluster.py 

--- Revision --- 
Status: Unverified 

Witteveen+Bos Consulting Engineers 
Leeuwenbrug 8
P.O. box 233 
7411 TJ Deventer
The Netherlands 
		
"""

#%% load modules

import os
import geopandas as gp
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_SWAN import SWAN_read_tab
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot
import pandas as pd
from scipy.io import loadmat

#%% Settings

# Location of SWAN2D output
path_main   = r'/project/130991_Systeemanalyse_ZSS/3.Models/SWAN/2D/Waddenzee/03_productiesommen/serie_01/G2'
dirs        = list_files_folders.list_folders(path_main, dir_incl='WZ', startswith = True, endswith = False)

# Shapefile with OKADER vak info (including id and fragility curve info)
path_OKid_shape = r'/project/130991_Systeemanalyse_ZSS/2.Data/GIS_TEMP/okader_fc_hydra_unique_handedit_WZ_v3_coords.shp'

# Excel file with coupling between illustratiepunten (simulations) and OKADER vakken
path_coupling = r'/project/130991_Systeemanalyse_ZSS/3.Models/SWAN/2D/Waddenzee/03_productiesommen/serie_01/input/IP_OKADER_coupling.xlsx'

# Shapefile with output locations along SWAN 1D profiles
path_1D_outlocs = r'/project/130991_Systeemanalyse_ZSS/2.Data/GIS_TEMP/HRD_locations_selectie_WZ_300m_interval_OKid.shp'

# Switch to results to Excel
save_excel_ids = False
save_excel_output = True

#%% Read output for selected locations and export to Excel

# get list of unique okader ids from shapefile
df_ids = gp.read_file(path_OKid_shape)

# get coupling of okader ids to simulation
xl_coupling = pd.ExcelFile(path_coupling,engine='openpyxl')
df_coupling = xl_coupling.parse()
okids_a = df_coupling['A']
okids_na = df_coupling['NA']
okids_all = df_coupling['ALL']

del df_coupling['A']
del df_coupling['NA']
del df_coupling['ALL']
df_coupling = np.array(df_coupling)

OKids = df_ids['VakId']
X = df_ids['xcoord']
Y = df_ids['ycoord']

#%% first loop over all OKADR ids to get SWAN som number

som_ids = []
OKids_near = []

ix = 0

for OKid in OKids:
    
    # get som id for okader vak id        
    indices = np.where(df_coupling==int(OKid))
    if indices[0].size > 0:
        som_ids.append(indices[1][0])
        print('OKADER ID assinged, som ID found')
        OKids_near.append('')
    elif indices[0].size == 0:
        print('OKADER ID %s not assigned, find nearest point' % OKid)
        xq = df_ids[df_ids['VakId']==OKid]['xcoord'].iloc[0]
        yq = df_ids[df_ids['VakId']==OKid]['ycoord'].iloc[0]
        dx = X - xq
        dy = Y - yq
        dis = np.sqrt(dx**2 + dy**2)
        dis[dis==0] = 1e6
        min_ind = np.argmin(dis, axis=0)
        OKid_near = OKids[min_ind]
        # check if nearest point is assigned in SWAN runs
        check_ind = np.where(df_coupling==int(OKid_near))
        if check_ind[0].size > 0:
            som_ids.append(check_ind[1][0])
            print('nearest point is assigned')
            OKids_near.append(OKid_near)
        elif check_ind[0].size == 0:
            print('nearest point is not assigned, take next point')
            for tt in range(0,3):
                dis[min_ind] = 1e6
                min_ind = np.argmin(dis, axis=0)
                OKid_near = OKids[min_ind]
                print(OKid_near)
                check_ind = np.where(df_coupling==int(OKid_near))
                if check_ind[0].size > 0:
                    som_ids.append(check_ind[1][0])
                    print('nearest point is assigned')
                    OKids_near.append(OKid_near)
                    break
                else:
                    print('assignment failed after %d iterations' % tt)
                    failed = 1
                    OKid_failed = OKid
    ix = ix + 1

data = {'OKid': OKids,
        'som_id': som_ids,
        'OKids_near': OKids_near}
assignment = pd.DataFrame(data)

if save_excel_ids:
    assignment.to_excel(os.path.join(path_main,'assignment_okader_ids_simulatie_SWAN2D_WZ.xlsx')) 


#%% get output at HRbasis locations

outlocs_name = 'HRbasis'
    
pd.options.mode.chained_assignment = None

min_dis_max = 0
min_dis_max_mat = 0

XX = df_ids['XCoordinat']
YY = df_ids['YCoordinat']

# loop over all scenario's and simulations

appended_data_01 = []
for diri in dirs:
    ix = 0
    dirname = os.path.basename(os.path.normpath(diri))
    
    for OKid in OKids:
               
        som_id = assignment[assignment['OKid']==OKid]['som_id']
        
        subdir = list_files_folders.list_folders(diri, dir_incl="ID%03d" % som_id)       
        subdir = subdir[0]
        
        files = list_files_folders.list_files('.TAB', subdir, startswith = False, endswith = True)
        subdirname = os.path.basename(os.path.normpath(subdir))
        scen_name = diri.split("/")[-1]
        for file in files:
            f = os.path.basename(os.path.normpath(file))
            if f.startswith(outlocs_name):
                print(OKid)
                print(scen_name)
                print(f)
                data, headers = SWAN_read_tab.Freadtab(os.path.join(subdir,f))  
        xx = data['Xp']
        yy = data['Yp']        
        xq = XX[ix]
        yq = YY[ix]
        
        dx = xx - xq
        dy = yy - yq
        dis = np.sqrt(dx**2 + dy**2)

        min_dis = np.min(dis)
        print('min distance = %.2f' % min_dis)
        row_ind = np.argmin(dis, axis=0)
        print('min index = %d' % row_ind)
        min_dis_max = max(min_dis, min_dis_max)
               
        result  = data.iloc[[row_ind]]
        result['OkaderId'] = OKids[ix]
        result['Scenario'] = dirname
        result['min_dis'] = min_dis
        result['min_ind'] = row_ind
        result['MAT_used']  = '0'
        result['TAB_used']  = '1'
        
        # if no output is found in TAB-file, get it from MAT-file
        if result['Depth'].iloc[0] < 0:
            print('no output found in HRbasis TAB-file, get output from MAT-file')
            files_mat = list_files_folders.list_files('.mat', subdir, startswith = False, endswith = True)
            
            data_mat = loadmat(files_mat[0])
                                 
            xx = data_mat['Xp']
            yy = data_mat['Yp']        
            
            dx = xx - xq
            dy = yy - yq
            dis = np.sqrt(dx**2 + dy**2)
    
            min_dis = np.nanmin(dis)
            print('min distance = %.2f' % min_dis)
            min_ind = np.nanargmin(dis)
            print('min index = %d' % row_ind)
            min_dis_max_mat = max(min_dis, min_dis_max_mat)
            
            result['Xp']        = data_mat['Xp'].flatten()[min_ind]
            result['Yp']        = data_mat['Yp'].flatten()[min_ind]
            result['Depth']     = data_mat['Depth'].flatten()[min_ind]
            result['Hsig']      = data_mat['Hsig'].flatten()[min_ind]
            result['RTpeak']    = data_mat['RTpeak'].flatten()[min_ind]
            result['TPsmoo']    = data_mat['TPsmoo'].flatten()[min_ind]
            result['Tm_10']     = data_mat['Tm_10'].flatten()[min_ind]
            result['Tm01']      = data_mat['Tm01'].flatten()[min_ind]
            result['Tm02']      = data_mat['Tm02'].flatten()[min_ind]
            result['Dir']       = data_mat['Dir'].flatten()[min_ind]
            result['Dspr']      = data_mat['Dspr'].flatten()[min_ind]
            result['Wlen']      = data_mat['Wlen'].flatten()[min_ind]
            result['Dissip']    = data_mat['Dissip'].flatten()[min_ind]
            result['dHs']       = data_mat['dHs'].flatten()[min_ind]
            result['dTm']       = data_mat['dTm'].flatten()[min_ind]
            result['Watlev']    = data_mat['Watlev'].flatten()[min_ind]
            result['X-Windv']   = data_mat['Windv_x'].flatten()[min_ind]
            result['Y-Windv']   = data_mat['Windv_y'].flatten()[min_ind]
            result['X-Vel']     = data_mat['Vel_x'].flatten()[min_ind]
            result['Y-Vel']     = data_mat['Vel_y'].flatten()[min_ind]
            result['Botlev']    = data_mat['Botlev'].flatten()[min_ind]
            result['Qb']        = data_mat['Qb'].flatten()[min_ind]
            
            result['min_dis'] = min_dis
            result['min_ind'] = min_ind
            result['MAT_used']  = '1'
            result['TAB_used']  = '0'
            
        # append data    
        appended_data_01.append(result)
        
        ix = ix + 1
        
        del data, result, dis, xx, yy, xq, yq
                                     
appended_data_01 = pd.concat(appended_data_01)
print('maximum distace with SWAN output loc = %.2f' % min_dis_max)


#%% get output along 1D profiles 300m from dyke (input 1D SWAN simulations)

outlocs_name = 'HRext01'

df_outlocs = gp.read_file(path_1D_outlocs)

distance = 300

pd.options.mode.chained_assignment = None

min_dis_max = 0
no_match = 0

# loop over all scenario's and simulations

appended_data_02 = []
for diri in dirs:
    ix = 0
    dirname = os.path.basename(os.path.normpath(diri))
    for OKid in OKids:
                   
        som_id = assignment[assignment['OKid']==OKid]['som_id']
        
        subdir = list_files_folders.list_folders(diri, dir_incl="ID%03d" % som_id)       
        subdir = subdir[0]
        
        files = list_files_folders.list_files('.TAB', subdir, startswith = False, endswith = True)
        subdirname = os.path.basename(os.path.normpath(subdir))
        scen_name = diri.split("/")[-1]
        for file in files:
            f = os.path.basename(os.path.normpath(file))
            if f.startswith(outlocs_name):
                print(OKid)
                print(scen_name)
                print(f)
                data, headers = SWAN_read_tab.Freadtab(os.path.join(subdir,f))  
        
        match = (df_outlocs['HubName'] == OKid) & (df_outlocs['cngmeters'] == distance)
        if match.any(axis=0) == True:
            xq = df_outlocs[(df_outlocs['HubName'] == OKid) & (df_outlocs['cngmeters'] == distance)]['xcoord'].iloc[0]  
            yq = df_outlocs[(df_outlocs['HubName'] == OKid) & (df_outlocs['cngmeters'] == distance)]['ycoord'].iloc[0] 
            
            xx = data['Xp']
            yy = data['Yp']        
            
            dx = xx - xq
            dy = yy - yq
            dis = np.sqrt(dx**2 + dy**2)

            min_dis = np.min(dis)
            print('min distance = %.2f' % min_dis)
            row_ind = np.argmin(dis, axis=0)
            print('min index = %d' % row_ind)
            min_dis_max = max(min_dis, min_dis_max)
                   
            result  = data.iloc[[row_ind]]
            
            result['OkaderId'] = OKid
            result['Scenario'] = dirname
            result['min_dis'] = min_dis
            result['min_ind'] = row_ind
            result['MAT_used']  = '0'
            result['TAB_used']  = '1'
            
            # if no output is found in TAB-file, get it from MAT-file 
            if result['Depth'].iloc[0] < 0:  
                print('no output found in HRbasis TAB-file, get output from MAT-file')
                
                files_mat = list_files_folders.list_files('.mat', subdir, startswith = False, endswith = True)
                
                data_mat = loadmat(files_mat[0])
                                     
                xx = data_mat['Xp']
                yy = data_mat['Yp']        
                
                dx = xx - xq
                dy = yy - yq
                dis = np.sqrt(dx**2 + dy**2)
        
                min_dis = np.nanmin(dis)
                print('min distance = %.2f' % min_dis)
                min_ind = np.nanargmin(dis)
                print('min index = %d' % row_ind)
                min_dis_max_mat = max(min_dis, min_dis_max_mat)
                
                result['Xp']        = data_mat['Xp'].flatten()[min_ind]
                result['Yp']        = data_mat['Yp'].flatten()[min_ind]
                result['Depth']     = data_mat['Depth'].flatten()[min_ind]
                result['Hsig']      = data_mat['Hsig'].flatten()[min_ind]
                result['RTpeak']    = data_mat['RTpeak'].flatten()[min_ind]
                result['TPsmoo']    = data_mat['TPsmoo'].flatten()[min_ind]
                result['Tm_10']     = data_mat['Tm_10'].flatten()[min_ind]
                result['Tm01']      = data_mat['Tm01'].flatten()[min_ind]
                result['Tm02']      = data_mat['Tm02'].flatten()[min_ind]
                result['Dir']       = data_mat['Dir'].flatten()[min_ind]
                result['Dspr']      = data_mat['Dspr'].flatten()[min_ind]
                result['Wlen']      = data_mat['Wlen'].flatten()[min_ind]
                result['Dissip']    = data_mat['Dissip'].flatten()[min_ind]
                result['dHs']       = data_mat['dHs'].flatten()[min_ind]
                result['dTm']       = data_mat['dTm'].flatten()[min_ind]
                result['Watlev']    = data_mat['Watlev'].flatten()[min_ind]
                result['X-Windv']   = data_mat['Windv_x'].flatten()[min_ind]
                result['Y-Windv']   = data_mat['Windv_y'].flatten()[min_ind]
                result['X-Vel']     = data_mat['Vel_x'].flatten()[min_ind]
                result['Y-Vel']     = data_mat['Vel_y'].flatten()[min_ind]
                result['Botlev']    = data_mat['Botlev'].flatten()[min_ind]
                result['Qb']        = data_mat['Qb'].flatten()[min_ind]
                
                result['min_dis'] = min_dis
                result['min_ind'] = min_ind
                result['MAT_used']  = '1'
                result['TAB_used']  = '0'   
                
            # append data   
            appended_data_02.append(result)
                           
            del data, result, dis, xx, yy, xq, yq  
                        
        else: 
            print('OKid %s has no matching 1D profile' % OKid)
            no_match = no_match + 1
                                
appended_data_02 = pd.concat(appended_data_02)
print('maximum distace with SWAN output loc = %.2f' % min_dis_max)


#%% get output along 1D profiles 600m from dyke (input 1D SWAN simulations)

outlocs_name = 'HRext01'

df_outlocs = gp.read_file(path_1D_outlocs)

distance = 600

pd.options.mode.chained_assignment = None

min_dis_max = 0
no_match = 0

# loop over all scenario's and simulations

appended_data_03 = []
for diri in dirs:
    ix = 0
    dirname = os.path.basename(os.path.normpath(diri))
    for OKid in OKids:
                   
        som_id = assignment[assignment['OKid']==OKid]['som_id']
        
        subdir = list_files_folders.list_folders(diri, dir_incl="ID%03d" % som_id)       
        subdir = subdir[0]
        
        files = list_files_folders.list_files('.TAB', subdir, startswith = False, endswith = True)
        subdirname = os.path.basename(os.path.normpath(subdir))
        scen_name = diri.split("/")[-1]
        for file in files:
            f = os.path.basename(os.path.normpath(file))
            if f.startswith(outlocs_name):
                print(OKid)
                print(scen_name)
                print(f)
                data, headers = SWAN_read_tab.Freadtab(os.path.join(subdir,f))  
        
        match = (df_outlocs['HubName'] == OKid) & (df_outlocs['cngmeters'] == distance)
        if match.any(axis=0) == True:
            xq = df_outlocs[(df_outlocs['HubName'] == OKid) & (df_outlocs['cngmeters'] == distance)]['xcoord'].iloc[0]  
            yq = df_outlocs[(df_outlocs['HubName'] == OKid) & (df_outlocs['cngmeters'] == distance)]['ycoord'].iloc[0] 
            
            xx = data['Xp']
            yy = data['Yp']        
            
            dx = xx - xq
            dy = yy - yq
            dis = np.sqrt(dx**2 + dy**2)

            min_dis = np.min(dis)
            print('min distance = %.2f' % min_dis)
            row_ind = np.argmin(dis, axis=0)
            print('min index = %d' % row_ind)
            min_dis_max = max(min_dis, min_dis_max)
                   
            result  = data.iloc[[row_ind]]
            
            result['OkaderId'] = OKid
            result['Scenario'] = dirname
            result['min_dis'] = min_dis
            result['min_ind'] = row_ind
            result['MAT_used']  = '0'
            result['TAB_used']  = '1'
            
            # if no output is found in TAB-file, get it from MAT-file 
            if result['Depth'].iloc[0] < 0:  
                print('no output found in HRbasis TAB-file, get output from MAT-file')
                
                files_mat = list_files_folders.list_files('.mat', subdir, startswith = False, endswith = True)
                
                data_mat = loadmat(files_mat[0])
                                     
                xx = data_mat['Xp']
                yy = data_mat['Yp']        
                
                dx = xx - xq
                dy = yy - yq
                dis = np.sqrt(dx**2 + dy**2)
        
                min_dis = np.nanmin(dis)
                print('min distance = %.2f' % min_dis)
                min_ind = np.nanargmin(dis)
                print('min index = %d' % row_ind)
                min_dis_max_mat = max(min_dis, min_dis_max_mat)
                
                result['Xp']        = data_mat['Xp'].flatten()[min_ind]
                result['Yp']        = data_mat['Yp'].flatten()[min_ind]
                result['Depth']     = data_mat['Depth'].flatten()[min_ind]
                result['Hsig']      = data_mat['Hsig'].flatten()[min_ind]
                result['RTpeak']    = data_mat['RTpeak'].flatten()[min_ind]
                result['TPsmoo']    = data_mat['TPsmoo'].flatten()[min_ind]
                result['Tm_10']     = data_mat['Tm_10'].flatten()[min_ind]
                result['Tm01']      = data_mat['Tm01'].flatten()[min_ind]
                result['Tm02']      = data_mat['Tm02'].flatten()[min_ind]
                result['Dir']       = data_mat['Dir'].flatten()[min_ind]
                result['Dspr']      = data_mat['Dspr'].flatten()[min_ind]
                result['Wlen']      = data_mat['Wlen'].flatten()[min_ind]
                result['Dissip']    = data_mat['Dissip'].flatten()[min_ind]
                result['dHs']       = data_mat['dHs'].flatten()[min_ind]
                result['dTm']       = data_mat['dTm'].flatten()[min_ind]
                result['Watlev']    = data_mat['Watlev'].flatten()[min_ind]
                result['X-Windv']   = data_mat['Windv_x'].flatten()[min_ind]
                result['Y-Windv']   = data_mat['Windv_y'].flatten()[min_ind]
                result['X-Vel']     = data_mat['Vel_x'].flatten()[min_ind]
                result['Y-Vel']     = data_mat['Vel_y'].flatten()[min_ind]
                result['Botlev']    = data_mat['Botlev'].flatten()[min_ind]
                result['Qb']        = data_mat['Qb'].flatten()[min_ind]
                
                result['min_dis'] = min_dis
                result['min_ind'] = min_ind
                result['MAT_used']  = '1'
                result['TAB_used']  = '0'   
                
            # append data   
            appended_data_03.append(result)
                           
            del data, result, dis, xx, yy, xq, yq  
                        
        else: 
            print('OKid %s has no matching 1D profile' % OKid)
            no_match = no_match + 1
                                
appended_data_03 = pd.concat(appended_data_03)
print('maximum distace with SWAN output loc = %.2f' % min_dis_max)

#%% now write result to Excel

if save_excel_output:
    writer = pd.ExcelWriter(os.path.join(path_main,'output_productie_SWAN2D_WZ_v3.xlsx'), engine = 'xlsxwriter')
    appended_data_01.to_excel(writer, sheet_name = 'HRbasis')
    appended_data_02.to_excel(writer, sheet_name = 'HRext01_300m')
    appended_data_03.to_excel(writer, sheet_name = 'HRext01_600m')
    writer.save()
    writer.close()