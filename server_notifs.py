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

import config
import db_connect

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("notifs_blueprint", __name__)

# Temporary storage for subscriptions TODO move this into database
temp_subscriptions = []

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
        # Add or remove subscription from database
        global temp_subscriptions
        subscription_token = flask.request.get_json().get("subscription_token", "")
        if subscription_token is None or subscription_token == "":
            return flask.jsonify({"error": "Invalid subscription"}), 400
        add_sub = flask.request.get_json().get("subscribe", "False")
        if add_sub == True:
            # For now add to local array. TODO add to database
            temp_subscriptions.append(subscription_token)
        else:
            # For now remove from local array. TODO remove from database
            p256dh = subscription_token["keys"]["p256dh"] # Identifier for key
            temp_subscriptions = [x for x in temp_subscriptions if x["keys"]["p256dh"] != p256dh]
        #print("Subscriptions list:", temp_subscriptions)
        return flask.Response(status=200, mimetype="application/json")

@blueprint.route("/push/test", methods=["POST"])
def push_test():
    """
    Test push notifications via web push. TODO remove or protect in production
    """
    # Validate message
    message = flask.request.get_json().get("message", "")
    if message is None or message == "":
        return flask.jsonify({"error": "Bad message"}), 400
    return do_push_notifications(board_id=message, post_id=None)

def do_push_notifications(board_id, post_id):
    """
    Performs the action of notifying all users of a post. This is an expensive operation

    If testing, set post_id to None and board_id to the message to send

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
    def _push_notif_worker(board_id, post_id, vapid_email, private_key):
        post = db_connect.get_db().fetch_post(post_id)
        msg = post["post_subject"]
        board_members = db_connect.get_db().fetch_board(board_id)["board_members"]
        for m in board_members:
            member = db_connect.get_db().fetch_user(userid=m, user_name=None)
            subscriptions = [] # TODO get user subscriptions here
            for s in subscriptions:
                send_web_push(s, msg, vapid_email, private_key)

    # Define test function to run in worker thread (expensive)
    def _push_notif_worker_test(msg, vapid_email, private_key):
        global temp_subscriptions
        for sub in temp_subscriptions:
            send_web_push(sub, msg, vapid_email, private_key)

    # Setup thread (daemon) worker and start it
    if post_id is None:
        target = _push_notif_worker_test
        args = (board_id, vapid_email, private_key,)
    else:
        target = _push_notif_worker
        args = (board_id, post_id, vapid_email, private_key,)
    t = threading.Thread(target=target, args=args, daemon=True)
    t.start()

    # Finally, send back a proper response
    return flask.Response(status=200, mimetype="application/json")


def send_web_push(subscription_information, message_body, vapid_email, private_key):
    """
    Sends a single web push notification to one end client

    Parameters:
     - subscription_information: The end client subscription generated
     - message_body: The message string to send off
     - vapid_email: The email of the VAPID key
     - private_key: The private VAPID key
    """
    #print("Attempting to send message", message_body, "to", subscription_information)
    return pywebpush.webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=private_key,
        vapid_claims={
            "sub": f"mailto: {vapid_email}"
        }
    )
