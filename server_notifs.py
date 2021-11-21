"""
Sets up logic for notifications

Note that we are our own push server. This means we must offload notifications to
a separate worker thread to not stall the Flask response. Push notifications happen
on a separate thread from that of the request's
"""

import flask
import pywebpush
import json
import threading

from bson import ObjectId

import config
import db_connect
import server_auth

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("notifs_blueprint", __name__)

@blueprint.route("/push/subscription", methods=["GET", "POST"])
def push_subscription():
    """
    GET provides the VAPID public key for the client to authenticate and setup the subscription
    POST submits the subscription information to the system
    """
    if flask.request.method == "GET":
        # Return public key
        vapid_pub_key = config.get("vapid_public_key", "")
        if vapid_pub_key == "":
            # No valid pubkey found, we will return 500
            return flask.jsonify({"error": "Server does not have a valid VAPID pubkey"}), 503
        return flask.Response(
            # Return pubkey in JSON format
            response=json.dumps({"public_key": vapid_pub_key}),
            headers={"Access-Control-Allow-Origin": "*"},
            content_type="application/json"
        )
    else:
        # User must be subscribed to do notifications
        if not server_auth.is_authenticated():
            return flask.jsonify({"error": "You must be logged in to subscribe to notifications"}), 403

        # Add or remove subscription from database
        subscription_token = flask.request.get_json().get("subscription_token", "")
        if subscription_token is None or subscription_token == "":
            return flask.jsonify({"error": "Invalid subscription"}), 400
        add_sub = flask.request.get_json().get("subscribe", "False")
        if add_sub:
            db_connect.get_db().add_notification(userid=None, user_name=server_auth.get_curr_username(), notification=subscription_token)
        else:
            db_connect.get_db().remove_notification(userid=None, user_name=server_auth.get_curr_username(), notification=subscription_token)
        return flask.Response(status=200, mimetype="application/json")

@blueprint.route("/push/test", methods=["POST"])
def push_test():
    """
    Test push notifications via web push. TODO remove or protect in production
    """
    # Validate message
    post_id = flask.request.get_json().get("post_id", "")
    board_id = flask.request.get_json().get("board_id", "")
    if post_id is None or post_id == "" or board_id is None or board_id == "":
        return flask.jsonify({"error": "Bad payload"}), 400
    return do_push_notifications(board_id=ObjectId(board_id), post_id=ObjectId(post_id))

def do_push_notifications(board_id: ObjectId, post_id: ObjectId):
    """
    Performs the action of notifying all users of a post. This is an expensive operation but will return immediately

    Parameters:
     - board_id: The board ID of the post
     - post_id: The post ID of the post
    Returns:
     - A Flask response that can be immediately returned to the client
    """

    # Valid VAPID credentials
    vapid_email = config.get("vapid_email", "")
    if vapid_email == "":
        return flask.jsonify({"error": "Server does not have a valid VAPID email"}), 503
    private_key = config.get("vapid_private_key", "")
    if private_key == "":
        return flask.jsonify({"error": "Server does not have a valid VAPID private key"}), 503

    # Define function to run in worker thread (expensive)
    db_obj = db_connect.get_db()
    def _push_notif_worker(board_id, post_id, vapid_email, private_key):
        post = db_obj.fetch_post(board_id, post_id)
        msg = post.get("post_subject", "Unknown post subject")
        board = db_obj.fetch_board(board_id)
        board_members = board.get("board_members", [])
        for m in board_members:
            member = db_obj.fetch_user(userid=m, user_name=None)
            subscriptions = member.get("notification", [])
            for s in subscriptions:
                payload = {
                    "username": str(member["username"]),
                    "board_name": str(board["board_name"]),
                    "message": msg
                }
                try:
                    send_web_push(s, json.dumps(payload), vapid_email, private_key)
                except pywebpush.WebPushException as e:
                    if "subscription has unsubscribed or expired" in str(e):
                        # Remove the subscription for the future
                        db_obj.remove_notification(userid=None, user_name=member["username"], notification=s)

    # Setup thread (daemon) worker and start it
    t = threading.Thread(target=_push_notif_worker, args=(board_id, post_id, vapid_email, private_key,), daemon=True)
    t.start()

    # Finally, send back a proper response
    return flask.Response(status=200, mimetype="application/json")


def send_web_push(subscription_information, payload, vapid_email, private_key):
    """
    Sends a single web push notification to one end client

    Parameters:
     - subscription_information: The end client subscription generated
     - payload: The message string to send off
     - vapid_email: The email of the VAPID key
     - private_key: The private VAPID key
    """
    #print("Attempting to send message", message_body, "to", subscription_information)
    return pywebpush.webpush(
        subscription_info=subscription_information,
        data=payload,
        vapid_private_key=private_key,
        vapid_claims={
            "sub": f"mailto: {vapid_email}"
        }
    )
