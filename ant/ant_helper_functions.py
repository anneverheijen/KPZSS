# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 12:07:07 2022

@author: VERA7
"""
# import modules
import os
import numpy as np
import antconnect
from dotenv import load_dotenv

# %%All config vars and secrets should be put into environmental vars
# if they are present, set skipping it

dirname_of_this_file = os.path.dirname(__file__)

def get_api_connection(ant_platform='LIVE', env_file=None):
    """
    returns connected api class
    
    Args:
        None
    Kwargs:
        ant_platform - platform for which credentials are required
            default = 'BETA'
            can be ALPHA, BETA and LIVE
        env_file - location of env file None is default, then 'ant_key.evn'
            in this directory is used
    Returns:
        ant - connected antconnect api class
    """

    # load environment variables
    if env_file is None:
        env_file = os.path.join(dirname_of_this_file, 'ant_key.env')
    load_dotenv(env_file)

    # Extract them, and use as globals
    clientID = os.environ[f'{ant_platform}_CLIENT_ID']
    host = os.environ[f'{ant_platform}_HOST']
    clientSecret = os.environ[f'{ant_platform}_CLIENT_SECRET']
    username = os.environ[f'{ant_platform}_USERNAME']
    password = os.environ[f'{ant_platform}_PASSWORD']
    
    # connect to ant
    ant = antconnect.API(host)
    ant.login(clientID, clientSecret, username, password)
    
    ant.ant_platform = ant_platform
    ant.env_file = os.path.abspath(env_file)
    
    return ant

def get_project_id(ant, project_name):
    """gets project id by name"""
    #read all projects
    projects = ant.projects_read()
    
    #loop and find right name
    for project in projects:
        if project['name'] == project_name:
            #if right name found, store id and break
            project_id = project['id']
            return project_id
    raise UserWarning('project "{project_name}" not found')

def get_table_id(ant, project_id, tableName):
    """gets table id by name"""
    tables = ant.tables_read(project_id)
    for table in tables:
        if table['name'] == tableName:
            tableID = table['id']
            return tableID
    raise UserWarning('table "{tableName}" not found')

def find_ids_or_records(records, cols_to_search, items_to_find, return_records=False):
    """
    returns the id or record of the first entry that matches items_to_find in cols_to_find
    
    if return_record=True, it returns the id and records, otherwise the ids only
    
    For example:
        cols_to_search = ['Naam', 'Methode']
        items_to_find  = ['Waddenzee', 'IPM']
        
        records = [{'id': 'df2985bd-7aa4-4bf6-b745-a50054e7e5ce',
                     'Naam': 'Waddenzee',
                     'Methode': 'IPM'},
                    {'id': 'b228477c-c82b-459f-af89-407ff71f9a72',
                     'Naam': 'Westerschelde',
                     'Methode': 'IPM'},
                    {'id': 'fc04022d-896b-41a5-b305-e70c8a1cd547',
                     'Naam': 'Waddenzee',
                     'Methode': 'Database'},
                    {'id': '10958d59-f3dd-45f8-98c8-cce9c4a3dd2a',
                     'Naam': 'Hollandse IJssel',
                     'Methode': 'Database'},
                    {'id': '5d4bb442-1934-4258-b6cd-8eb226a8c627',
                     'Naam': 'Oosterschelde',
                     'Methode': 'Database'}]
        
        This will return:
            'df2985bd-7aa4-4bf6-b745-a50054e7e5ce'
        
    """
    if np.size(cols_to_search) is not np.size(items_to_find):
        raise UserWarning('cols_to_search and items_to_find do not have equal length, if you require more items per column consider looping in main script')
    # define empty lists to store found ids and records
    id_list = []
    record_list = []
    # loop over all records
    for record in records:
        # check if all cols match
        if np.all([record[col]==item_to_find for col, item_to_find in zip(cols_to_search, items_to_find)]):
            found_id = record['id']
            # append to id_list and record_list
            id_list.append(found_id)
            record_list.append(record)
                        
    if not return_records:
        return id_list
    else:
        return id_list, record_list
    
    raise UserWarning('Did not find the right record')
    
def find_task(ant_connection, project_id, signed_in_user_uuid, session_name,
             task_name):
    """
    finds open task that is assigned to user with uuid 'signed_in_user_uuid'
    This task should be part of session with name 'session_name' and have the name
    'task_name'

    Parameters
    ----------
    ant_connection : initiated antconnect class
    project_id : str, uuid of project
    signed_in_user_uuid : str, uuid of user
    session_name : str, name of the session that task belongs to
    task_name : str, name of task to find

    Raises
    ------
    UserWarning
        When no matching task is found


    Returns
    -------
    task_dict : dict with task data (one of the responses of ant_connection.tasks_read)
    job : dict with job data (response from ant_connection.task_getJob)

    """
    # get first open task
    runs = ant_connection.tasks_read(project_id=project_id, status='open',
                                     user=signed_in_user_uuid)

    found_job = False
    session_names = []
    task_names = []
    for task_dict in runs:
        # get job
        job = ant_connection.task_getJob(project_id, task_dict['id']) 
        
        # check if this is the one we want
        if not isinstance(job, bool):
            session_names.append(job['session_object']['name'])
            task_names.append(job['task']['name'])
            if job['session_object']['name'] == session_name and job['task']['name'] == f'{task_name} Task':    
                print("=== \nFound job\n===")
                found_job = True
                break
    if not found_job:
        raise UserWarning(f'Did not find the right task ("{task_name}") in session "{session_name}". '
                          'Did you assign the job to yourself?\n'
                          f'I found the following session names: {session_names}\n'
                          f'I found the following task names: {task_names}')

    return task_dict, job

def find_session(ant_connection, project_id, session_name):
    """
    finds the right session, belonging to session_name
    
    Parameters
    ----------
    ant_connection : initiated antconnect class
    project_id : str, uuid of project
    session_name : str, name of the session that task belongs to

    Raises
    ------
    UserWarning
        When no matching task is found


    Returns
    -------
    session : dict with session data (one of the responses of ant_connection.project_sessions)

    """
    sessions = ant_connection.project_sessions(project_id, None)
    
    session_name_bools = [session_name == session['name'] for session in sessions]
    
    if sum(session_name_bools) == 1:
        session = np.array(sessions)[session_name_bools][0]
        print(f'Found session "{session["name"]}"')
    elif sum(session_name_bools) == 0:
        raise UserWarning(f'Found no session with name {session_name}. Only found "{[session["name"] for session in sessions]}"')
    else:
        raise UserWarning('Found more than one session. This should not be possible')
        
    return session