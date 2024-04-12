# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 08:57:36 2022

@author: ENGT2
"""

# import

import os
import matplotlib.pyplot as plt 
from hmtoolbox import WB_basic 
from hmtoolbox import WB_SWAN 
from hmtoolbox.WB_basic import list_files_folders, save_plot
from hmtoolbox.WB_SWAN import SWAN_check_convergence

# settings

gebied = 'WZ'

path_main   = r'Z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\2D\Waddenzee\03_productiesommen\serie_01\G2'
dirs        = list_files_folders.list_folders(path_main, dir_incl=gebied, startswith = True, endswith = False)

# check convergence

save_fig = True

for diri in dirs:
    subdirs = list_files_folders.list_folders(diri, dir_incl='ID')
    for subdiri in subdirs:
        file = list_files_folders.list_files('.prt-001',subdiri,endswith=True)
        iteration_list, convergence_list = SWAN_check_convergence.check_swan_convergence(file[0])
        if max(convergence_list,default=0)<101:
            print('Max convergence = '+str(max(convergence_list,default=0))+ '%, plotted. \n'+file[0])
            fig = plt.figure()
            plt.plot(iteration_list,convergence_list)
            plt.text(2,convergence_list[-1],"max. convergence = %.2f%%" % convergence_list[-1])
            plt.xlabel('Iteration [nr.]')
            plt.ylabel('Convergence [%]')
            plt.title('SWAN convergence')
            if save_fig:
                savename = os.path.join(diri, 'figures', os.path.basename(os.path.normpath(subdiri) + '_convergence_prt-001.png'))
                save_plot.save_plot(fig, savename, incl_wibo = False, dpi = 300, 
                              change_size = False, figwidth = 8, figheight = 6)
                plt.close()
            else:
                print('Convergence > 101%, not plotted. \n'+file[0])

