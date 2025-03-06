# ---------------------------------------------------------------------------
# Name: uploadscript.py
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
import keyring
import getpass
import configparser
import logging

## Module Variables
# this is a pointer to the module object instance itself.
this = sys.modules[__name__]
this.uploadFilePath = None
this.portal = None
# open config file for other parameters
config = configparser.ConfigParser()
configPath = os.path.join (Path(__file__).parent, 'config.ini')
config.read(configPath)

# create logger object
logFile = config["DEFAULT"]['logfile']
logger = logging.getLogger("MetroGISDataPublish")
fh = logging.FileHandler(logFile)
ch = logging.StreamHandler()
def init(dataset):
    '''Run once per session to setup parameters for upload'''
    # Open log file
    logLevel = int(config[dataset]['loglevel'])
    logger.setLevel(logLevel)
    #fh.setLevel(logging.DEBUG)
    fh.setLevel(logLevel)
    
    ch.setLevel(20)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)


    #Look for key errors
    portalurl = config[dataset]['portalurl']
    this.uploadFilePath = config[dataset]['uploadfile']
    username = config[dataset]['User']

    # Log parameters
    logger.info("Dataset {}".format(dataset))
    logger.info("Uploading file: {}".format(this.uploadFilePath))
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
    try:
        this.portal = GIS(portalurl, username, pwd)
        return True
    except Exception as e:
        logger.info(e.args[0])
        p = getpass.getpass()
        try:
            this.portal = GIS(portalurl, username, p)
            pwd = keyring.set_password("MetroGISFileUpload", username, p)
            logger.info("new password saved in keyring")
            return True
        except Exception as e:
            logger.warning(e.args[0])
            return False
        


def validatedataset(dataset):
    ds = dataset.upper()
    '''make sure dataset is one of the MetroGIS Aggregated datesets'''
    validdslist = ["ADDRESSPOINTS", "PARCELS", "CENTERLINES", "PARKS"]
    if ds in validdslist:
        return ds
    else:
        print("dataset={}".format(dataset))
        print("first and only parameter must be one of ADDRESSPOINTS, PARCELS, CENTERLINES, PARKS")
        exit()

#### Begin Upload to Met Council ArcGIS Portal ####
def uploaddataset(dataset):
    '''Upload Dataset to Portal'''
    dataset = validatedataset(dataset)
    if init(dataset):
        uploadFilePath = this.uploadFilePath
        portal = this.portal
        # Set up metadata for item
        title = config[dataset]['title']
        county = config["DEFAULT"]['county']
        tags = "MetroGIS, {}, {}, {}, {} County".format(dataset, title, county, county)
        snippet = "MetroGIS {} Upload for {} County".format(title, county)
        description = "This zipped file geodatabase contains {} for {} County as part of the MetroGIS aggregation and validation initiative facilitated by the Metropolitan Council. The Portal Item will be downloaded through nightly automations and validation errors sent to corresponding county if needed.".format(title, county)
        item_properties = {"type": "File Geodatabase",
                           "title": title,
                           "tags": tags,
                           "snippet": snippet,
                           "description": description,
                           "commentsEnabled": False
                           }
        logger.debug(item_properties)

        path = Path(uploadFilePath)
        if path.is_file():
            try:
                # Check if item already exists
                itemid = config[dataset].get('itemid', None)
                if itemid:
                    # Update existing item
                    updateitem = portal.content.get(itemid)
                    updateitem.update(item_properties, data=uploadFilePath)
                    rslt = updateitem
                    logger.info("{} has been updated in Portal.".format(title))
                else:
                    # Add new item
                    root_folder = portal.content.get('root')
                    if root_folder:
                        rslt = root_folder.add(item_properties, data=uploadFilePath)
                        config[dataset]['itemid'] = rslt.id
                        with open(configPath, 'w') as configfile:
                            config.write(configfile)
                        logger.debug("added itemid to config file under {}".format(dataset))
                        logger.info("Uploaded item: {}".format(rslt.homepage))
                    else:
                        logger.error("Could not retrieve the root folder.")
                        rslt = None
            except Exception as e:
                logger.info("Could not overwrite {} with just name".format(dataset))
                logger.debug("{}".format(e))
                rslt = None
        else:
            if uploadFilePath == '':
                logger.warning("uploadFilePath: {} is empty".format(uploadFilePath))
            else:
                logger.warning("uploadFilePath: {} does not point to a file".format(uploadFilePath))
            rslt = None

        if rslt:
            # Log full response
            logger.debug("new itemid: {}".format(rslt.id))
            config[dataset]['itemid'] = rslt.id
            with open(configPath, 'w') as configfile:
                config.write(configfile)
            logger.debug("added itemid to config file under {}".format(dataset))
            logger.info("Uploaded item: {}".format(rslt.homepage))
        else:
            # Try getting item with id and updating item
            try:
                itemid = config[dataset]['itemid']
                updateitem = portal.content.get(itemid)
                updateitem.update(item_properties, data=uploadFilePath)
                logger.info("{} has been updated in Portal.".format(title))
            except KeyError:
                logger.critical("No Item ID in config file. {} upload unsuccessful!".format(dataset))
            except Exception as e:
                logger.critical("{} upload unsuccessful!".format(dataset))
                logger.warning("{}".format(e))
    else:
        logger.critical("Could not log into Met Council Portal\n")
    #### END UPLOAD TO Met Council ArcGIS PORTAL ####

    # Close log and exit
    logger.info("-----------------Script completed----------------------------------\n")
    logger.removeHandler(fh)
    logger.removeHandler(ch)

    #report.close()

def main(dataset):
    uploaddataset(dataset)

if __name__ == "__main__":
    # Get Dataset Parameter
    # ADDRESSPOINTS, PARCELS, CENTERLINES
    try:
        ds = sys.argv[1].upper()
        dataset = validatedataset(ds)
    except KeyError:
        dataset = "DEFAULT"
    main(dataset)
