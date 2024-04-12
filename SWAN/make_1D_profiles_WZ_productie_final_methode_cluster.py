# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 10:54:36 2022

This is a script to make 1D profiles for the Waddenzee, where a combination of Deltares bodem en AHN is needed.
This script uses a buffer of ca. 50m on the edge of the AHN data to interpolate between the two datasets

@author: ENGT2 + BADD
"""

#%% Import modules

import os
import gc
import scipy.io
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.io import loadmat
# from raster2xyz.raster2xyz import Raster2xyz
import matplotlib.pyplot as plt
from shapely.ops import substring
from hmtoolbox.WB_basic import save_plot
from hmtoolbox.WB_basic.deg2uv import uv2deg
from hmtoolbox.WB_topo import interpolate, geometry_funcs
from mpl_toolkits.axes_grid1 import make_axes_locatable

# %matplotlib qt

#%% Settings

base_path = r'/project/130991_Systeemanalyse_ZSS/2.Data/bathy/Final/WZ'
scene_ref = base_path+'//Niet meegroeien//0m = base_minimum_bathymetry//Volledig_meegroeien_minimumbathy_0m_v6.mat'
scene_dict = {'WZ_NM_RF' : base_path+'//Niet meegroeien//0m = base_minimum_bathymetry//Volledig_meegroeien_minimumbathy_0m_v6.mat',
              'WZ_GM_A1' : base_path+'//Gedeeltelijk meegroeien//A-1 Gunstig_05m_Elev_meanBedChange_GW//Gunstig_0.5m_Elev_meanBedChange_inclED_v2.mat',
              'WZ_GM_B1' : base_path+'//Gedeeltelijk meegroeien//B-1 Gunstig_10m_Elev_meanBedChange_GW//Gunstig_1.0m_Elev_meanBedChange_inclED.mat',
              'WZ_GM_C1' : base_path+'//Gedeeltelijk meegroeien//C-1 Gunstig_20m_Elev_meanBedChange_GW//Gunstig_2.0m_Elev_meanBedChange_inclED.mat',
              'WZ_GM_D1' : base_path+'//Gedeeltelijk meegroeien//D-1 Gunstig_30m_Elev_meanBedChange_GW//Gunstig_3.0m_Elev_meanBedChange_inclED.mat',
              'WZ_GM_B2' : base_path+'//Gedeeltelijk meegroeien//B-2 Ongunstig_10m_Elev_meanBedChange_GW//Ongunstig_1.0m_Elev_meanBedChange_inclED_V2.mat',
              'WZ_GM_C2' : base_path+'//Gedeeltelijk meegroeien//C-2 Ongunstig_20m_Elev_meanBedChange_GW//Ongunstig_2.0m_Elev_meanBedChange_inclED_V2.mat',
              'WZ_VM_F' : base_path+'//Geheel meegroeien//05m//Volledig_meegroeien_minimumbathy_05m_v6.mat',
              'WZ_VM_G' : base_path+'//Geheel meegroeien//1m//Volledig_meegroeien_minimumbathy_1m_v6.mat',
              'WZ_VM_H' : base_path+'//Geheel meegroeien//2m//Volledig_meegroeien_minimumbathy_2m_v6.mat',
              'WZ_VM_I' : base_path+'//Geheel meegroeien//3m//Volledig_meegroeien_minimumbathy_3m_v6.mat'}

path_profiles       = r'/project/130991_Systeemanalyse_ZSS/2.Data/GIS_TEMP'
file_profiles       = path_profiles+'/HRD_locations_selectie_WZ_profielen_extended_no_duplicates.shp'
ahn_poly            = r'/project/130991_Systeemanalyse_ZSS/2.Data/GIS_TEMP/polygon_ahntiles.shp'
okader_mid          = path_profiles+'/okader_fc_hydra_unique_handedit_WZ.shp'
path_ahn_rasters    = r'/project/130991_Systeemanalyse_ZSS/2.Data/profiles_ahn_deltares/ahn_tiles'
path_ahn_csv        = r'/project/130991_Systeemanalyse_ZSS/2.Data/ahn-csv'
        
save_path = r'/project/130991_Systeemanalyse_ZSS/3.Models/SWAN/1D/Waddenzee/02_productie/_bodem'
 
switch_fig = True
switch_output = True

#%% input data
buffer = 100
spacing = 5
radius = 50
max_len = 600
buffer_ahn_deltares = 50
max_dis_int = np.sqrt(2) * 50

#%% load shape and make buffer
df_shp = gpd.read_file(file_profiles)
df_okader = gpd.read_file(okader_mid)

hubnames = df_shp['HubName']

for scene, file in scene_dict.items():
    print(scene)
    print(file)
    
    data = loadmat(file)
    x = data['grd'][0][0][0]
    y = data['grd'][0][0][1]
    z = data['grd'][0][0][2]
    z[abs(z)>100] = np.nan
    
    data_ref = loadmat(scene_ref)
    x_ref = data_ref['grd'][0][0][0]
    y_ref = data_ref['grd'][0][0][1]
    z_ref = data_ref['grd'][0][0][2]
    z_ref[abs(z_ref)>100] = np.nan
        
    for hubname in hubnames:
        
        print(hubname)

        # make buffer around profile
        df_shp_sel = df_shp[df_shp['HubName']==hubname]
        df_shp_sel = df_shp_sel.reset_index()
        df_shp_buffered = df_shp_sel.buffer(buffer)

        # check in which ahn-tile the profile is located (fully contained)
        df_ahn = gpd.read_file(ahn_poly)
        df_ahn_check = df_ahn[df_ahn.contains(df_shp_buffered[0])]['layer']

        # check how many tiles
        # if one match, continue
        if len(df_ahn_check) == 1:
            print('One match')

        # if no match with (fully contained), try overlap (not fully contained)
        elif len(df_ahn_check) == 0:
            print('No match, so check overlap')
            df_ahn_check = df_ahn[df_ahn.overlaps(df_shp_buffered[0])]['layer']

            if len(df_ahn_check) == 0:
                print('Still no match')

        # if overlap results in more than one match, pick ahn tile in which okadervak midpoint is located
        if len(df_ahn_check) > 1:
            print('More than one match, pick match based on location okader midpoint')
            df_okader_sel = df_okader[df_okader['VakId'].values == str(hubname)]['geometry']
            df_okader_sel = df_okader_sel.reset_index()
            df_okader_buf = df_okader_sel.buffer(0.0001)
            df_ahn_check = df_ahn[df_ahn.contains(df_okader_buf[0])]['layer']
            
        print(f'Profile of okadervak {hubname}, is located in {df_ahn_check.iloc[0]}')
        input_raster = path_ahn_rasters + df_ahn_check.iloc[0]   
        out_csv = os.path.join(path_ahn_csv, (df_ahn_check.iloc[0] + '.csv'))

        ahn_csv = pd.read_csv(out_csv, delimiter = ',')
        # ahn_csv = ahn_csv[ahn_csv['z'] != 3.4028235e+38]
        ahn_csv = ahn_csv.drop(ahn_csv[ahn_csv['z'] > 100].index)
        x_ahn = ahn_csv['x']
        y_ahn = ahn_csv['y']
        z_ahn = ahn_csv['z']
    
        #%% find indices inside buffer and make df_xyz, for bathy and ahn
        
        ind_inside = geometry_funcs.get_points_in_polygon(df_shp_buffered[0],x,y)
        ind_inside_ahn = geometry_funcs.get_points_in_polygon(df_shp_buffered[0],x_ahn.values,y_ahn.values)
        
        # deltares bathy's
        df_xyz_ref  = pd.DataFrame({'x':x_ref[ind_inside].ravel(),'y':y_ref[ind_inside].ravel(),'z':z_ref[ind_inside].ravel()})        
        df_xyz_scen = pd.DataFrame({'x':x[ind_inside].ravel(),'y':y[ind_inside].ravel(),'z':z[ind_inside].ravel()})
        df_xyz_int  = pd.DataFrame({'x':x[ind_inside].ravel(),'y':y[ind_inside].ravel(),'z':z[ind_inside].ravel()})
        
        # ahn bathy
        df_xyz_ahn  = pd.DataFrame({'x':x_ahn[ind_inside_ahn].ravel(),'y':y_ahn[ind_inside_ahn].ravel(),'z':z_ahn[ind_inside_ahn].ravel()})
        
        # remove nan's
        df_xyz_scen = df_xyz_scen.dropna()
        df_xyz_int  = df_xyz_int.dropna()
        df_xyz_ahn = df_xyz_ahn.dropna()
        
        #%% make sure line is oriented the right way
        
        # get line
        line = df_shp_sel.geometry[0]
        linex, liney = line.coords.xy
        linexy = pd.DataFrame(list(zip(linex,liney)), columns=['x', 'y'])
        dx = linexy.x[1]-linexy.x[0]
        dy = linexy.y[1]-linexy.y[0]

        # determine line oriëntation
        lineori = uv2deg(dx,dy,convention = 'nautical')
        lineori = np.mod(lineori+180,360)
        FC_DN = int(df_shp_sel['FC_DN'].iloc[0])
        diff = FC_DN - lineori
        if diff > 90:
            print('== line orientation switched')
            line = substring(line, 1, 0, normalized=True)
        else:
            print('== line orientation is ok')  
        
        #%% make chain on shape and make dataframes for bathy
        
        # chainage of coordinates
        chain = geometry_funcs.points_on_line(line,spacing,incl_end_point=False)
        chain_coords = []
        [chain_coords.append((c.coords.xy[0][0],c.coords.xy[1][0])) for c in chain]
         
        # deltares bathy's
        df_xy_ref           = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_xy_ref['z']      = np.zeros_like(df_xy_ref['x'])
        df_xy_scen          = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_xy_scen['z']     = np.zeros_like(df_xy_scen['x'])
        df_xy_int           = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_xy_int['z']      = np.zeros_like(df_xy_int['x'])

        # ahn bathy
        df_xy_ahn_ref       = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_xy_ahn_ref['z']  = np.zeros_like(df_xy_ahn_ref['x'])
        df_xy_ahn_scen      = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_xy_ahn_scen['z'] = np.zeros_like(df_xy_ahn_scen['x'])
               
        # combined bathy
        df_xy_comb          = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_xy_comb['z']     = np.zeros_like(df_xy_comb['x'])
        
        # delta h (difference deltares bathy and referentie)
        df_dh               = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_dh['dh']         = np.zeros_like(df_dh['x'])
        
        # calculate distance
        df_xy_ref['distance']   = np.sqrt((df_xy_ref['x']-df_xy_ref['x'][0])**2+(df_xy_ref['y']-df_xy_ref['y'][0])**2)
        df_xy_scen['distance']  = np.sqrt((df_xy_scen['x']-df_xy_scen['x'][0])**2+(df_xy_scen['y']-df_xy_scen['y'][0])**2)
        df_xy_int['distance']   = np.sqrt((df_xy_int['x']-df_xy_int['x'][0])**2+(df_xy_int['y']-df_xy_int['y'][0])**2)

        df_xy_ahn_ref['distance']   = np.sqrt((df_xy_ahn_ref['x']-df_xy_ahn_ref['x'][0])**2+(df_xy_ahn_ref['y']-df_xy_ahn_ref['y'][0])**2)   
        df_xy_ahn_scen['distance']  = np.sqrt((df_xy_ahn_scen['x']-df_xy_ahn_scen['x'][0])**2+(df_xy_ahn_scen['y']-df_xy_ahn_scen['y'][0])**2)
        
        df_xy_comb['distance']      = np.sqrt((df_xy_comb['x']-df_xy_comb['x'][0])**2+(df_xy_comb['y']-df_xy_comb['y'][0])**2)
        
        # limit profiles to specified max length
        df_xy_ref   = df_xy_ref.drop(df_xy_ref[df_xy_ref['distance'] > max_len].index)
        df_xy_scen  = df_xy_scen.drop(df_xy_scen[df_xy_scen['distance'] > max_len].index)
        df_xy_int   = df_xy_int.drop(df_xy_int[df_xy_int['distance'] > max_len].index)

        df_xy_ahn_ref   = df_xy_ahn_ref.drop(df_xy_ahn_ref[df_xy_ahn_ref['distance'] > max_len].index)
        df_xy_ahn_scen   = df_xy_ahn_scen.drop(df_xy_ahn_scen[df_xy_ahn_scen['distance'] > max_len].index)

        df_xy_comb  = df_xy_comb.drop(df_xy_comb[df_xy_comb['distance'] > max_len].index)

        #%% Drape deltares bathy and ahn on profile
              
        # deltares bathy
        interpolate.interpolate_xyz_on_xy(df_xyz_ref, df_xy_ref,acceptable_dist_from_points=max_dis_int)
        interpolate.interpolate_xyz_on_xy(df_xyz_scen, df_xy_scen,acceptable_dist_from_points=max_dis_int)
        # ahn bathy
        interpolate.interpolate_xyz_on_xy(df_xyz_ahn, df_xy_ahn_ref,acceptable_dist_from_points=max_dis_int)
        
        #%% Add dh to ahn data
        
        # determine the first nan of the ahn dataset
        buff_data_outside = df_xy_ahn_ref['z'][::-1].notnull().idxmax()
        
        # first remove nans
        df_xy_ref[df_xy_ref['z']<-100]['z'] = np.nan
        df_xy_scen[df_xy_scen['z']<-100]['z'] = np.nan
        
        df_dh['z_ref'] = df_xy_ref['z']
        df_dh['z_scen'] = df_xy_scen['z']
        df_dh['dh'] = df_dh['z_scen'] - df_dh['z_ref'] 
        df_dh[df_dh['dh']>10] = np.nan
        df_dh[df_dh['dh']<-10] = np.nan 
        dh_mean = np.nanmean(df_dh['dh'][0:buff_data_outside])
        if np.isnan(dh_mean):
            dh_mean = 0
                      
        # add dh to ahn data
        df_xy_ahn_scen['z'] = df_xy_ahn_ref['z'] +  dh_mean
        
        #%% Remove Deltares bathy points higher than ahn within circle with specified radius
                
        # remove points if condition is met
        extra_marge = 0.5
        buffer_del = np.sqrt(2)*radius
        for i in range(len(df_xyz_int)):
            if df_xyz_int['x'].iloc[i] < df_xy_ahn_scen.loc[buff_data_outside]['x'] + buffer_del and \
                df_xyz_int['x'].iloc[i] > df_xy_ahn_scen.loc[buff_data_outside]['x'] - buffer_del and \
                df_xyz_int['y'].iloc[i] < df_xy_ahn_scen.loc[buff_data_outside]['y'] + buffer_del and \
                df_xyz_int['y'].iloc[i] > df_xy_ahn_scen.loc[buff_data_outside]['y'] - buffer_del and \
                df_xyz_int['z'].iloc[i] > df_xy_ahn_scen.loc[buff_data_outside]['z'] - extra_marge:
                    df_xyz_int['z'].iloc[i] = np.nan
            else:
                print('no points removed in Deltares bathy')        
        
        # Interpolate modified Deltares bathy to profile
        interpolate.interpolate_xyz_on_xy(df_xyz_int, df_xy_int,acceptable_dist_from_points=max_dis_int)
        interpolate.interpolate_xyz_on_xy(df_xyz_int, df_xy_comb,acceptable_dist_from_points=max_dis_int)
        
        # if ahn-data is available, replace values from deltares bathy with the values from ahn
        df_xy_comb.loc[df_xy_ahn_scen['z'].notnull().values] = df_xy_ahn_scen.loc[df_xy_ahn_scen['z'].notnull().values]
                                 
        #%% finish df_xy dataframe
                          
        # fill out nans
        df_xy_comb['zfilled'] = df_xy_comb['z'].interpolate()
               
        # remove any remaining nans
        nanlist = list(np.where(df_xy_comb['zfilled'].isnull())[0])
        for ix in nanlist:
            if ix == 0:
                df_xy_comb['zfilled'][ix] = df_xy_comb['zfilled'][nanlist[-1]+1]
            else:
                df_xy_comb['zfilled'][ix] = df_xy_comb['zfilled'][nanlist[-1]+1]    
                
        # limit to last valid index of z
        last_valid_ind = df_xy_comb['z'].last_valid_index()
        df_xy_comb = df_xy_comb.iloc[:last_valid_ind]

        #%% plot results
        
        fig,ax = plt.subplots(1,2,figsize=(16,6))
        fig.patch.set_facecolor('white')
        
        # plot samples and profile (top view)
        zs = np.concatenate([z_ahn.values[ind_inside_ahn], z[ind_inside]], axis = 0)
        z_min, z_max = np.nanmin(zs), np.nanmax(zs)
       
        s = ax[0].scatter(x_ahn.values[ind_inside_ahn],y_ahn.values[ind_inside_ahn],2,z_ahn.values[ind_inside_ahn],cmap='jet', vmin=z_min, vmax=z_max) 
        # t = ax[0].scatter(x[ind_inside],y[ind_inside],15,z[ind_inside],cmap='jet', edgecolor = 'k', linewidth = 0.2, vmin=z_min, vmax=z_max)
        t = ax[0].scatter(df_xyz_int['x'], df_xyz_int['y'], 15, df_xyz_int['z'], cmap='jet', edgecolor = 'k', linewidth = 0.2, vmin=z_min, vmax=z_max)
        ax[0].plot(df_xy_ref['x'],df_xy_ref['y'], color = 'k', linewidth = 1)
        
        ax[0].set_xlabel('x [m]')
        ax[0].set_ylabel('y [m]')
        ax[0].set_title(f'Deltares & AHN samples ({buffer} m buffer)')
        ax[0].set_xlim([df_xy_ref['x'][0] - 610, df_xy_ref['x'][0] + 610])
        ax[0].set_ylim([df_xy_ref['y'][0] - 610, df_xy_ref['y'][0] + 610])
        ax[0].grid(visible=True, which='major', axis='both')
        ax[0].set_aspect('equal','box')
       
        divider = make_axes_locatable(ax[0])
        cax = divider.append_axes("right", size=0.15, pad=0.05)
        cbar = fig.colorbar(s, ax=ax[0], cax=cax)
        cbar.set_label('bodemhoogte (m +NAP)')
        
        ### plot interpolated bathy along profile
        
        # deltares bathy
        ax[1].plot(df_xy_ref['distance'],df_xy_ref['z'],'-',color='c',label='Deltares referentie',linewidth = 2)
        ax[1].plot(df_xy_scen['distance'],df_xy_scen['z'],'-',color='c',label='Deltares scenario',linewidth = 4)
        # ax[1].plot(df_xy_int['distance'],df_xy_int['z'],'-',color='r',label='Deltares interp',linewidth = 4)
        
        # ahn bathy
        ax[1].plot(df_xy_ahn_ref['distance'],df_xy_ahn_ref['z'],'-',color='tab:pink',label='AHN referentie',linewidth = 2)
        ax[1].plot(df_xy_ahn_scen['distance'],df_xy_ahn_scen['z'],'-',color='tab:pink',label='AHN scenario',linewidth = 4)
        
        # interpolation between AHN and Deltares
        # ax[1].plot(df_xy_comb.loc[buff_data_outside-1:(buff_data_outside+buffer_steps+1), 'distance'],df_xy_comb.loc[buff_data_outside-1:(buff_data_outside+buffer_steps+1), 'zfilled'],'-',color='y',label='overgang AHN en Deltares',linewidth = 4)

        # filled in nan's
        ax[1].plot(df_xy_comb['distance'],df_xy_comb['zfilled'],'-',color='tab:orange',label='geïnterpoleerde NaNs',zorder=0,linewidth = 4)
              
        # final bathy
        ax[1].plot(df_xy_comb['distance'],df_xy_comb['zfilled'],':',color='k',label='SWAN1D profiel',linewidth = 2)
        
        ax[1].set_title(f'Bodemhoogte langs profiel, dx = {spacing} m, DN = {FC_DN}, delta_ahn = {dh_mean:.2f} m')
        ax[1].set_xlabel('afstand [m]')
        ax[1].set_ylabel('bodemhoogte [m +NAP]')
        ax[1].legend()
        ax[1].grid(visible=True, which='major', axis='both')
        
        box = ax[1].get_position()
        box.x0 = box.x0 + 0.02
        box.x1 = box.x1 + 0.02
        ax[1].set_position(box)
        
        fig.tight_layout()
    
        # export figure
        if switch_fig:
            save_name = os.path.join(save_path, f'{scene}_{hubname}_profile')
            save_plot.save_plot(fig,save_name,ax = ax[1])
                    
        #%% export to text file
        if switch_output:
            save_bot = os.path.join(save_path, f'{scene}_{hubname}_bottom.txt')
            df_xy_comb['zfilled'].to_csv(save_bot, index=False, header=False, float_format='%.3f')
            save_profile = os.path.join(save_path, f'{scene}_{hubname}_profile.txt')
            df_xy_comb.to_csv(save_profile,sep=',', index=False, header=True, float_format='%.3f')
        
        plt.close('all')
        gc.collect()