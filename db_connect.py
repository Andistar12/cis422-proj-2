# Handles connection to the database

import flask
import pymongo
import logging

import db
import config

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("db_connect_blueprint", __name__)

def get_db():
    """
    Retrieves the AppDB instance in use by the Flask server
    """
    try:
        if 'db' not in flask.g:
            client = pymongo.MongoClient(config.get("db_link", ""))
            flask.g.db = db.AppDB(client)
            for admin in config.get("admins", []):
                flask.g.db.add_admin(userid=None, user_name=admin)
            print("The DB is", flask.g.db)
        return flask.g.db
    except:
        logging.getLogger("db").error("Error occurred setting up database connection", exc_info=True)
        flask.g.db = None
        return None

# TODO add a teardown_appcontext to remove memory leak for db connection
