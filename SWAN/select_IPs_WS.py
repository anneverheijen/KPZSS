# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 14:43:06 2022

@author: ENGT2
"""

#%% load modules

import os
import pandas as pd
import numpy as np
import scipy
import matplotlib
import matplotlib.pyplot as plt
# %matplotlib qt
from hmtoolbox.WB_basic import save_plot
from hmtoolbox.WB_basic import save_plot_mod

#%% settings

dirs = {'input':    r'z:\130991_Systeemanalyse_ZSS\5.Results\Hydra-NL_HBN',
        'output':   r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Westerschelde\03_productiesommen\serie_01\input'}

files = {'hyd_output':  'Westerschelde_HBN_v3.csv'}

# scenarios = df_hyd['ZSS-scenario'].unique()
scenarios = ["'KPZSS_2023_Referentie'", 
             "'KPZSS_2100_Laag'", "'KPZSS_2100_Extreem'", "'KPZSS_2100_Zeer_extreem'", 
             "'KPZSS_2200_Laag'", "'KPZSS_2200_Gematigd'", "'KPZSS_2200_Extreem'"]

save_excel  = False
save_fig    = False

scenario_sel = scenarios[0]

# set bins
h_bins = np.array([2,3,4,5,6,7,8,9,10,11,12])
ws_bins = np.array([16,19,22,25,28,31,34,37,40,43,46,49])
wdir_vals = np.array([60,180,240,270,300,330,360])

#%% read hydra-NL output data

df_hyd  = pd.read_csv(os.path.join(dirs['input'],files['hyd_output']), sep=';')

#%% first plot IP's for all ZSS scenario's

plt.close('all')

fig_01 = plt.figure()
colors = ['k','g','b','r','b','r','m']

nloc = len(df_hyd['OKADER VakId'].unique())
nscen = len(scenarios)
okid_mat = np.zeros((nloc,nscen))

ix = 0
for scenario in scenarios:
    is_scen =  df_hyd['ZSS-scenario']==scenario
    df_hyd_scen = df_hyd[is_scen]
    df_hyd_scen_sort = df_hyd_scen.sort_values('OKADER VakId')
    df_hyd_scen_sort = df_hyd_scen_sort.reset_index()
    df_hyd_scen_sort['index1'] = df_hyd_scen_sort.index
    okid_mat[:,ix] = df_hyd_scen_sort['OKADER VakId'].to_numpy()
    plt.subplot(3,1,1)
    s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['windsnelheid [m/s]'],5,colors[ix])
    s = plt.plot(df_hyd_scen_sort['index1'],df_hyd_scen_sort['windsnelheid [m/s]'],colors[ix],label=scenario)
    plt.grid()
    plt.xlabel('locatie')
    plt.ylabel('windsnelheid [m/s]')
    plt.legend()
    
    plt.subplot(3,1,2)
    s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['windrichting [graden N]'],5,colors[ix])
    s = plt.plot(df_hyd_scen_sort['index1'],df_hyd_scen_sort['windrichting [graden N]'],colors[ix],label=scenario)
    plt.grid()
    plt.xlabel('locatie')
    plt.ylabel('windrichting [graden N]')
    plt.legend()
    
    plt.subplot(3,1,3)
    s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['h, teen [m+NAP]'],5,colors[ix])
    s = plt.plot(df_hyd_scen_sort['index1'],df_hyd_scen_sort['h, teen [m+NAP]'],colors[ix],label=scenario)
    plt.grid()
    plt.xlabel('locatie')
    plt.ylabel('h, teen [m+NAP]')
    plt.legend()
    
    ix = ix + 1

# check if OKADER vakken are ordered in the same way for all plots
okid_mat_diff = np.diff(okid_mat,axis=1)
if okid_mat_diff.max() !=0:
    print('OKADER VakIds are not ordered in the same way')
else:
    print('OKADER VakIds are ordered in the same way')

if save_fig:
    name = f'output_hydra_vergelijking_ZSS.png'
    fname = os.path.join(dirs['output'],name)
    save_plot_mod.save_plot(fig_01, fname, incl_wibo = False, dpi = 300, 
              change_size = True, figwidth = 14, figheight = 10)
    
#%% plot IP parameters for specified scenario

# filter on scenario

is_scen =  df_hyd['ZSS-scenario']==scenario_sel
df_hyd_scen = df_hyd[is_scen]
df_hyd_scen_sort = df_hyd_scen.sort_values('OKADER VakId')
df_hyd_scen_sort = df_hyd_scen_sort.reset_index()
df_hyd_scen_sort['index1'] = df_hyd_scen_sort.index

hbn_min = round(min(df_hyd_scen_sort['HBN [m+NAP]']) / 2) * 2
hbn_max = round(max(df_hyd_scen_sort['HBN [m+NAP]']) / 2) * 2
hbn_step = 2
hbn_nstep = int((hbn_max - hbn_min)/hbn_step)
hbn_range = list(range(hbn_min, hbn_max + hbn_step, hbn_step))

ws_min = round(min(df_hyd_scen_sort['windsnelheid [m/s]']) / 2) * 2
ws_max = round(max(df_hyd_scen_sort['windsnelheid [m/s]']) / 2) * 2
ws_step = 3
ws_nstep = int((ws_max - ws_min)/ws_step)
ws_range = list(range(ws_min, ws_max + ws_step, ws_step))

hs_min = round(min(df_hyd_scen_sort['Hm0, teen [m]']) / 2) * 2
hs_max = round(max(df_hyd_scen_sort['Hm0, teen [m]']) / 2) * 2
hs_step = 1
hs_nstep = int((hs_max - hs_min)/hs_step)
hs_range = list(range(hs_min, hs_max + hs_step, hs_step))

h_min = round(min(df_hyd_scen_sort['h, teen [m+NAP]']) / 2) * 2
h_max = round(max(df_hyd_scen_sort['h, teen [m+NAP]']) / 2) * 2
h_step = 1
h_nstep = int((h_max - h_min)/h_step)
h_range = list(range(h_min, h_max + h_step, h_step))

dir_min = round(min(df_hyd_scen_sort['windrichting [graden N]']) / 2) * 2
dir_max = round(max(df_hyd_scen_sort['windrichting [graden N]']) / 2) * 2
dir_step = 30
dir_nstep = int((dir_max - dir_min)/dir_step)
dir_range = list(range(dir_min, dir_max + dir_step, dir_step))


### spatial plot

fig_02 = plt.figure()

cmap = plt.get_cmap('jet', hbn_nstep)

plt.subplot(3,2,1)
s = plt.scatter(df_hyd_scen_sort['HYD_location_X'],df_hyd_scen_sort['HYD_location_Y'],10,df_hyd_scen_sort['HBN [m+NAP]'],cmap=cmap,vmin=hbn_min,vmax=hbn_max)
plt.xlabel('x (m)')
plt.ylabel('y (m)')
fig_02.colorbar(s, orientation='vertical', label='HBN [m+NAP]',boundaries = hbn_range,ticks = hbn_range)
plt.grid()
plt.axis('equal')

cmap = plt.get_cmap('jet', ws_nstep)

plt.subplot(3,2,4)
s = plt.scatter(df_hyd_scen_sort['HYD_location_X'],df_hyd_scen_sort['HYD_location_Y'],10,df_hyd_scen_sort['windsnelheid [m/s]'],cmap=cmap,vmin=ws_min,vmax=ws_max)
plt.xlabel('x (m)')
plt.ylabel('y (m)')
# plt.clim(20,45)
fig_02.colorbar(s, orientation='vertical', label='windsnelheid [m/s]',boundaries = ws_range,ticks = ws_range)
plt.grid()
plt.axis('equal')

cmap = plt.get_cmap('jet', h_nstep)

plt.subplot(3,2,2)
s = plt.scatter(df_hyd_scen_sort['HYD_location_X'],df_hyd_scen_sort['HYD_location_Y'],10,df_hyd_scen_sort['h, teen [m+NAP]'],cmap=cmap,vmin=h_min,vmax=h_max)
plt.xlabel('x (m)')
plt.ylabel('y (m)')
# plt.clim(5,9)
fig_02.colorbar(s, orientation='vertical', label='h, teen [m+NAP]',boundaries = h_range,ticks = h_range)
plt.grid()
plt.axis('equal')

cmap = plt.get_cmap('jet', dir_nstep)

plt.subplot(3,2,6)
s = plt.scatter(df_hyd_scen_sort['HYD_location_X'],df_hyd_scen_sort['HYD_location_Y'],10,df_hyd_scen_sort['windrichting [graden N]'],cmap=cmap,vmin=dir_min,vmax=dir_max)
plt.xlabel('x (m)')
plt.ylabel('y (m)')
# plt.clim(230,360)
fig_02.colorbar(s, orientation='vertical', label='windrichting [graden N]',boundaries = dir_range,ticks = dir_range)
plt.grid()
plt.axis('equal')

cmap = plt.get_cmap('jet', hs_nstep)

plt.subplot(3,2,3)
s = plt.scatter(df_hyd_scen_sort['HYD_location_X'],df_hyd_scen_sort['HYD_location_Y'],10,df_hyd_scen_sort['Hm0, teen [m]'],cmap=cmap,vmin=hs_min,vmax=hs_max)
plt.xlabel('x (m)')
plt.ylabel('y (m)')
# plt.clim(0,5)
fig_02.colorbar(s, orientation='vertical', label='Hm0 [m]',boundaries = hs_range,ticks = hs_range)
plt.grid()
plt.axis('equal')

fig_02.tight_layout()

plt.show()

plt.rcParams.update({'font.size': 8})

if save_fig:
    namestr = scenario_sel[1:-1]
    name = f'output_hydra_ruimtelijk_{namestr}.png'
    fname = os.path.join(dirs['output'],name)
    save_plot_mod.save_plot(fig_02, fname, incl_wibo = False, dpi = 300, 
              change_size = True, figwidth = 12, figheight = 8)
    
#%% location plots

# limits = [0, 32, 38, 48, 88, 110, 143, len(df_hyd_scen_sort['index1'])]

fig_03 = plt.figure()

cmap = plt.get_cmap('jet', hbn_nstep)

plt.subplot(3,2,1)
s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['HBN [m+NAP]'],10,df_hyd_scen_sort['HBN [m+NAP]'],cmap=cmap,vmin=hbn_min,vmax=hbn_max)
plt.xlabel('locatie')
fig_03.colorbar(s, orientation='vertical', label='HBN [m+NAP]',boundaries = hbn_range,ticks = hbn_range)
plt.grid()
ax =plt.gca()
ymin,ymax = ax.get_ylim()
# plt.vlines(limits, ymin, ymax, colors='k', linestyles='dashed')

cmap = plt.get_cmap('jet', ws_nstep)

plt.subplot(3,2,4)
s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['windsnelheid [m/s]'],10,df_hyd_scen_sort['windsnelheid [m/s]'],cmap=cmap,vmin=ws_min,vmax=ws_max)
plt.xlabel('locatie')
# plt.clim(20,45)
fig_03.colorbar(s, orientation='vertical', label='windsnelheid [m/s]',boundaries = ws_range,ticks = ws_range)
plt.grid()
ax =plt.gca()
ymin,ymax = ax.get_ylim()
# plt.vlines(limits, ymin, ymax, colors='k', linestyles='dashed')

cmap = plt.get_cmap('jet', h_nstep)

plt.subplot(3,2,2)
s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['h, teen [m+NAP]'],10,df_hyd_scen_sort['h, teen [m+NAP]'],cmap=cmap,vmin=h_min,vmax=h_max)
plt.xlabel('locatie')
# plt.clim(5,9)
fig_03.colorbar(s, orientation='vertical', label='h, teen [m+NAP]',boundaries = h_range,ticks = h_range)
plt.grid()
ax =plt.gca()
ymin,ymax = ax.get_ylim()
# plt.vlines(limits, ymin, ymax, colors='k', linestyles='dashed')

cmap = plt.get_cmap('jet', dir_nstep)

plt.subplot(3,2,6)
s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['windrichting [graden N]'],10,df_hyd_scen_sort['windrichting [graden N]'],cmap=cmap,vmin=dir_min,vmax=dir_max)
plt.xlabel('locatie')
# plt.clim(230,360)
fig_03.colorbar(s, orientation='vertical', label='windrichting [graden N]',boundaries = dir_range,ticks = dir_range)
plt.grid()
ax =plt.gca()
ymin,ymax = ax.get_ylim()
# plt.vlines(limits, ymin, ymax, colors='k', linestyles='dashed')

cmap = plt.get_cmap('jet', hs_nstep)

plt.subplot(3,2,3)
s = plt.scatter(df_hyd_scen_sort['index1'],df_hyd_scen_sort['Hm0, teen [m]'],10,df_hyd_scen_sort['Hm0, teen [m]'],cmap=cmap,vmin=hs_min,vmax=hs_max)
plt.xlabel('locatie')
# plt.clim(0,5)
fig_03.colorbar(s, orientation='vertical', label='Hm0 [m]',boundaries = hs_range,ticks = hs_range)
plt.grid()
ax =plt.gca()
ymin,ymax = ax.get_ylim()
# plt.vlines(limits, ymin, ymax, colors='k', linestyles='dashed')

fig_03.tight_layout()

plt.show()

plt.rcParams.update({'font.size': 8})

if save_fig:
    namestr = scenario_sel[1:-1]
    name = f'output_hydra_locatie_{namestr}.png'
    fname = os.path.join(dirs['output'],name)
    save_plot_mod.save_plot(fig_03, fname, incl_wibo = False, dpi = 300, 
              change_size = True, figwidth = 12, figheight = 8)

#%% bin IP data for selected scenario

# filter on scenario

is_scen =  df_hyd['ZSS-scenario']==scenario_sel
df_hyd_scen = df_hyd[is_scen]
df_hyd_scen_sort = df_hyd_scen.sort_values('OKADER VakId')
df_hyd_scen_sort = df_hyd_scen_sort.reset_index()
df_hyd_scen_sort['index1'] = df_hyd_scen_sort.index

# plt.close('all')

# extract hydra-NL data 
h   = df_hyd_scen_sort['h, teen [m+NAP]']
ws  = df_hyd_scen_sort['windsnelheid [m/s]']
wdir = df_hyd_scen_sort['windrichting [graden N]']
okid = df_hyd_scen_sort['OKADER VakId']

# make a mesh (for plotting purposes)
X,Y = np.meshgrid(h_bins,ws_bins)
X = np.transpose(X)
Y = np.transpose(Y)

# allocate some stuff
binning = pd.DataFrame()
okids = []
okids_na = []
okids_as = []
okids_total = []
ix = 0

# bin data
for wdir_val in wdir_vals:
    for h_bottom, h_top in zip(h_bins[:-1], h_bins[1:]):
        for ws_bottom, ws_top in zip(ws_bins[:-1], ws_bins[1:]):
            ids = np.where((h>=h_bottom) & (h<h_top) & (ws>=ws_bottom) & (ws<ws_top) & (wdir==wdir_val))
            ids_temp = np.array(ids)
            numel = ids_temp.size
            if numel == 0:
                okids = []
            elif wdir_val == 60 or wdir_val == 180 or wdir_val == 360 or numel == 1:
                for id in np.nditer(ids):
                    okids_na.append(np.array(okid.iloc[id]))
            else:
                for id in np.nditer(ids):
                    okids_as.append(np.array(okid.iloc[id]))
                okids = okid.iloc[ids]
                h_locs = h.iloc[ids]
                h_mean = h_locs.mean()
                ws_locs = ws.iloc[ids]
                ws_mean = ws_locs.mean()
                data = {'wdir': wdir_val,
                        'h_bottom': h_bottom,
                        'h_top': h_top,
                        'ws_bottom': ws_bottom,
                        'ws_top': ws_top,
                        'ids': ids,
                        'numel': numel,
                        'okids': (np.array([]), ),
                        'h_locs': (np.array([]), ),
                        'h_mean': h_mean,
                        'ws_locs': (np.array([]), ),
                        'ws_mean': ws_mean}
                df_temp = pd.DataFrame(data)
                df_temp.at[0,'okids'] = np.array(okids)
                df_temp.at[0,'h_locs'] = np.array(h_locs)
                df_temp.at[0,'ws_locs'] = np.array(ws_locs)
                binning = binning.append(df_temp, ignore_index=True)
                
# check if all okids are covered (either assigned or not assigned)
print('== total of %d okader vakken allocated in bins' % binning['numel'].sum())
print('== %d okader vakken not allocated' % (len(df_hyd_scen['OKADER VakId'])-binning['numel'].sum()))

okids_total = np.concatenate((okids_as, okids_na), axis=0)
okids_total = np.sort(okids_total)
okid_mat_diff = np.array(df_hyd_scen_sort['OKADER VakId']) - okids_total
if okid_mat_diff.max() !=0:
    print('all OKADER VakIds are covered')
else:
    print('NOT all OKADER VakIds are covered')

# save result
if save_excel:         
    binning.to_excel(os.path.join(dirs['output'],'IP_binning_WS_%s.xlsx' % scenario_sel[1:-1]))


#%% allocated okader ids that have not been allocated yet (NOT WORKING YET)

x = df_hyd_scen_sort['HYD_location_X']
y = df_hyd_scen_sort['HYD_location_Y']

okid_nearest = []

for id in okids_na:
    xloc = df_hyd_scen_sort[df_hyd_scen_sort['OKADER VakId']==id]['HYD_location_X']
    yloc = df_hyd_scen_sort[df_hyd_scen_sort['OKADER VakId']==id]['HYD_location_Y']
    dx = x-xloc.iloc[0]
    dy = y-yloc.iloc[0]
    dis = np.sqrt(np.square(dx)+np.square(dy))
    idx = dis.argmin()   
    okid_nearest.append(df_hyd_scen_sort['OKADER VakId'][idx])
    # check if nearest point is not in list
    exists = df_hyd_scen_sort['OKADER VakId'][idx] in okids_na
    print(exists)

#%%
# plt.close('all')

for direc in wdir_vals:
    
    selec1 = binning[(binning['wdir'] == direc)]
    selec2 = df_hyd_scen_sort[df_hyd_scen_sort['windrichting [graden N]'] == direc]
    
    fig = plt.figure()
    plt.scatter(selec2['h, teen [m+NAP]'],selec2['windsnelheid [m/s]'],10,'k')
    plt.scatter(X,Y,20,'k',marker='x')
    for ix, row in selec1.iterrows():
        plt.text(row['h_mean'],row['ws_mean'],'%d' % row['numel'],color='r',fontsize=10,fontweight='bold')
        plt.scatter(row['h_mean'],row['ws_mean'],20,'r')
    plt.xlabel('h, teen [m+NAP]')
    plt.ylabel('windsnelheid [m/s]')
    plt.xticks(ticks=h_bins)
    plt.yticks(ticks=ws_bins)
    plt.grid()
    plt.title('wdir = %d' % direc)
    
    if save_fig:
        namestr = scenario_sel[1:-1]
        name = 'binning_dir_%03d_%s.png' % (direc, namestr)
        fname = os.path.join(dirs['output'],name)
        save_plot_mod.save_plot(fig, fname, incl_wibo = False, dpi = 300, 
                  change_size = True, figwidth = 12, figheight = 8)

#%% extract data for certain directions

