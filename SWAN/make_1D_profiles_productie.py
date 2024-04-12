# -*- coding: utf-8 -*-
"""
--- Synopsis --- 
This scripts generates profiles for SWAN1D runs for the Westerschelde or Waddenzee.

--- Remarks --- 
See also: 
To-Do: 
Dependencies: 

--- Version --- 
Created on Tue Sep 27 10:54:36 2022
@author: ENGT2
Project: KP ZSS (130991)
Script name: make_1D_profiles_productie.py

--- Revision --- 
Status: Unverified 

Witteveen+Bos Consulting Engineers 
Leeuwenbrug 8
P.O. box 233 
7411 TJ Deventer
The Netherlands 
		
"""

#%% Import modules

import matplotlib.pyplot as plt
import numpy as np
import scipy.io
import os
from hmtoolbox.WB_basic.deg2uv import uv2deg
from shapely.ops import substring
import gc
from scipy.io import loadmat
from mpl_toolkits.axes_grid1 import make_axes_locatable

import geopandas as gpd
import pandas as pd
# import mat73

from hmtoolbox.WB_topo import interpolate, geometry_funcs
from hmtoolbox.WB_basic import save_plot

#%% Settings

gebied = 'WS' #'WZ'

# setup based on gebied parameter, dictionaries with scenes and mat files
if gebied == 'WS':
    base_path = r'z:\130991_Systeemanalyse_ZSS\2.Data\bathy\Final\WS\oplevering'
    # scene_dict = {'WS_NM_RF' : os.path.join(base_path, 'C - geen verandering\WS-25m_2021.mat'),
    #               'WS_VT_A1' : os.path.join(base_path, 'A1 - trends 2100\\bath2100_filled.mat'),
    #               'WS_VT_A2' : os.path.join(base_path, 'A2 - trends 2200\\bathy2200_filled.mat'),
    #               'WS_VM_B1' : os.path.join(base_path, 'B - meegroeien\\WS-25m_05.mat'),
    #               'WS_VM_B2' : os.path.join(base_path, 'B - meegroeien\\WS-25m_1.mat'),
    #               'WS_VM_B3' : os.path.join(base_path, 'B - meegroeien\\WS-25m_2.mat'),
    #               'WS_VM_B4' : os.path.join(base_path, 'B - meegroeien\\WS-25m_3.mat')}
    scene_dict = {'WS_VM_B4' : os.path.join(base_path, 'B - meegroeien\\WS-25m_3.mat')}
    
    
    path_profiles = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Westerschelde\02_productie\_profielen'
    file_profiles = os.path.join(path_profiles, 'HRD_locations_selectie_WS_profielen_extended_no_duplicates.shp')
       
    save_path = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Westerschelde\02_productie\_bodem'
    
elif gebied == 'WZ':
    base_path = r'z:\130991_Systeemanalyse_ZSS\2.Data\bathy\Final\WZ'
    scene_dict = {'WZ_NM_RF' : base_path+'Niet meegroeien\\0m = base_minimum_bathymetry\\Volledig_meegroeien_minimumbathy_0m_v6.mat',
                  'WZ_GM_A1' : base_path+'Gedeeltelijk meegroeien\\A-1 Gunstig_05m_Elev_meanBedChange_GW\\Gunstig_0.5m_Elev_meanBedChange_inclED_v6.mat',
                  'WZ_GM_B1' : base_path+'Gedeeltelijk meegroeien\\B-1 Gunstig_10m_Elev_meanBedChange_GW\\Gunstig_1.0m_Elev_meanBedChange_inclED_v6.mat',
                  'WZ_GM_C1' : base_path+'Gedeeltelijk meegroeien\\C-1 Gunstig_20m_Elev_meanBedChange_GW\\Gunstig_2.0m_Elev_meanBedChange_inclED_v6.mat',
                  'WZ_GM_D1' : base_path+'Gedeeltelijk meegroeien\\D-1 Gunstig_30m_Elev_meanBedChange_GW\\Gunstig_3.0m_Elev_meanBedChange_inclED_v6.mat',
                  'WZ_GM_B2' : base_path+'Gedeeltelijk meegroeien\\B-2 Ongunstig_10m_Elev_meanBedChange_GW\\Ongunstig_1.0m_Elev_meanBedChange_inclED_v6.mat',
                  'WZ_GM_C2' : base_path+'Gedeeltelijk meegroeien\\C-2 Ongunstig_20m_Elev_meanBedChange_GW\\Ongunstig_2.0m_Elev_meanBedChange_inclED_v6.mat',
                  'WZ_VM_F' : base_path+'Geheel meegroeien\\05m\\Volledig_meegroeien_minimumbathy_05m_v6.mat',
                  'WZ_VM_G' : base_path+'Geheel meegroeien\\1m\\Volledig_meegroeien_minimumbathy_1m_v6.mat',
                  'WZ_VM_H' : base_path+'Geheel meegroeien\\2m\\Volledig_meegroeien_minimumbathy_2m_v6.mat',
                  'WZ_VM_I' : base_path+'Geheel meegroeien\\3m\\Volledig_meegroeien_minimumbathy_3m_v6.mat'}
    
    path_profiles = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\_profielen'
    file_profiles = path_profiles+'\ill_pilot_v03_profielen_04_WZ.shp'
            
    save_path = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\_bodem'
    
else:
    raise UserWarning(f'{gebied} does not exist')
    
    
switch_fig = True
switch_output = True

# Interpolation settings
buffer = 100
spacing = 5

# Max length of 1D profile
max_len = 600

#%% load shape and make buffer
df_shp = gpd.read_file(file_profiles)

hubnames = df_shp['HubName']

for scene, file in scene_dict.items():
    print(scene)
    print(file)
    
    if gebied == 'WS':
        # load data using loadmat
        data = loadmat(file)

        x = data['grd'][0][0][0]
        y = data['grd'][0][0][1]
        z = data['grd'][0][0][2]
        
    elif gebied == 'WZ':
        # load data using mat73
        # data = mat73.loadmat(file)
        # data = scipy.io.loadmat(file)
        # x = data['grd']['x']
        # y = data['grd']['y']
        # z = data['grd']['dp']
        
        data = loadmat(file)

        x = data['grd'][0][0][0]
        y = data['grd'][0][0][1]
        z = data['grd'][0][0][2]
        
    for hubname in hubnames:
        
        print(hubname)

        df_shp_sel = df_shp[df_shp['HubName']==hubname]
        df_shp_sel = df_shp_sel.reset_index()
        
        df_shp_buffered = df_shp_sel.buffer(buffer)
    
        #%% find indices inside buffer and make df_xyz
        ind_inside = geometry_funcs.get_points_in_polygon(df_shp_buffered[0],x,y)
        
        df_xyz = pd.DataFrame({'x':x[ind_inside].ravel(),'y':y[ind_inside].ravel(),'z':z[ind_inside].ravel()})
        df_xyz = df_xyz.dropna()
        
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
        
        #%% make chain on shape
        chain = geometry_funcs.points_on_line(line,spacing,incl_end_point=False)
        chain_coords = []
        [chain_coords.append((c.coords.xy[0][0],c.coords.xy[1][0])) for c in chain]
        
        # make dataframe of chain
        df_xy = pd.DataFrame({'x':list(zip(*chain_coords))[0],'y':list(zip(*chain_coords))[1]})
        df_xy['z'] = np.zeros_like(df_xy['x'])
    
        #%% drape on xy
        interpolate.interpolate_xyz_on_xy(df_xyz,df_xy)
        
        #%% finish df_xy dataframe
        # limit to last valid index of z
        last_valid_ind = df_xy['z'].last_valid_index()
        df_xy = df_xy.iloc[:last_valid_ind]
           
        # calculate distance and fill out nans
        df_xy['distance'] = np.sqrt((df_xy['x']-df_xy['x'][0])**2+(df_xy['y']-df_xy['y'][0])**2)
        df_xy['zfilled'] = df_xy['z'].interpolate()
        
        # limit to specify max length
        df_xy = df_xy.drop(df_xy[df_xy['distance'] > max_len].index)
        
        # remove any remaining nans
        nanlist = list(np.where(df_xy['zfilled'].isnull())[0])
        for ix in nanlist:
            if ix == 0:
                df_xy['zfilled'][ix] = df_xy['zfilled'][nanlist[-1]+1]
            else:
                df_xy['zfilled'][ix] = df_xy['zfilled'][nanlist[-1]+1]    
    
        #%% show plot
        fig,ax = plt.subplots(1,2,figsize=(12,6))
        # df_shp_buffered.plot(ax = ax[0],color='lightgrey')
        s = ax[0].scatter(x[ind_inside],y[ind_inside],5,z[ind_inside],cmap='jet')
        ax[0].plot(df_xy['x'],df_xy['y'], color = 'k', linewidth = 2)
        # df_shp_sel.plot(ax = ax[0], color = 'red',linewidth=3)
        # ax[0].scatter(list(zip(*chain_coords))[0],list(zip(*chain_coords))[1],5,'k',zorder=10)
        
        divider = make_axes_locatable(ax[0])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(s, ax=ax[0], cax=cax)
        
        ax[0].set_xlabel('x-coord [m]')
        ax[0].set_ylabel('y-coord [m]')
        ax[0].set_title(f'bathy buffered with {buffer} m')
        ax[0].set_aspect('equal')
        
        ax[1].plot(df_xy['distance'],df_xy['z'],label='raw 1D profile')
        ax[1].plot(df_xy['distance'],df_xy['zfilled'],label='interpolated NaNs',zorder=0)
        ax[1].set_title(f'interpolated 1D bathy, spacing = {spacing} m, DN = {FC_DN}')
        ax[1].set_xlabel('distance [m]')
        ax[1].set_ylabel('height [m NAP]')
        ax[1].legend()
        
        box = ax[1].get_position()
        box.x0 = box.x0 + 0.02
        box.x1 = box.x1 + 0.02
        ax[1].set_position(box)
        # ymin = -5
        # ymax = 10
        
        # plt.ylim(ymin,ymax)
    
        # export to figure
        if switch_fig:
            save_name = os.path.join(save_path, f'{scene}_{hubname}_profile')
            save_plot.save_plot(fig,save_name,ax = ax[1])
        
        #%% export to text file
        if switch_output:
            save_bot = os.path.join(save_path, f'{scene}_{hubname}_bottom.txt')
            df_xy['zfilled'].to_csv(save_bot, index=False, header=False, float_format='%.3f')
            save_profile = os.path.join(save_path, f'{scene}_{hubname}_profile.txt')
            df_xy.to_csv(save_profile,sep=',', index=False, header=True, float_format='%.3f')
            
        plt.close('all')
        gc.collect()