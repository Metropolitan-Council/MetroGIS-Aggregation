# MetroGIS Upload
Upload Count datasets to be aggegated into MetroGIS Regional Datasets

## Requirements
Python 3.x\
ArcGIS Pro - "arcgis" Python module requires running on a client with ArcGIS Pro\
all other python modules are standard

## Instructions
### 1) Edit config.ini file
#### Set the following values in the default section
* logfile - your choice on the your local file system for where the log file should go
* user - username assigned from the Met Council
* loglevel - How verbose do you want the log file?

#### Add the location of zip file of each dataset to be uploaded under the section for that dataset
e.g.
~~~
[ADDRESSPOINTS]
uploadfile = C:\temp\addresspointdatazipfile.zip
~~~
### 2) Run once interactively
Run the python code with one parameter - *datastsetname*
e.g.
~~~
python.exe uploadscript.py ADDRESSPOINTS
~~~

The script will challenge for the password of the user identified in the user parameter of the config.ini (see step 1)
The script will store the username and password in the local system credential manager for future unattended/scheduled execution

### 3) Set up scheduled task
The script can be run Non-interactively