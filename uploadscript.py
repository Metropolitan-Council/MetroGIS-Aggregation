# ---------------------------------------------------------------------------
# Name: ap_upload.py
# Created: 2015-10-20
# Updated: 2018-5-15
# Updated Again: 2021-10-28
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
#import urllib3


#Get Parameters
county = sys.argv[1]
if county == "#":
    county = "Hennepin"
dataset = sys.argv[2]
if dataset == "#":
    dataset = "AddressPoints"
wd = sys.argv[3]
# Set working directory for Use in Tool
workingDirectory = os.path.dirname(os.path.realpath(sys.argv[3]))
if wd == "#":
    #----Set working directory when incorporating in script or running from Python-----#
    workingDirectory = "K:\\data_devel\\{}\\1_Data_Collection\\{}-county".format(dataset,county)
else:
    workingDirectory = os.path.dirname(os.path.realpath(wd))
    
# Open log file
logFile = workingDirectory + "\\upload.log"
report = open(logFile,'w')


# Get timestamp
timestamp = time.strftime("%c")
report.write("Running script at " + timestamp + "\n")
report.write("{}, {}\n".format(county, dataset))


# Set local variables
### ArcGIS Portal Upload Variables ###
portalurl = "https://arcgis.metc.state.mn.us/portal"
report.write("{}\n".format(sys.executable))
report.write("{}\n".format(sys.version))
### Username and password
username = "testtemp"
pwd = keyring.get_password("MetroGISFileUpload", username)
if not pwd:
    report.write("password not set yet")
    p = getpass.getpass()
    pwd = keyring.set_password("MetroGISFileUpload", username, p)

portal = GIS(portalurl, username, pwd)
me = portal.users.me

### UPLOAD VARIABLES ###
if dataset == "AddressPoints":
    uploadFilePath = workingDirectory + "\\adp.zip" # Path to local file that will be uploaded to update existing resource
elif dataset == "parcels":
    uploadFilePath = workingDirectory + "\\parcel.zip" # Path to local file that will be uploaded to update existing resource
#Check if uploadFilePath exists

#### Begin Upload to Met Council ArcGIS Portal ####
title = "{} County {}".format(county, dataset)
tags = "metrogis, {}, {}, test, delete"
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
