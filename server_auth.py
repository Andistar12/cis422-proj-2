# Handles user authentication and account creation

import flask_login
import flask

from flask import render_template, request, session, redirect, url_for, flash, abort
from flask_restful import Resource, Api

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

from passlib.apps import custom_app_context as pwd_context
from passlib.hash import sha256_crypt as pwd_context

from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators

   
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


def hash_password(password):
    return pwd_context.encrypt(password)


def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)


# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("auth_blueprint", __name__)

# The Flask login manager
login_manager = flask_login.LoginManager()

@login_required
def is_admin(username):
    """
    Returns whether the user is an administrator
    """
    #get the list of current admins
    admins = flask.current_app.db.fetch_admins(user_name = username)
    if username in admins:
        return True
    return False

def is_authenticated(username):
    """
    Return whether the user is logged in
    """
    if username in session:
        print('You are loggen in as ' + session['username'])
        return True 
    return False  

@login_manager.user_loader
def user_loader(username):
    """
    Loads the user if it exists
    """
    user = flask.current_app.db.fetch_user(user_name=username)
    if user.get('username') == username:
        session['username'] = username        
    return 'The user with username' + username + ' has been loaded in.'
    

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
            username = request.form["username"].encode('utf-8')
            password = request.form["password"].encode('utf-8')
                
                    
            #search for a user with the provided user name
            user = flask.current_app.db.fetch_user(user_name = username)
            #if the user isnt found, hash the password and register the new user      
            if user.get('username') is None:
                hashed_pass = hash_password(password)
                flask.current_app.db.add_user(user_name = username, password = hashed_pass)
                session['username'] = request.form['username']
                return redirect(url_for('home.html'))
            else:
                return 'A user with that username already exists, please try another username.'   
    #otherwise it is a GET request or error and we render the register page
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
            username = request.form["username"].encode('utf-8')
            password = request.form["password"].encode('utf-8')
            
            user = flask.current_app.db.fetch_user(user_name = username)
            #if that username exits, checking the password for a match
            if user.get('username') is not None:
                if user.get('password') == verify_password(password, user.get('password')):
                    session['username'] = username        
                    return redirect(url_for('myboards.html'))
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
    return redirect(url_for("home.html"))

# # Run the application
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)