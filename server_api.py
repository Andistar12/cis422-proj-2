# Sets up the endpoints for interacting with the database (fetching boards, posts, comments)

import flask

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
    pass # TODO


@blueprint.route("/api/user_boards")
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
    pass # TODO


@blueprint.route("/api/board_subscribe", methods=["POST"])
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

    On error, return a JSON with "error" set to the message
    """
    pass # TODO


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

    On error, return a JSON with "error" set to the message
    """
    pass # TODO


@blueprint.route("/api/post_upvote", methods=["POST"])
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

    Returns a JSON with "error" or "success" set to an associated message.
    """
    pass # TODO


@blueprint.route("/api/comment_upvote", methods=["POST"])
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

    Returns a JSON with "error" or "success" set to an associated message.
    """
    pass # TODO
