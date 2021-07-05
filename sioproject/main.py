import os
import requests
import time
import json
import base64
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from gauth import get_oauth_access_token

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

values = {
    'slider1': 25,
    'slider2': 0,
}


with open("gcp-service-account.json", "r") as fp:
    cred = json.load(fp)
    scopes = ["https://www.googleapis.com/auth/pubsub"]
    token = get_oauth_access_token(cred, scopes)
    headers = {"Authorization": token}


project = "lucid-flask-web"
sub = "test-sub"
subscription = f"projects/{project}/subscriptions/{sub}"
ENDPOINT = f"https://pubsub.googleapis.com/v1/{subscription}:"


def pull_events():
    decode_messages = []
    payload = dict(maxMessages=100)
    try:
        resp = requests.post(
            ENDPOINT + "pull",
            json=payload,
            headers=headers,
            timeout=10,
        ).json()
        if resp:
            print("=============================")
            print(json.dumps(resp, indent=4))
            decode_messages = [
                base64.b64decode(msg['message']['data']).decode("utf-8")
                for msg in resp['receivedMessages']
            ]
            print(decode_messages)
            payload = {"ackIds": [msg["ackId"] for msg in resp['receivedMessages']]}
            resp = requests.post(
                ENDPOINT + "acknowledge",
                json=payload,
                headers=headers,
            )

    except Exception as e:
        print("Ignore error", e)

    return decode_messages


@app.route('/')
def index():
    return render_template('index.html', **values)


@socketio.on('connect')
def test_connect():
    print("first time")
    print(request.headers)
    emit('after connect', {'data': 'Lets dance'})
    return "ok"


@socketio.on('Slider value changed')
def value_changed(message):
    values[message['who']] = message['data']
    emit('update value', message, broadcast=True)


@socketio.on('Ask queue')
def ask_queue(message):
    print("Any question?", message)
    events = pull_events()
    emit("send events", events)


if __name__ == '__main__':
    PORT = os.environ.get("PORT", 8080)
    socketio.run(app, debug=True, port=PORT)
