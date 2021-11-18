"""
Manages the database connection to MongoDB

We handle this connection separately from the Flask app since it may be restarted
or not exist across parallel worker threads
"""

import flask
import pymongo
import logging

import db
import config


def get_db():
    """
    Retrieves the AppDB instance in use by the Flask server

    Returns:
     - An AppDB instance representing the server connection, or None if the connection failed failed
    """
    ctx = flask._app_ctx_stack.top
    try:
        app_db_client = getattr(ctx, "app_db_client", None)
        if app_db_client is None:
            ctx.app_db_client = pymongo.MongoClient(config.get("db_link", ""))
            ctx.app_db = db.AppDB(ctx.app_db_client)
        return ctx.app_db
    except:
        logging.getLogger("db").error("Error occurred setting up database connection", exc_info=True)
        ctx.app_db_client = None
        ctx.app_db = None
        return None

def db_teardown(error=None):
    """
    Closes the database connection when the app is torn down

    Parameters:
     - error: any error that caused the app to shut down
    """
    ctx = flask._app_ctx_stack.top
    app_db_client = getattr(ctx, "app_db_client", None)
    if app_db_client is not None:
        logging.getLogger("db").info("Closing the db connection")
        app_db_client.close()
        ctx.app_db_client = None
        ctx.app_db = None