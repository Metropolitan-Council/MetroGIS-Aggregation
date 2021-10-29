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
dataset = sys.argv[2]
#----Set working directory when incorporating in script or running from Python-----#
workingDirectory = "K:\\data_devel\\AddressPoints\\1_Data_Collection\\anoka-county"
workingDirectory = "K:\\data_devel\\parcels\\1_Data_Collection\\hennepin-county"

# Set working directory for Use in Tool
#workingDirectory = os.path.dirname(os.path.realpath(sys.argv[0]))

# Open log file
logFile = workingDirectory + "\\upload.log"
report = open(logFile,'w')


# Get timestamp
timestamp = time.strftime("%c")
#report.write("Running script at " + timestamp + "\n")


# Set local variables
### ArcGIS Portal Upload Variables ###
portalurl = "https://arcgis.metc.state.mn.us/portal"
report.write(sys.executable)
report.write(sys.version)
### Username and password
username = "testtemp"
pwd = keyring.get_password("MetroGISFileUpload", username)
if not pwd:
    report.write("password not set yet")
    p = getpass.getpass()
    pwd = keyring.set_password("MetroGISFileUpload", username, p)
else:
    print("Password!")
portal = GIS(portalurl, username, pwd)
me = portal.users.me

### UPLOAD VARIABLES ###
uploadFilePath = workingDirectory + "\\adp.zip" # Path to local file that will be uploaded to update existing resource
uploadFilePath = workingDirectory + "\\parcel.zip" # Path to local file that will be uploaded to update existing resource

#### Begin Upload to Met Council ArcGIS Portal ####
item_properties = {"type": "File Geodatabase",
                    "title": "Hennepin County Parcels",
                    "tags":"metrogis,test,delete",
                    "snippet":"testing upload of zipped file gdb",
                    "description":"Started with a small file geodatabase. This is a large sized zip file. Eventually testing a large upload and automating it.",
                  "commentsEnabled" : False,
                  "overwrite":True
                  }

rslt = portal.content.add(item_properties, data=uploadFilePath)
if rslt:
    # Log full response
    report.write("Uploaded item{}".format(rslt.homepage))
else:
    report.write("Upload unsuccessful")




#### END UPLOAD TO MRCC PORTAL ####
# Close log and exit
report.write("\n" + "Script completed")
report.close()
sys.exit()
