# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 12:14:36 2022

@author: BEMC

script to generate 1D profiles for SWAN 1D simulations based on .mat files

"""

import matplotlib.pyplot as plt
import numpy as np
import scipy.io
import os
from hmtoolbox.WB_basic.deg2uv import uv2deg
from shapely.ops import substring

import geopandas as gpd
import pandas as pd
# import mat73

from hmtoolbox.WB_topo import interpolate, geometry_funcs
from hmtoolbox.WB_basic import save_plot

gebied = 'WZ' #'WZ'

# setup based on gebied parameter, dictionaries with scenes and mat files
if gebied == 'WS':
    base_path = 'z:\\130991_Systeemanalyse_ZSS\\2.Data\\bathy\\ontvangen\\WS\\oplevering\\'
    scene_dict = {'WS_NM_RF' : base_path+'C - geen verandering\\WS-25m_2021.mat',
                  'WS_VT_A1' : base_path+'A1 - trends 2100\\bath2100_filled.mat',
                  'WS_VT_A2' : base_path+'A2 - trends 2200\\bathy2200_filled.mat',
                  'WS_VM_B1' : base_path+'B - meegroeien\\WS-25m_05.mat',
                  'WS_VM_B2' : base_path+'B - meegroeien\\WS-25m_1.mat',
                  'WS_VM_B3' : base_path+'B - meegroeien\\WS-25m_2.mat',
                  'WS_VM_B4' : base_path+'B - meegroeien\\WS-25m_3.mat'}
    
    path_dummy = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Westerschelde\tests\_profielen'
    file_shape = path_dummy+'\ill_pilot_v02_profielen_02.shp'
    
    hubname = '29001016'
    
    save_path = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Westerschelde\tests\_bodem'
    
elif gebied == 'WZ':
    base_path = 'z:\\130991_Systeemanalyse_ZSS\\2.Data\\bathy\\ontvangen\\WZ\\'
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
    
    path_dummy = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\_profielen'
    file_shape = path_dummy+'\ill_pilot_v03_profielen_04_WZ.shp'
         
    hubname = '6003036'
    # hubname = '6004026'
    
    save_path = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\tests\_bodem'
    
else:
    raise UserWarning(f'{gebied} does not exist')
    

# path_dummy = r'z:\130991_Systeemanalyse_ZSS\2.Data\dummy'
# file_shape = os.path.join(path_dummy, '1D_voorland_transect_WS.shp')

switch_fig = True
switch_output = True

ymin = -5
ymax = 5

#%% input data
buffer = 100
spacing = 5

#%% load shape and make buffer
df_shp = gpd.read_file(file_shape)

df_shp = df_shp[df_shp['HubName']==hubname]
df_shp = df_shp.reset_index()

df_shp_buffered = df_shp.buffer(buffer)

from scipy.io import loadmat
for scene,file in scene_dict.items():
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

    #%% find indices inside buffer and make df_xyz
    ind_inside = geometry_funcs.get_points_in_polygon(df_shp_buffered[0],x,y)
    
    df_xyz = pd.DataFrame({'x':x[ind_inside].ravel(),'y':y[ind_inside].ravel(),'z':z[ind_inside].ravel()})
    df_xyz = df_xyz.dropna()
    
    #%% make sure line is oriented the right way
    # get line
    line = df_shp.geometry[0]
    linex, liney = line.coords.xy
    linexy = pd.DataFrame(list(zip(linex,liney)), columns=['x', 'y'])
    dx = linexy.x[1]-linexy.x[0]
    dy = linexy.y[1]-linexy.y[0]
    # determine line oriëntation
    lineori = uv2deg(dx,dy,convention = 'nautical')
    lineori = np.mod(lineori+180,360)
    diff = df_shp['SL_DIR'].iloc[0] - lineori
    if diff > 10:
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
    
    # remove any remaining nans
    nanlist = list(np.where(df_xy['zfilled'].isnull())[0])
    for ix in nanlist:
        if ix == 0:
            df_xy['zfilled'][ix] = df_xy['zfilled'][nanlist[-1]+1]
        else:
            df_xy['zfilled'][ix] = df_xy['zfilled'][nanlist[-1]+1]    

    #%% show plot
    fig,ax = plt.subplots(1,2,figsize=(12,6))
    df_shp_buffered.plot(ax = ax[0])
    ax[0].scatter(x[ind_inside],y[ind_inside],5,z[ind_inside])
    df_shp.plot(ax = ax[0], color = 'red',linewidth=3)
    ax[0].scatter(list(zip(*chain_coords))[0],list(zip(*chain_coords))[1],5,'k',zorder=10)
    
    ax[0].set_xlabel('x-coord [m]')
    ax[0].set_ylabel('y-coord [m]')
    ax[0].set_title(f'bathy buffered with {buffer} m')
    
    ax[1].plot(df_xy['distance'],df_xy['z'],label='raw 1D profile')
    ax[1].plot(df_xy['distance'],df_xy['zfilled'],label='interpolated NaNs',zorder=0)
    ax[1].set_title(f'interpolated 1D bathy, spacing = {spacing} m')
    ax[1].set_xlabel('distance [m]')
    ax[1].set_ylabel('height [m NAP]')
    ax[1].legend()
    plt.ylim(ymin,ymax)

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