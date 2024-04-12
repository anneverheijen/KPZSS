# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 15:44:00 2022

@author: ENGT2
"""

import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from hmtoolbox.WB_SWAN import SWAN_quickplot
from hmtoolbox.WB_basic import list_files_folders
from hmtoolbox.WB_basic import save_plot
import datetime
import gc

gebied = 'WS'

path_main = r'd:\Users\ENGT2\Documents\Projects\130991 - SA Waterveiligheid ZSS\TEMP'

dirs = list_files_folders.list_folders(path_main, dir_incl=gebied, startswith = True, endswith = False)

params  = ['Hsig','RTpeak','Depth']
labels  = ['Hsig (m)','Tp (s)', 'Water depth (m)']

for diri in dirs:
    subdirs = list_files_folders.list_folders(diri, dir_incl='ID')
    for subdiri in subdirs:
        print('Start at {} doing stuff'.format(datetime.datetime.now()))
        files = list_files_folders.list_files('.mat',subdiri, startswith = False, endswith = False, recursive = True)
        file = files[0]
        subdir = os.path.basename(os.path.normpath(subdiri))
        title = subdir 
        fig = SWAN_quickplot.SWAN_quickplot_2D(file, parameters=params, parameters_clabel=labels, name=title,
                          coord_unit='m', cmap='jet', quivers = False, contours = False, vec_thinning=50, 
                          wat_lev=0, vmin=False, vmax=False, sf=False, figsize = (8,12), rows=3, columns=1)
        
        save_name = os.path.join(diri, 'figures', os.path.basename(os.path.normpath(subdiri) + '_results.png'))
        save_plot.save_plot(fig, save_name, incl_wibo = False, dpi = 300, 
                      change_size = True, figwidth = 8, figheight = 10)
        plt.close('all')
        del fig
        print('End at {} doing stuff'.format(datetime.datetime.now()))
        gc.collect()