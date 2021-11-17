# Sets up the endpoints for interacting with the database (fetching boards, posts, comments)

import flask

import db_connect
import server_auth

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("api_blueprint", __name__)

# API endpoints

@blueprint.route("/api/boards")
def api_boards():
    """
    Fetches up to 50 boards. 

    GET request takes the following parameters:
    "search": string, a search query to filter boards by
    "offset": integer, offset for boards. For example, if offset=1 then this fetches boards 50-99.

    Returns an array of board objects in the following format:
    [
        {
            "board_id": string, unique ID of the board
            "board_name": string, name of the board
            "board_description": string, description of the board
            "board_date": string, creation date of the board
            "board_member_count": integer, number of members in the community
            "board_vote_threshold": integer, percentage of communtiy required for vote
            "subscribed": boolean, whether the user has subscribed to it or not
        },
        ...
    ]

    On error, return a JSON with "error" set to the message
    """
    db = db_connect.get_db() #fetch the db object
    data = flask.request.args #fetch the arguments from the GET request
    search = data['search'] #extract the search term and offset from the request
    offset = int(data['offset'])
    boards = db.fetch_boards(search, offset) #query database with keyword
    return flask.jsonify(boards) #return a JSON of the boards


@blueprint.route("/api/board/user")
def api_user_boards():
    """
    Fetches all user subscribed boards.

    Returns an array of board objects in the following format:
    [
        {
            "board_id": string, unique ID of the board
            "board_name": string, name of the board
            "board_description": string, description of the board
            "board_date": string, creation date of the board
            "board_member_count": integer, number of members in the community
            "board_vote_threshold": integer, percentage of communtiy required for vote
            "subscribed": boolean, whether the user has subscribed to it or not
        },
        ...
    ]

    On error, return a JSON with "error" set to the message
    """
    db = db_connect.get_db()
    username = server_auth.user_loader()
    if username is None:
        return "Error: Could not find user"
    user = db.fetch_user(None, username.username)
    if not user:
        return "Error: Could not find user"
    print(user)
    board_ids = user['subscriptions']
    boards = [db.fetch_board(i) for i in board_ids]
    return flask.jsonify(boards)

@blueprint.route("/api/admins")
def api_admins():
    """
    Fetches all admins.

    The user must be an administrator to perform this action.

    Returns the following payload:
    {
        "admins": list of Strings of admin usernames
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/admins/add", methods=["POST"])
def api_admins_add():
    """
    Adds an administrator to the system.

    The user must be an administrator to perform this action.

    POST request takes in the following payload:
    {
        "username": the username to add as administrator
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/admins/remove", methods=["POST"])
def api_admins_remove():
    """
    Removes an administrator from the system.

    The user must be an administrator to perform this action.

    POST request takes in the following payload:
    {
        "username": the username to add as administrator
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/board")
def api_board():
    """
    Fetches information about a board.

    GET request takes in the following parameters:
    "board_id": string, unique ID of the board

    Request returns the following board payload: 
    {
        "board_id": string, unique ID of the board
        "board_name": string, name of the board
        "board_description": string, description of the board
        "board_date": string, creation date of the board
        "board_vote_threshold": integer, percentage of communtiy required for vote
        "board_member_count": integer, number of members in the community
        "subscribed": boolean, whether the user has subscribed to it or not
        "board_posts": Array of all board posts (see below)
    }

    Posts have the following format:
    {
        "post_id": string, unique ID of the post
        "post_subject": string, subject of the post
        "post_description": string, description of the post
        "post_username": string, name of the post owner
        "post_date": string, creation date of the post
        "post_upvotes": integer, number of raw upvotes
        "post_notified": boolean, whether the post notification has already been triggered
        "upvoted": boolean, whether the user has upvoted it or not
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/board/create", methods=["POST"])
def api_board_add():
    """
    Creates a board.

    POST requests takes in the following payload:
    {
        "board_name": board name with 175 char limit
        "board_description": board description
        "board_vote_threshold": percentage of community approval for post notification
    }

    Returns the following payload:
    {
        "board_id": the ID of the newly created board
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/board/subscribe", methods=["POST"])
def api_board_subscribe():
    """
    Subscribes a user to a board. Unsubscribes if the user is subscribed.

    POST requests takes in the following payload:
    {
        "board_id": the board to subscribe to
    }

    On error, return a JSON with "error" set to the message
    """
    pass # TODO

@blueprint.route("/api/board/delete", methods=["POST"])
def api_board_delete():
    """
    Deletes a board from the database.

    The user must be an administrator to perform this action.

    POST requests take the following form:
    {
        "board_id": the ID of the board to delete
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/board/purge", methods=["POST"])
def api_board_purge():
    """
    Purges boards from the database.

    The user must be an administrator to perform this action.

    POST requests take the following form:
    {
        "board_id": the ID of the board to delete
        "days": the the minimum age of a post to purge it
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """

@blueprint.route("/api/post")
def api_post():
    """
    Fetches information about a post.

    GET request takes in the following parameters:
    "post_id": string, unique ID of the post

    Returns the following payload:
    {
        "post_id": string, unique ID of the post
        "post_subject": string, subject of the post
        "post_description": string, description of the post
        "post_username": string, name of the post owner
        "post_date": string, creation date of the post
        "post_upvotes": integer, number of raw upvotes
        "post_comments": Array of comments (see below)
    }

    Comments have the following format:
    {
        "comment_id": string, unique ID of the comment
        "comment_username": string, name of the comment owner
        "comment_message": string, message content of the comment
        "comment_date": string, creation date of the comment
        "comment_upvotes": integer, number of raw upvotes
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/post/create", methods=["POST"])
def api_post_create():
    """
    Creates a post.

    POST request takes in the following payload:
    {
        "board_id": the ID of the board to post under
        "post_subject": subject with 175 char limit
        "post_description": Description of post
    }

    The user must be subscribed to the board to subscribe.

    Returns the following payload:
    {
        "post_id": the ID of the newly created post
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/post/delete", methods=["POST"])
def api_post_delete():
    """
    Deletes a post from a board.

    The user must be an administrator to perform this action.

    POST request takes in the following payload:
    {
        "board_id": the ID of the board
        "post_id": the ID of the post
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/post/purge", methods=["POST"])
def api_post_purge():
    """
    Purges posts from a board.

    The user must be an administrator to perform this action.

    POST request takes in the following payload:
    {
        "board_id": the ID of the board
        "post_id": the ID of the post
        "days": the the minimum age of a post to purge it
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/post/upvote", methods=["POST"])
def api_post_upvote():
    """
    Upvotes a post. Triggers a notification if it passes the board vote threshold.

    If a post has already been notified, it can no longer be upvoted.

    If a user has already voted on a post it will be rescinded.

    POST request takes in the following payload:
    {
        "board_id": the unique ID of the board
        "post_id": the unique ID of the post
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/comment/create", methods=["POST"])
def api_comment_create():
    """
    Creates a comment under a post.

    POST request takes in the following payload:
    {
        "board_id": the ID of the board
        "post_id": the ID of the post
        "message": the contents of the message
    }

    Returns the following payload:
    {
        "comment_id": the ID of the newly created comment
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/comment/upvote", methods=["POST"])
def api_comment_upvote():
    """
    Upvotes a comment. 

    If a user has already voted on a comment it will be rescinded.

    POST request takes in the following payload:
    {
        "board_id": the unique ID of the board
        "post_id": the unique ID of the post
        "comment_id": the unique ID of the comment
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO

@blueprint.route("/api/comment/delete", methods=["POST"])
def api_comment_delete():
    """
    Deletes a comment.

    The user must be an administrator to perform this action.

    POST request takes in the following payload:
    {
        "board_id": the ID of the board
        "post_id": the ID of the post
        "comment_id": the ID of the comment
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    pass # TODO
