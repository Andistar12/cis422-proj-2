# Sets up the endpoints for fetching and rendering pages from Flask

import flask

import server_auth

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("pages_blueprint", __name__)

def is_authenticated():
    """
    Returns whether the user is logged in
    """
    return server_auth.is_authenticated()
    #return False

def is_admin():
    """
    Returns whether the user is an admin
    """
    return server_auth.is_admin()
    #return True

def get_curr_username():
    """
    Returns the current user's username
    """
    return server_auth.get_curr_username()

# Page endpoints

@blueprint.route("/")
@blueprint.route("/home.html")
def index():
    """
    Returns the index page home.html
    """
    return flask.render_template("home.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())

@blueprint.app_errorhandler(404)
def page_not_found(error):
    """
    Returns the 404 page 404.html
    """
    flask.session["linkback"] = flask.url_for("pages_blueprint.index")
    return flask.render_template("404.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username()), 404

@blueprint.app_errorhandler(403)
def page_not_found(error):
    """
    Returns the 403 page 403.html
    """
    flask.session["linkback"] = flask.url_for("pages_blueprint.index")
    return flask.render_template("403.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username()), 403

@blueprint.route("/admin.html")
def admin():
    """
    Returns the admin page
    """
    if not is_admin():
        flask.abort(403)
    return flask.render_template("admin.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())

@blueprint.route("/findboard.html")
def find_board():
    """
    Returns the find board page findboard.html
    """
    if not is_authenticated():
        flask.abort(403)
    return flask.render_template("findboard.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())

@blueprint.route("/createboard.html")
def create_board():
    """
    Returns the create new board page createboard.html
    """
    if not is_authenticated():
        flask.abort(403)
    return flask.render_template("createboard.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())

@blueprint.route("/myboards.html")
def my_boards():
    """
    Returns the user's boards page myboards.html
    """
    if not is_authenticated():
        flask.abort(403)
    return flask.render_template("myboards.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())

@blueprint.route("/viewboard.html")
def view_board():
    """
    Returns the page for viewing a single board viewboard.html. Takes in the parameters
    -  board_id: the ID of the board to display
    """
    if not is_authenticated():
        flask.abort(403)
    return flask.render_template("viewboard.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())

@blueprint.route("/viewpost.html")
def view_post():
    """
    Returns the page for viewing a single post viewpost.html
    """
    if not is_authenticated():
        flask.abort(403)
    return flask.render_template("viewpost.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())

@blueprint.route("/makepost.html")
def make_post():
    """
    Returns the page for making a post makepost.html
    """
    if not is_authenticated():
        flask.abort(403)
    return flask.render_template("makepost.html", is_authenticated=is_authenticated(), is_admin=is_admin(), username=get_curr_username())
