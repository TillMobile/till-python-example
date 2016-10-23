import os
import uuid
import json
import requests

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from pusher import Pusher

TILL_URL = os.environ.get("TILL_URL")
PUSHER_URL = os.environ.get("PUSHER_URL")
PUSHER_URL_CHUNKS = PUSHER_URL.split("http://")[1].split(":")
PUSHER_KEY = PUSHER_URL_CHUNKS[0]
PUSHER_SECRET = PUSHER_URL_CHUNKS[1].split("@")[0]
PUSHER_APP_ID = PUSHER_URL_CHUNKS[1].split("@")[1].split("/")[2]

app = Flask(__name__)
pusher = Pusher(app_id=PUSHER_APP_ID, key=PUSHER_KEY, secret=PUSHER_SECRET)

@app.route("/")
def index():
    return render_template(
        "index.html",
        uuid=str(uuid.uuid4()),
        pusher_token=PUSHER_KEY
    )

@app.route("/send/", methods=["POST"])
def send():
    resp = requests.post(TILL_URL, json={
        "phone": [request.form["phone_number"]],
        "questions" : [{
            "text": "Favorite color?",
            "tag": "favorite_color",
            "responses": ["Red", "Green", "Yellow"],
            "webhook": "%s?uuid=%s" % (request.form["webhook_url"], request.form["uuid"])
        }]
    })
    return jsonify(status="success")

@app.route("/results/", methods=["POST"])
def results():
    pusher.trigger(request.args.get("uuid"), "result", json.loads(request.data))
    return jsonify(status="success")

if __name__ == "__main__":
    app.run()
