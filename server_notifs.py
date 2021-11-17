# Sets up logic for notifications

import flask
import pywebpush
import json

import config

# The blueprint for Flask to load in the main server file
blueprint = flask.Blueprint("notifs_blueprint", __name__)

temp_subscriptions = []

@blueprint.route("/push/subscription", methods=["GET", "POST"])
def push_subscription():
    """
    GET provides the VAPID public key for the client to authenticate and setup the subscription
    POST submits the subscription information to the system
    """
    if flask.request.method == "GET":
        vapid_pub_key = config.get("vapid_public_key", "")
        if vapid_pub_key == "":
            return flask.Response(status=200, mimetype="application/json") # TODO something else
        return flask.Response(
            response=json.dumps({"public_key": vapid_pub_key}),
            headers={"Access-Control-Allow-Origin": "*"},
            content_type="application/json"
        )
    else:
        subscription_token = flask.request.get_json().get("subscription_token", "")
        if subscription_token is not None and subscription_token != "":
            temp_subscriptions.append(subscription_token)
        #print("Subscriptions is", temp_subscriptions)
        return flask.Response(status=200, mimetype="application/json")

@blueprint.route("/push/test", methods=["POST"])
def push_test():
    """
    Test push notifications via web push
    """
    message = flask.request.get_json().get("message", "")
    if message is None or message == "":
        return flask.jsonify({"error": "Bad message"}), 400
    for sub in temp_subscriptions:
        print(send_web_push(sub, message))
    return flask.jsonify({"success": "1"})

def send_web_push(subscription_information, message_body):
    """
    Sends a single web push notification to one end client

    Parameters:
     - subscription_information: The end client subscription generated
     - message_body: The message string to send off
    """
    vapid_email = config.get("vapid_email", "")
    if vapid_email == "":
        return
    private_key = config.get("vapid_private_key", "")
    if private_key == "":
        return

    vapid_claims = {
        "sub": f"mailto: {vapid_email}"
    }
    print("Attempting to send message", message_body, "to", subscription_information)
    return pywebpush.webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=private_key,
        vapid_claims=vapid_claims
    )