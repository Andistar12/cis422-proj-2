import json
import sys
import os
import logging

config = None

def init_config():
    """
    Initiates the configuration file
    """
    global config

    # Determine the appropriate config file location
    cfgloc = ""
    try:
        cfgloc = os.environ["CONFIG_LOC"]
    except KeyError:
        # config file location can be specified via command line argument
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            cfgloc = sys.argv[1]

    # Read files from config
    try:
        with open(cfgloc) as cfgfile:
            config = json.load(cfgfile)
    except:
        logging.getLogger("server").error("Error occurred opening config file", exc_info=True)
        config = {}

def get(key, default):
    """
    Gets a parameter key from the configuration file, falling back to default if it does not exist
    """
    if config is None:
        init_config()
    return config.get(key, default)