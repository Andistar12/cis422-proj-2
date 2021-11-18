"""
Manages configuration (from file) for the entire project

We handle config separately from the Flask app since it may be restarted
or not exist across parallel worker threads
"""

import json
import sys
import os
import logging

# The config JSON
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

    Parameters:
     - key: the config key to look for
     - default: what to return if the key is not found
    Returns:
     - The value associated with the key
    """
    if config is None:
        # Read in the config
        init_config()
    return config.get(key, default)