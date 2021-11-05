# ---------------------------------------------------------------------------
# Name: uploadscript.py
# Created: 2015-10-20
# Updated: 2018-5-15
# Updated Again: 2021-10-29
# ---------------------------------------------------------------------------

# Import modules
import sys
import os
import time
import requests
import json
from arcgis.gis import GIS
from arcgis.gis import Item
#from urllib3.exceptions import InsecureRequestWarning #added
import keyring
import getpass
import configparser

#Get Dataset Parameter
#ADDRESSPOINTS, PARCELS, CENTERLINES
try:
    dataset = sys.argv[1]
except KeyError:
    dataset = "DEFAULT"
if dataset == "ADDRESSPOINTS":
    pass
elif dataset == "PARCELS":
    pass
elif dataset == "CENTERLINES":
    pass
else:
    print("dataset={}".format(dataset))
    print("first and only parameter must be one of ADDRESSPOINTS, PARCELS, CENTERLINES")
    exit()

# open config file for other parameters
config = configparser.ConfigParser()
config.read('config.ini')
# Open log file
logFile = config[dataset]['logfile']
report = open(logFile,'w')
#Look for key errors
portalurl = config[dataset]['portalurl']
uploadFilePath = config[dataset]['uploadfile']
username = config[dataset]['User']

timestamp = time.strftime("%c")
report.write("Running script at " + timestamp + "\n")
# Log parameters
report.write("Dataset {}\n".format(dataset))
report.write("Uploading: {}\n".format(uploadFilePath))
report.write("Uploading to: {}\n".format(portalurl))
report.write("User: {}\n".format(username))

# Set local variables
### ArcGIS Portal Upload Variables ###
report.write("{}\n".format(sys.executable))
report.write("{}\n".format(sys.version))
### Username and password
pwd = keyring.get_password("MetroGISFileUpload", username)
if not pwd:
    report.write("password not set yet")
    p = getpass.getpass()
    pwd = keyring.set_password("MetroGISFileUpload", username, p)

portal = GIS(portalurl, username, pwd)
me = portal.users.me

#Check if uploadFilePath exists

#### Begin Upload to Met Council ArcGIS Portal ####
title = "County {}".format(dataset)
tags = "metrogis, {}, {}, test, delete".format(dataset)
item_properties = {"type": "File Geodatabase",
                    "title": title,
                    "tags":tags,
                    "snippet":"testing upload of zipped file gdb",
                    "description":"Started with a small file geodatabase. This is a large sized zip file. Eventually testing a large upload and automating it.",
                  "commentsEnabled" : False,
                  "overwrite":True
                  }

rslt = portal.content.add(item_properties, data=uploadFilePath)
if rslt:
    # Log full response
    report.write("Uploaded item: {}\n".format(rslt.homepage))
else:
    report.write("Upload unsuccessful\n")

#### END UPLOAD TO MRCC PORTAL ####
# Close log and exit
report.write("\n" + "Script completed\n----------------------------------")
report.close()
sys.exit()



