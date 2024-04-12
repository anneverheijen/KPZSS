# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 21:00:36 2022

@author: ENGT2
"""

import io
import os
import time
import sys
from tkinter import messagebox, Tk, Label, Button, Radiobutton, IntVar
import numpy as np
from hmtoolbox.WB_basic import list_files_folders

# results SWAN 1D
path_qsubs = r'z:\130991_Systeemanalyse_ZSS\3.Models\SWAN\1D\Waddenzee\02_productie\serie_02\iter_02'
qsub_files = list_files_folders.list_files('.qsub',path_qsubs)

newmachinename = 'triton'

for qsub_file in qsub_files:

    fname = qsub_file
    #adhere data and change 1 row
    with io.open(fname, 'r+', newline='\n') as file:
        data = file.readlines()
        
        for cnt, line in enumerate(data):
            if 'nodes' in line and 'galatea' in line and 'ppn=1' in line:
                #do some magic to create a new line
                newstring = data[cnt][:data[cnt].find('=')+1]+newmachinename+data[cnt][data[cnt].find(':'):]
                data[cnt] = newstring
                print('line changed')
                break
    
    with io.open(fname, 'w', newline='\n') as file:
        file.writelines(data)