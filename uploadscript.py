# ---------------------------------------------------------------------------
# Name: uploadscript.py
# Created: 2015-10-20
# Updated: 2018-5-15
# Updated Again: 2021-10-29
# ---------------------------------------------------------------------------

# Import modules
import sys
import os
from pathlib import Path
import time
import requests
import json
from arcgis.gis import GIS
from arcgis.gis import Item
#from urllib3.exceptions import InsecureRequestWarning #added
import keyring
import getpass
import configparser
import logging

#Get Dataset Parameter
#ADDRESSPOINTS, PARCELS, CENTERLINES
try:
    dataset = sys.argv[1].upper()
except KeyError:
    dataset = "DEFAULT"
if dataset == "ADDRESSPOINTS":
    pass
elif dataset == "PARCELS":
    pass
elif dataset == "CENTERLINES":
    pass
elif dataset =="PARKS":
    pass
else:
    print("dataset={}".format(dataset))
    print("first and only parameter must be one of ADDRESSPOINTS, PARCELS, CENTERLINES, PARKS")
    exit()

# open config file for other parameters
config = configparser.ConfigParser()
config.read('config.ini')

# Open log file
logFile = config[dataset]['logfile']
logLevel = int(config[dataset]['loglevel'])
logger = logging.getLogger("MetroGISDataPublish")
logger.setLevel(logLevel)
fh = logging.FileHandler(logFile)
#fh.setLevel(logging.DEBUG)
fh.setLevel(logLevel)
ch = logging.StreamHandler()
ch.setLevel(20)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

#Look for key errors
portalurl = config[dataset]['portalurl']
uploadFilePath = config[dataset]['uploadfile']
username = config[dataset]['User']

timestamp = time.strftime("%c")
# Log parameters
logger.info("Dataset {}".format(dataset))
logger.info("Uploading file: {}".format(uploadFilePath))
logger.info("Uploading to: {}".format(portalurl))
logger.info("User: {}".format(username))

# Set local variables
### ArcGIS Portal Upload Variables ###
logger.debug("{}".format(sys.executable))
logger.debug("{}".format(sys.version))
### Username and password
pwd = keyring.get_password("MetroGISFileUpload", username)
if not pwd:
    logger.info("password not set yet")
    p = getpass.getpass()
    pwd = keyring.set_password("MetroGISFileUpload", username, p)
    logger.info("password saved in keyring")
    
portal = GIS(portalurl, username, pwd)
me = portal.users.me

#Check if uploadFilePath exists

#### Begin Upload to Met Council ArcGIS Portal ####
title = "{}".format(dataset)
tags = "metrogis, {}, test, delete".format(dataset)
item_properties = {"type": "File Geodatabase",
                    "title": title,
                    "tags":tags,
                    "snippet":"testing upload of zipped file gdb",
                    "description":"Started with a small file geodatabase. This is a large sized zip file. Eventually testing a large upload and automating it.",
                  "commentsEnabled" : False,
                  "overwrite":True
                  }
logger.debug("Overwrite Property={}".format(item_properties["overwrite"]))
path = Path(uploadFilePath)
if path.is_file():
    try:
        rslt = portal.content.add(item_properties, data=uploadFilePath)
        
    except Exception as e:
        logger.info("{} Upload {} failed".format(dataset, uploadFilePath))
        logger.info("{}".format(e))
        #If error code 409. Need to get item and update
        #update(file, folder_name=None, file_name=None, text=None)
        #rslt = portal.content.update(item_properties, data=uploadFilePath)
        rslt=None
else:
    logger.warning("{} does not point to a file".format(uploadFilePath))
    rslt = None
if rslt:
    # Log full response
    logger.debug("new itemid: {}".format(rslt.id))
    config[dataset]['itemid']=rslt.id
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    logger.debug("added itemid to config file under {}".format(dataset))
    logger.info("Uploaded item: {}".format(rslt.homepage))
else:
    #try getting item with id and updating item https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.update
    try:
        itemid = config[dataset]['itemid']
        updateitem = portal.content.get(itemid)
        updateitem.update(data=uploadFilePath)
    except KeyError:
        logger.critical("{} upload unsuccessful!".format(dataset))

#### END UPLOAD TO Met Council ArcGIS PORTAL ####
# Close log and exit
logger.info("-----------------Script completed----------------------------------\n")
#report.close()
sys.exit()



