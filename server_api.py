# Sets up the endpoints for interacting with the database (fetching boards, posts, comments)

import flask
import flask_restful
from flask import Response

import db_connect
import server_auth
import server_notifs
import bson
import pymongo
import re
from bson import json_util
from bson.objectid import ObjectId

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("api_blueprint", __name__)

# API endpoints

def err(msg, status=400):
    return {'error': str(msg)}, status

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
    try:
        search = data['search'] #extract the search term and offset from the request
        try:
            offset = int(data['offset'])
        except ValueError:
            return err('offset must be a positive integer')
        if offset < 0:
            return err('offset must be a positive integer')
    except KeyError:
        return err('Must provide search term and offset')
    try:
        boards = db.fetch_boards(search, offset, False) #query database with keyword
    except (pymongo.errors.OperationFailure, re.error):
        return err('Invalid search given')
    return json_util.dumps(boards) # Return a JSON (using BSON decoder) of the boards


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
    if not server_auth.is_authenticated():
        return flask.Response({"error": "Must be logged in to fetch boards"}, status=403)
    db = db_connect.get_db()
    username = server_auth.get_curr_username()
    if username is None or not (user := db.fetch_user(None, username)):
        return flask.Response({"error": "Could not find user"}, status=404)
    board_ids = user['subscriptions']
    boards = []
    for i in board_ids:
        obj = db.fetch_board(i)
        board = {
            'board_id': str(obj['_id']),
            'board_name': obj['board_name'],
            'board_description': obj['board_description'],
            'board_date': str(obj['board_date']),
            'board_member_count': obj['board_member_count'],
            'board_vote_threshold': obj['board_vote_threshold'],
            "subscribed": True
        }
        boards.append(board)
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
    if server_auth.is_admin():
        db = db_connect.get_db()
        admins = db.fetch_admins()
        admins = [i['username'] for i in admins]
        return flask.jsonify(admins)
    return Response({"error": "User must be an admin to request admins"}, status=403)

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
    if server_auth.is_admin():
        db = db_connect.get_db()
        try:
            username = flask.request.form['username']
        except KeyError:
            return err('Must provide a username')
        try:
            ret = db.add_admin(None, username)
        except ValueError as e:
            return err(e)
        if ret is None:
            return err('Could not find user %s' % username, 404)
        else:
            return Response(status=200)
    return err('User must be an admin to add an admin', 403)

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
    if server_auth.is_admin():
        db = db_connect.get_db()
        try:
            username = flask.request.form['username']
        except KeyError:
            return err('Must provide a username')
        ret = db.remove_admin(None, username)
        if ret is None:
            return err('Could not find user %s' % username, 404)
        else:
            return Response(status=200)
    return err('User must be an admin to remove an admin', 403)

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
    db = db_connect.get_db()
    try:
        board_id = ObjectId(flask.request.args["board_id"])
    except KeyError:
        return err('Must provide a board id')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    obj = db.fetch_board(board_id)
    if not obj:
        return err('Could not find board %s' % board_id, 404)
    username = server_auth.get_curr_username()
    user = db.fetch_user(None, username)
    if not user:
        subscribed = False
    else:
        subs = user['subscriptions']
        subscribed = board_id in subs
    posts = obj["board_posts"]
    board = {
        'board_id': str(obj['_id']),
        'board_name': obj['board_name'],
        'board_description': obj['board_description'],
        'board_date': str(obj['board_date']),
        'board_vote_threshold': obj['board_vote_threshold'],
        'board_member_count': obj['board_member_count'],
        "subscribed": subscribed,
        "posts": posts
    }
    return json_util.dumps(board)

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
    if not server_auth.is_authenticated():
        return err('Must be logged in to create board', 403)
    form = flask.request.form
    try:
        name = form['board_name']
        desc = form['board_description']
        threshold = form['board_vote_threshold']
    except KeyError:
        return err('Missing required arguments to create board')
    if not name or not isinstance(name, str) or len(name) > 25:
        return err('Board name must be a string with 1-25 characters')
    if not desc or not isinstance(desc, str) or len(desc) > 100:
        return err('Board description must be a string with 1-100 characters')
    try:
        threshold = int(threshold)
    except ValueError:
        return err('Board vote threshold must be an integer, 0 < n <= 100')
    if not threshold or not isinstance(threshold, int) or threshold < 1 or threshold > 100:
        return err('Board vote threshold must be an integer, 0 < n <= 100')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    try:
        val = db.create_board(None, username, name, desc, threshold)
    except ValueError as e:
        return err(e)
    ret = {'board_id': str(val)}
    return flask.jsonify(ret)

@blueprint.route("/api/board/subscribe", methods=["POST"])
def api_board_subscribe():
    """
    Subscribes a user to a board.

    POST requests takes in the following payload:
    {
        "board_id": the board to subscribe to
    }

    On error, return a JSON with "error" set to the message
    """
    if not server_auth.is_authenticated():
        return err('Must be logged in to subscribe to board', 403)
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
    except KeyError:
        return err('Must provide a board id')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    ret = db.subscribe_board(None, username, board_id)
    if ret is None:
        return err('Could not subscribe to board', 404)
    return Response(status=200)

@blueprint.route("/api/board/unsubscribe", methods=["POST"])
def api_board_unsubscribe():
    """
    Unsubscribes a user from a board.

    POST requests takes in the following payload:
    {
        "board_id": the board to subscribe to
    }

    On error, return a JSON with "error" set to the message
    """
    if not server_auth.is_authenticated():
        return err('Must be logged in to unsubscribe from board', 403)
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
    except KeyError:
        return err('Must provide a board id')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    ret = db.unsubscribe_board(None, username, board_id)
    if ret is None:
        return err('Could not subscribe to board', 404)
    return Response(status=200)


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
    if not server_auth.is_admin():
        return err('Must be an admin to delete a board', 403)
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
    except KeyError:
        return err('Must provide a board id')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    db = db_connect.get_db()
    username = server_auth.get_curr_username()
    ret = db.delete_board(None, username, board_id)
    if ret is None:
        return err('Could not delete board', 404)
    return Response(status=200)

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
    "board_id": string, unique ID of the post's board
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
        "upvoted": Boolean, true if user is logged in and has upvoted the post
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
    args = flask.request.args
    try:
        board_id = ObjectId(args['board_id'])
        post_id = ObjectId(args['post_id'])
    except KeyError:
        return err('Must provide a board id and post id')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    db = db_connect.get_db()
    obj = db.fetch_post(board_id, post_id)
    if not obj:
        return err('Could not find post', 404)
    comments = db.fetch_comments(post_id)
    upvoted = False
    if server_auth.is_authenticated():
        username = server_auth.get_curr_username()
        user = db.fetch_user(None, username)
        user_id = user['_id']
        upvotes = obj['post_upvoters']
        upvoted = ObjectId(user_id) in upvotes
    owner = db.fetch_user(userid=obj['post_owner'], user_name=None)
    owner_username = owner['username']
    post = {
        'post_id': str(obj['_id']),
        'post_subject': obj['post_subject'],
        'post_description': obj['post_description'],
        "post_username": owner_username,
        "post_date": obj['post_date'],
        "post_upvotes": obj['post_upvotes'],
        "post_comments": comments,
        "post_notified": obj['post_notified'],
        "upvoted": upvoted
    }
    return json_util.dumps(post)

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

    The user must be subscribed to the board to create a post.

    Returns the following payload:
    {
        "post_id": the ID of the newly created post
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    if not server_auth.is_authenticated():
        return err('Must be logged in to create a post', 403)
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    user = db.fetch_user(None, username)
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
        subject = form['post_subject']
        description = form['post_description']
    except KeyError:
        return err('Missing required arguments to create post')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    if not subject or not isinstance(subject, str) or len(subject) > 100:
        return err('Subject must be a string with 1-100 characters', 403)
    if not description or not isinstance(description, str) or len(description) > 1000:
        return err('Description must be a string with 1-1000 characters', 403)
    if board_id not in user['subscriptions']:
        return err('Must be subscribed to post to board', 403)
    ret = db.create_post(None, username, board_id, subject, description)
    if not ret:
        return err('Could not create post', 404)
    return flask.jsonify({'post_id': str(ret)})

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
    if not server_auth.is_admin():
        return err('Must be an administrator to delete a post', 403)
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
        post_id = ObjectId(form['post_id'])
    except KeyError:
        return err('Must provide board and post ids')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    ret = db.delete_post(None, username, board_id, post_id)
    if ret is None:
        return err('Could not delete post', 404)
    return Response(status=200)

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
    if not server_auth.is_authenticated():
        return err('Must be logged in to upvote a post', 403)
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
        post_id = ObjectId(form['post_id'])
    except KeyError:
        return err('Must provide board and post ids')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    ret = db.upvote_post(None, username, board_id, post_id)
    if not ret:
        return err('Could not upvote post', 404)
    board = db.fetch_board(board_id)
    post = db.fetch_post(board_id, post_id)
    threshold = int(board['board_vote_threshold'])
    upvotes = int(post['post_upvotes'])
    subscribers = int(board['board_member_count'])
    #notify if not already notified and upvote ratio exceeds threshold
    #upvotes/subscribers >= threshold/100
    #multiply both sides by (100*subscribers) to get:
    if (upvotes * 100) >= (subscribers * threshold):
        if not post['post_notified']:
            server_notifs.do_push_notifications(board_id, post_id)
            db.notify_post(board_id, post_id)
    return Response(status=200)

@blueprint.route("/api/post/upvote/cancel", methods=["POST"])
def api_post_cancel_vote():
    """
    Rescinds an upvote on a post.

    If a post has already been notified, it's votes can no longer be rescinded.

    POST request takes in the following payload:
    {
        "board_id": the unique ID of the board
        "post_id": the unique ID of the post
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    if not server_auth.is_authenticated():
        return err('Must be logged in to cancel a vote', 403)
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
        post_id = ObjectId(form['post_id'])
    except KeyError:
        return err('Must provide board and post ids')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    ret = db.unupvote_post(None, username, board_id, post_id)
    if not ret:
        return err('Could not cancel vote', 404)
    return Response(status=200)

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
    if not server_auth.is_authenticated():
        return err('Must be logged in to post a comment', 403)
    form = flask.request.form
    try:
        board_id = ObjectId(form['board_id'])
        post_id = ObjectId(form['post_id'])
        message = form['message']
    except KeyError:
        return err('Must provide board id, post id, and message')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    ret = db.add_comment(None, username, board_id, post_id, message)
    if not ret:
        return err('Could not create comment', 404)
    return flask.jsonify({'comment_id': str(ret)})

@blueprint.route("/api/comment/upvote", methods=["POST"])
def api_comment_upvote():
    """
    Upvotes a comment. 

    If a user has already voted on a comment it will be rescinded.

    POST request takes in the following payload:
    {
        "post_id": the unique ID of the post
        "comment_id": the unique ID of the comment
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    if not server_auth.is_authenticated():
        return err('Must be logged in to upvote a comment', 403)
    form = flask.request.form
    try:
        post_id = ObjectId(form['post_id'])
        comment_id = ObjectId(form['comment_id'])
    except KeyError:
        return err('Must provide post and comment ids')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    ret = db.upvote_comment(None, username, post_id, comment_id)
    if not ret:
        return err('Could not upvote comment', 404)
    return Response(status=200)

@blueprint.route("/api/comment/delete", methods=["POST"])
def api_comment_delete():
    """
    Deletes a comment.

    The user must be an administrator to perform this action.

    POST request takes in the following payload:
    {
        "post_id": the ID of the post
        "comment_id": the ID of the comment
    }

    Returns 200 OK or a JSON with "error" set to an associated message.
    """
    if not server_auth.is_authenticated():
        return err('Must be logged in to delete a comment', 403)
    form = flask.request.form
    try:
        post_id = ObjectId(form['post_id'])
        comment_id = ObjectId(form['comment_id'])
    except KeyError:
        return err('Must provide post and comment ids')
    except bson.errors.InvalidId:
        return err('Given id is not well-formed')
    username = server_auth.get_curr_username()
    db = db_connect.get_db()
    ret = db.delete_comment(None, username, post_id, comment_id)
    if not ret:
        return err('Could not delete comment', 404)
    return Response(status=200)
