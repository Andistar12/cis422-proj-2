# Sets up the endpoints for fetching and rendering pages from Flask

import flask

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("pages_blueprint", __name__)

# Page endpoints

@blueprint.route("/")
@blueprint.route("/index")
@blueprint.route("/home")
def index():
    """
    Returns the index page home.html
    """
    return flask.render_template("home.html")


@blueprint.app_errorhandler(404)
def page_not_found(error):
    """
    Returns the 404 page 404.html
    """
    flask.session["linkback"] = flask.url_for("pages_blueprint.index")
    return flask.render_template("404.html"), 404


@blueprint.route("/findboard")
def find_board():
    """
    Returns the find board page findboard.html
    """
    return flask.render_template("findboard.html")

@blueprint.route("/createboard", methods=["GET", "POST"])
def create_board():
    """
    GET: Returns the create new board page createboard.html
    POST: Creates a board and redirects to viewboard. Takes in the payload:
    {
        "name": board name with 175 char limit
        "description": board description
        "vote_threshold": percentage of community approval for post notification
    }
    """
    if flask.request.method == "GET":
        return flask.render_template("createboard.html")
    else:
        pass # TODO


@blueprint.route("/myboards.html")
def my_boards():
    """
    Returns the user's boards page myboards.html
    """
    return flask.render_template("myboards.html")


@blueprint.route("/viewboard", methods=["GET", "POST"])
def view_board():
    """
    GET: Returns the page for viewing a single board viewboard.html
    POST: Creates a post and redirects to viewpost. Takes in the payload:
    {
        "subject": subject with 175 char limit
        "description": Description of post
    }
    """
    if flask.request.method == "GET":
        return flask.render_template("viewboard.html")
    else:
        pass # TODO


@blueprint.route("/viewpost", methods=["GET", "POST"])
def view_post():
    """
    GET: Returns the page for viewing a single post viewpost.html
    POST: Creates a comment and refreshes the page (redirect to self). Takes in the payload:
    {
        "board_id": ID of the board it is being created under
        "post_id": ID of the post it is being created under
        "comment": user comment
    }
    """
    if flask.request.method == "GET":
        return flask.render_template("viewpost.html")
    else:
        pass # TODO


@blueprint.route("/makepost", methods=["GET", "POST"])
def make_post():
    """
    GET: Returns the page for making a post makepost.html
    POST: Creates a post and redirects to view that post. Takes in the payload:
    {
        "board_id": ID of the board it is being created under
        "subject": post subject
        "description": post description
    }
    """
    if flask.request.method == "GET":
        return flask.render_template("makepost.html")
    else:
        pass # TODO
