# How to use ANT

This readme covers the basics about reading and writing form ANT that are important for this project. A more elaborate documentation about `antconnect` (the module we use) is given at [their documentation page](https://docs.antcde.io/ANTConnect/python/#verwijder-een-tabel)

## Make connection

### First time connection
For first time use you need to create a file called "ant_key.env" in the folder "ant". **Don't commit this file. It contains your credentials**. This file should contain the following lines:

```
LIVE_HOST=https://api.antcde.io/
LIVE_USERNAME=<your username>
LIVE_PASSWORD=<your password>
LIVE_CLIENT_ID=<see below>
LIVE_CLIENT_SECRET=<see below>
```

You can create a token in ANT and fill in the cliend id and secret that belong to this token. 
The token can be made by clicking on your username a the bottom right and go to "profile settings".
The pane that opens contains the snippet below. Press new token to make one and copy the client id and client secret into the "ant_key.env"
![image](https://user-images.githubusercontent.com/68229914/181701896-8816896f-dd00-4c3e-a2dd-43320a9db912.png)

### Make API connection

If you have the "ant_key.env" in the "ant" folder and you installed the requirements (i.e. antconnect), you can make an api connection with ant with the following lines of code

```python
# import ant functions
from ant import ant_helper_functions as ant_funcs

# make api connection
ant_connection = ant_funcs.get_api_connection()

```

This connection will be used later on to read tables and upload to them, but also to work with sessions

## Read table 

You can read items from a table after making API connection (see above) with the following code:

```python

# specify what to read
project_name = 'Systeemanalyse Waterveiligheid'
table_name = 'Calc_output'

# get the project and table id
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)

ant_connection.records_read(project_id, table_id)

```

## Upload to table

Upload to a table can be done with and without linking to a session. This example shows how to upload without a session. You need to make an API connection first, see above.

```python
# specify where to put it
project_name = 'Systeemanalyse Waterveiligheid'
table_name = 'Calc_output'

# get the project and table id
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
table_id = ant_funcs.get_table_id(ant_connection, project_id, table_name)

# make example file
example_file = 'test.txt'
with open(example_file, 'w') as file:
    file.write('testing')

# create a dict with a result. columns should have name of columns in output table
result_dict = {'Name' : 'vanuit python',
               'Number' : 10,
               'Correct' : True,
               'Use in next step' : True,
               'remarks' : None,
               'output_file' : ant_connection.parse_document(example_file)}
ant_connection.record_create(project_id, table_id, result_dict)

```
## Update records in a table

You can update specific fields of a record with `records.update`. Note you need to supply the changing fields only, see example below.

```python
# import own modules
from ant import ant_helper_functions as ant_funcs

# %% set some variables
project_name = 'Systeemanalyse Waterveiligheid'
output_table = 'Calc_output'

# make api connection
ant_connection = ant_funcs.get_api_connection()

# get ids required to do the analysis
project_id = ant_funcs.get_project_id(ant_connection, project_name=project_name)
table_id = ant_funcs.get_table_id(ant_connection, project_id, output_table)


# read records and find one to update
records = ant_connection.records_read(project_id, table_id)

found_ids, found_records = ant_funcs.find_ids_or_records(records, ['Number'], [11], return_records=True)

for found_record in found_records:
    # set new number
    newdict = {'Number' : found_record['Number'] + 1} 
    
    ant_connection.record_update(project_id, table_id, found_record['id'], 
                                 newdict)
```

## Working with sessions

You can upload session data to a table and read session data from a table. Both princples are discuces below. 

### Upload
The following steps are required to upload data to a session ([demo in this file](https://github.com/witteveenbos/KPZSS/blob/main/example/demo_upload.py)):
1. Specify:
   1. Which session you are working on (name);
   2. Which task (block) you are working on (name);
   3. which table you want to put your results in at top of the script;
2. Get the task in the session;
3. Set it on processing (just because we can);
4. Upload the data
5. Close the task. 

### Read data while doing a task

If you found the right task in the steps for uploading data, you can use the session id in `job['session']` to read data from a table. For instance with:
`records = ant_connection.records_read(project_id, table_id, session=job['session'])`

### Read without doing a task

The following steps are required to read session data without doing a task ([demo in this file](https://github.com/witteveenbos/KPZSS/blob/main/example/demo_read_session_data.py)):
1. Specify:
   1. Which session you are working on (name);
   2. which table you want to read data from;
2. Get the session id
3. read the data

## Used datamodel

![image](https://user-images.githubusercontent.com/68229914/183667963-a00443c5-c309-4e59-aa1e-8a1a46de903c.png)
