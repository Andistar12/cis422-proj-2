# Handles user authentication and account creation
import os
import secrets
import datetime
import flask_login
import hashlib
import flask

from os import O_RDONLY
from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
import json
import pandas as pd
import logging

from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)

from passlib.apps import custom_app_context as pwd_context
from passlib.hash import sha256_crypt as pwd_context

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

# importing our database 
# client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
client = MongoClient('mongodb://ourdb', 27017)
db = client.database
user = client.users

SECRET_KEY = "im super secret"


class register(Resource): #has to be a POST
    def post(self):
        # hash the password, insert usename and hashed pword into the database
        app.logger.debug("ENTERED USER REGISTRATION")

        username = request.form.get('username', default = "Default", type=str)
        password = pwd_context.encrypt(request.form.get('password', default = "None", type=str))
       
        findUser = user.users.find_one({"username": username})
        if (findUser):
            return {"message": "<h1>A user with that name already exists, please pick another user name.</h1>"}, 400
        else:
            user.users.insert({"username": username, "password": password})
            return {"message": "<H1>Registration success!</h1>"}, 201
        

class token(Resource):
    def get(self):
        # hash the password, compare to database, seturn error if not in there, token otherwise
        app.logger.debug("ENTERED USER LOGIN")
        
        username = request.args.get('username', default = "None", type=str)
        password = request.args.get('password', default = "None", type=str)
       
        findUser = user.users.find_one({"username": username})
        if (not findUser):
            return {"message": "No user matching that user name found!"}, 401
        else:
            if (verify_password(password, findUser["password"])):
                token = generate_auth_token(username).decode('utf-8')
               
                return {"message": "success", "token":token, "valid":10, "id": str(findUser["_id"])}, 200  
            else:
                return {"message": "Password does not match the one on record!"}, 401

def hash_password(password):
    return pwd_context.encrypt(password)


def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

def generate_auth_token(username, expiration=10):
    s = Serializer(SECRET_KEY, expires_in=expiration)
    return s.dumps({"username": username})


def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False, "Expired token!"    # valid token, but expired
    except BadSignature:
        return False, "Invalid token!"    # invalid token
    return True, "success"


# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("auth_blueprint", __name__)

# The Flask login manager
login_manager = flask_login.LoginManager()

# def is_admin():
#     """
#     Returns whether the user is an administrator
#     """
#     return False # TODO

# def is_authenticated():
#     """
#     Return whether the user is logged in
#     """
#     return False  # TODO

# @login_manager.user_loader
# def user_loader(username):
#     """
#     Loads the user if it exists
#     """
#     pass # TODO 

# # Page endpoints

# class User(flask_login.UserMixin):
#     """
#     The user class object for session/auth purposes
#     """
    
#     def __init__(self):
#         pass # TODO

#     def get_id(self):
#         return str(self.id)

# @blueprint.route("/register", methods=["GET", "POST"])
# def register():
#     """
#     GET: Returns the register account page register.html
#     POST: Attempts to register the account and redirects to the login page login.html
#     """
#     pass # TODO

# @blueprint.route("/login.html", methods=["GET", "POST"])
# def login():
#     """
#     GET: Returns the login page login.html
#     POST: Attempts to log in the user and redirects to my boards myboards.html
#     """
#     pass # TODO

# @blueprint.route("/logout")
# def logout():
#     """
#     Logs out the user and redirects to the home page home.html 
#     """
#     pass # TODO

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)