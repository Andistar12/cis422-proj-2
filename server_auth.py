# Handles user authentication and account creation

import os
import secrets
import datetime
import flask_login
import hashlib
import flask

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("auth_blueprint", __name__)

# The Flask login manager
login_manager = flask_login.LoginManager()

def is_admin():
    """
    Returns whether the user is an administrator
    """
    return False # TODO

def is_authenticated():
    """
    Return whether the user is logged in
    """
    return False  # TODO

@login_manager.user_loader
def user_loader(username):
    """
    Loads the user if it exists
    """
    pass # TODO 

# Page endpoints

class User(flask_login.UserMixin):
    """
    The user class object for session/auth purposes
    """
    
    def __init__(self):
        pass # TODO

    def get_id(self):
        return str(self.id)

@blueprint.route("/register", methods=["GET", "POST"])
def register():
    """
    GET: Returns the register account page register.html
    POST: Attempts to register the account and redirects to the login page login.html
    """
    pass # TODO

@blueprint.route("/login.html", methods=["GET", "POST"])
def login():
    """
    GET: Returns the login page login.html
    POST: Attempts to log in the user and redirects to my boards myboards.html
    """
    pass # TODO

@blueprint.route("/logout")
def logout():
    """
    Logs out the user and redirects to the home page home.html 
    """
    pass # TODO
