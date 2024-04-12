# -*- coding: utf-8 -*-
"""
Created on Fri Sep 1 12:04:36 2022

This is a script to create a back-up of the hydra-nl werkmap and delete specified calculations (systems)

@author: BADD

The following steps are done:
1. Specify:
   1. Location of Hydra werkmap
   2. Toggles for zip and delete werkmap
   3. Specify names of zip and folders
2. If zip_toggle is yes:
   1. A zip is created of entire werkmap as a back-up
   2. If name zip already exists a KeyError is raised to prevent overwriting of earlier .zip
3. If delete_toggle is yes:
   1. All calculations are deleted of the specified systems
   2. Databases and shapes are not deleted

"""


# import modules
import os, shutil
from datetime import datetime  

# set variables and paths
hydra_werkmap = r'C:\MyPrograms\Hydra-NL_KP_ZSS\werkmap'
os.chdir(os.path.dirname(hydra_werkmap))

zip_toggle = 'Yes' # 'No' | do you want to zip existing werkmap
zip_description = 'HBN (WZ) productie' # description for in zipfile-name

delete_toggle = 'No' # 'No', do you want to delete all calculations within werkmap
delete_folders = ["Westerschelde", "Waddenzee", "Hollandse", "Europoort"] # list with System(s) of which you want to delete calculations

# zip files
if zip_toggle == 'Yes':
    print('zip_toggle is activated')
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    str_date_time = date_time.strftime("%d-%m-%Y") # _%Hh%Mm")

    if not os.path.exists(os.path.join(os.path.dirname(hydra_werkmap), f"backup_werkmap_{str_date_time}_{zip_description}.zip")):
        shutil.make_archive(f"backup_werkmap_{str_date_time}_{zip_description}", 'zip', hydra_werkmap)
        print('the werkmap is zipped')
    else: 
        creation_time_stamp = os.path.getctime(os.path.join(os.path.dirname(hydra_werkmap), f"backup_werkmap_{str_date_time}_{zip_description}.zip"))
        creation_date_time = datetime.fromtimestamp(creation_time_stamp)
        str_creation_date_time = creation_date_time.strftime("%d-%m-%Y, %H:%M:%S")
        raise KeyError(
            f"The zip named backup_werkmap_{str_date_time}_{zip_description}.zip already exists, change description, rename existing version or delete existing version. This version was created on {str_creation_date_time}"
            )
else:
    print('zip_toggle is turned off')

# delete files
if delete_toggle == 'Yes':
    print('delete_toggle is activated')
    for folder in os.listdir(hydra_werkmap):

        for substring in delete_folders:
            if substring in folder:
                folder_path = os.path.join(hydra_werkmap, folder)
                for map in os.listdir(folder_path):
                    if os.path.isdir(os.path.join(hydra_werkmap, folder, map)) and not 'Shapes' in map:
                        shutil.rmtree(os.path.join(hydra_werkmap, folder, map))
                        print(f'the calculations of {folder} at location {map} are deleted')
            else:
                print(f'no calculations within {substring} available, so nothing was deleted')
else:
    print('delete_toggle is turned off')
