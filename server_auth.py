# Handles user authentication and account creation

import flask_login
import flask

from flask import render_template, request, session, redirect, url_for, flash

from passlib.hash import sha256_crypt as pwd_context

from flask_login import login_required, logout_user, UserMixin, fresh_login_required, login_user
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators

import db_connect
import config
   
class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
        message=u"A little too short or long for a username."),
        validators.InputRequired(u"Input is required.")])
    password = StringField('Password', [
        validators.Length(min=2, max=25,
        message=u"Huh, little too short for a password."),
        validators.InputRequired(u"Forget something?")])    
    remember = BooleanField('Remember me')    

class RegisterForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
        message=u"A little too short or long for a username."),
        validators.InputRequired(u"Input is required.")])
    password = StringField('Password', [
        validators.Length(min=2, max=25,
        message=u"Huh, little too short for a password."),
        validators.InputRequired(u"Forget something?")])   

def get_salt(base_string: str):
    return base_string.replace(" ", "").zfill(16)

def hash_password(password):
    return pwd_context.hash(password, salt=get_salt(config.get("secret_key", "super secret")))

def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)


# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("auth_blueprint", __name__)

# The Flask login manager
@blueprint.record_once
def on_load(state):
    login_manager.init_app(state.app)

class UserObject(UserMixin):
    def __init__(self, username: str):
        self.username = username

    def get_id(self):
        return str(self.username)

login_manager = flask_login.LoginManager()

def is_admin():
    """
    Returns whether the user is an administrator
    """
    # Check if they are even logged in first
    if not is_authenticated():
        return False

    # get the list of current admins
    admins = db_connect.get_db().fetch_admins()
    for admin in admins:
        if flask_login.current_user.get_id() == admin["username"]:
            return True
    return False

def is_authenticated():
    """
    Return whether the user is logged in
    """
    return flask_login.current_user.is_authenticated

def get_curr_username():
    """
    Fetches the username of the current user. Assumes they are already authenticated
    """
    return flask_login.current_user.get_id()

@login_manager.user_loader
def user_loader(username):
    """
    Loads the user if they are logged in. This is only used internally by Flask-Login
    """
    return UserObject(username)


@blueprint.route("/register.html", methods=["GET", "POST"])
def register():
    """
    GET: Returns the register account page register.html
    POST: Attempts to register the account and redirects to the login page login.html
    """
    form = RegisterForm()
    #handling the POST requests
    if request.method == "POST": 
        if form.validate_on_submit() and "username" in request.form and "password" in request.form:
            username = request.form["username"]
            password = request.form["password"]

            #search for a user with the provided user name
            user = db_connect.get_db().fetch_user(userid=None, user_name = username)
            #if the user isnt found, hash the password and register the new user      
            if user.get('username') is None:
                hashed_pass = hash_password(password)
                new_id = db_connect.get_db().add_user(user_name = request.form["username"], password = hashed_pass)
                session['username'] = request.form['username']
                return redirect(url_for('auth_blueprint.login')) # Redirect wants function name, not endpoint
            else:
                return 'A user with that username already exists, please try another username.'   
    #otherwise it is a GET request or error and we render the register page
        else:
            return "failed to validate"
    else:
        return render_template("register.html", form=form)

@blueprint.route("/login.html", methods=["GET", "POST"])
def login():
    """
    GET: Returns the login page login.html
    POST: Attempts to log in the user and redirects to my boards myboards.html
    """
    form = LoginForm()
    #handling the POST request
    if request.method == "POST":
        #checking for valid username and password field
        if form.validate_on_submit() and "username" in request.form and "password" in request.form:
            username = request.form["username"]
            password = request.form["password"]
            
            user = db_connect.get_db().fetch_user(userid=None, user_name = username)
            #if that username exits, checking the password for a match
            if user.get('username') is not None:
                if verify_password(password, user.get('password')):
                    #session['username'] = username
                    user = UserObject(username)
                    if login_user(user, remember=True):
                        session.permanent = True
                        return redirect(url_for('pages_blueprint.my_boards')) # Redirect wants function name, not endpoint
                    else:
                        return "An internal error occurred loggin you in"
                else:
                    return 'Invalid username or password, please try again!'
            else:
                return 'Invalid username or password, please try again!'
    #handling invalid inputs and the GET requests        
        flash('Invalid input, please try again!')
        return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)

@blueprint.route("/logout")
@login_required
def logout():
    """
    Logs out the user and redirects to the home page home.html
    """
    logout_user()
    flash("Logged out.")
    return redirect(url_for('pages_blueprint.index'))

# # Run the application
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)