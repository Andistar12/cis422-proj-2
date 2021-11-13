# The main Flask app web server

import os # Used to fetch environment vars for parameters
import sys # Used to access command-line parameters
import json # Used for config loading
import logging # Used for logging
import flask # Used as the backend and for webpage rendering
import pymongo # Used for MongoDB bindings

# Imports from our own modules
import server_webpages
import server_auth
import server_api
import db

# Global variables

app = flask.Flask(__name__)

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

# Fetch config parameters
app.port = config.get("port", 5000)
app.secret_key = config.get("secret_key", "super secret")
app.debug = config.get("debug", True)
app.db_link = config.get("db_link", "")
app.admins = config.get("admins", [])

# Hook into Gunicorn logger
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)

# Load blueprints to create server endpoints
app.register_blueprint(server_webpages.blueprint)
app.register_blueprint(server_auth.blueprint)
app.register_blueprint(server_api.blueprint)

# Inits the MongoDB connection
try:
    client = pymongo.MongoClient(app.db_link)
    app.db = db.AppDB(client)
    for admin in app.admins:
        app.db.add_admin(admin)
except:
    logging.getLogger("")
    logging.getLogger("server").error("Error occurred setting up database connection", exc_info=True)
    app.db = None

if __name__ == "__main__":
    # Run app
    print(f"Launching flask app on port {app.port}")
    app.run(port=app.port, host="0.0.0.0", debug=app.debug)
