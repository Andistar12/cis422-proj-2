# Handles user authentication and account creation


# Import helper functions from Flask
import flask
from flask import render_template, request, session, redirect, url_for, flash

# Import helper functions from passlib for password hashing
from passlib.hash import sha256_crypt as pwd_context

# Import helper functions from flask login for user auth
import flask_login
from flask_login import login_required, logout_user, UserMixin, fresh_login_required, login_user
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators, PasswordField

# Import our modules
import db_connect
import config
   
class LoginForm(Form):
    """
    Represents the login form object for form validation
    """
    username = StringField('Username', [
        validators.Length(min=2, max=25,
        message=u"Username must be between 2 and 25 characters long"),
        validators.InputRequired(u"Username input is required.")])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
        message=u"Password must be between 2 and 25 characters long"),
        validators.InputRequired(u"Password input is required")])

class RegisterForm(Form):
    """
    Represents the registration form object for form validation
    """
    username = StringField('Username', [
        validators.Length(min=2, max=25,
        message=u"Username must be between 2 and 25 characters long"),
        validators.InputRequired(u"Username input is required.")])
    password = PasswordField('New Password', [
        validators.Length(min=2, max=25,
        message=u"Password must be between 2 and 25 characters long"),
        validators.InputRequired(u"Password input is required"),
        validators.EqualTo("confirm", message="Passwords must match")])
    confirm = PasswordField("Confirm password")

def get_salt(base_string: str):
    """
    Fetches the hash salt to use for SHA256

    Parameters:
     - base_string: the base string to use as the salt
    Returns:
     - A 16 character salt
    """
    return base_string.replace(" ", "")[:16].zfill(16)

def hash_password(password):
    """
    Hashes a given password using SHA256

    Parameters:
     - password: the cleartext password to hash
    Returns:
      - The newly hashed password
    """
    return pwd_context.hash(password, salt=get_salt(config.get("secret_key", "super secret")))

def verify_password(password, hashVal):
    """
    Verifies a password matches a given hash

    Parameters:
     - password: the password in cleartext to verify
     - hashVal: The hashed password to verify against
    Returns:
     - Whether the passwords match
    """
    return pwd_context.verify(password, hashVal)


# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("auth_blueprint", __name__)

# The Flask login manager
login_manager = flask_login.LoginManager()

@blueprint.record_once
def on_load(state):
    """
    Initiates the Flask app with the login manager
    """
    login_manager.init_app(state.app)

class UserObject(UserMixin):
    """
    Represents our user object for Flask-Login to track
    """

    def __init__(self, username: str):
        """
        Initiates the user class with a username
        """
        self.username = username

    def get_id(self):
        """
        Fetches the UserMixin ID, which we identify using the username
        """
        return str(self.username)


def is_admin():
    """
    Returns whether the user is an administrator
    """
    # Check if they are even logged in first
    if not is_authenticated():
        return False

    # get the list of current admins
    admins = db_connect.get_db().fetch_admins()
    if len(admins) == 0:
        return True # Decided that if no admins present, all users have admin privileges

    for admin in admins: # Check all admins
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
    if is_authenticated():
        return flask_login.current_user.get_id()
    return ""

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
                flash("Account successfully created. Please log in", "info")
                return redirect(url_for('auth_blueprint.login')) # Redirect wants function name, not endpoint
            else:
                flash("A user with that username already exists.", "error")
                return redirect(url_for("auth_blueprint.register"))
        else:
            for _, err in form.errors.items():
                flash(err, "error")
            return redirect(url_for("auth_blueprint.register"))
    # otherwise it is a GET request or error and we render the register page
    else:
        return render_template("register.html", form=form, username="")

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
                        flash("Welcome, " + username, "info")
                        return redirect(url_for('pages_blueprint.my_boards')) # Redirect wants function name, not endpoint
                    else:
                        flash("An internal error occurred. Please try again", "error")
                        return redirect(url_for('auth_blueprint.login'))
                else:
                    flash("Invalid username or password. Please try again", "error")
                    return redirect(url_for('auth_blueprint.login'))
            else:
                flash("Invalid username or password. Please try again", "error")
                return redirect(url_for('auth_blueprint.login'))
        #handling invalid inputs and the GET requests
        for _, err in form.errors.items():
            flash(err, "error")
        return redirect(url_for('auth_blueprint.login'))
    else:
        return render_template("login.html", form=form, username="")

@blueprint.route("/logout")
@login_required
def logout():
    """
    Logs out the user and redirects to the home page home.html
    """
    logout_user()
    flash("Logged out.")
    return redirect(url_for('pages_blueprint.index'))
