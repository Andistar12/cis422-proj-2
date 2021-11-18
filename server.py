# The main Flask app web server

import logging # Used for logging
import flask # Used as the backend and for webpage rendering

# Imports from our own modules
import db_connect
import server_webpages
import server_auth
import server_api
import server_notifs
import config

# Global variables
app = flask.Flask(__name__)
app.secret_key = config.get("secret_key", "super secret")
app.debug = config.get("debug", True)

# Hook into Gunicorn logger (for production only)
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)

# Load blueprints to create server endpoints
app.register_blueprint(server_webpages.blueprint)
app.register_blueprint(server_auth.blueprint)
app.register_blueprint(server_api.blueprint)
app.register_blueprint(server_notifs.blueprint)

# Register the teardown context for the database
app.teardown_appcontext(db_connect.db_teardown)

if __name__ == "__main__":
    # Run app
    port = config.get('port', 5000)
    print(f"Launching flask app on port {port}")
    app.run(port=port, host="0.0.0.0", debug=app.debug)
