# MetroGIS Upload
Upload County datasets to be aggegated into MetroGIS Regional Datasets

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
Run the python code with one parameter - *datastsetname* \
As mentioned above, the script requires a Python module installed with ArcGIS Pro. On a windows machine with a standard ArcGIS Pro installation, one way to run the script would be from the "Python Command Prompt" found in the Windows Start Menu under the ArcGIS Folder.\ 
Assuming you saved the code and config file in c:\scripts\MetroGIS, it would look something like this:\
~~~
(arcgispro-py3) C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3>python.exe C:\scripts\MetroGIS\uploadscript.py ADDRESSPOINTS
~~~

The script will challenge for the password of the user identified in the user parameter of the config.ini (see step 1)\
The script will use the local system credential manager for future unattended/scheduled execution.\
When Portal password changes, remember to either change the password in the credential manager, or remove the entry entirely and run interactively.

### 3) Set up scheduled task
The script can now be run non-interactively/automated
