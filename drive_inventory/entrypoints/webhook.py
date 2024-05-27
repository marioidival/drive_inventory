import json

from drive_inventory.bootstrap import bootstrap
from flask import Flask, request, jsonify

from drive_inventory.adapters.drive import DriveAdapter
from drive_inventory.adapters.notifications import EmailNotifications
from drive_inventory.adapters.repository import MongoRepository
from drive_inventory.config import load_credentials
from drive_inventory.service_layer.sync_files import DriveService

app = Flask(__name__)
drive_service, gmail_service = load_credentials()
deps = bootstrap(
    DriveAdapter(drive_service),
    EmailNotifications(gmail_service),
    MongoRepository(),
)


@app.route("/", methods=["POST"])
def webhookindex():
    data = request.data
    print("index", data)
    return jsonify({"status": "received"}), 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.data
    print(data)
    return jsonify({"status": "received"}), 200


def watch_changes(drive_service):
    body = {
        "id": "mylolid511",
        "type": "webhook",
        "address": "https://73cc-2804-29b8-5066-4ef9-5d5a-7409-1d9d-f652.ngrok-free.app/webhook",
    }
    token_response = drive_service.changes().getStartPageToken().execute()
    response = (
        drive_service.changes()
        .watch(pageToken=token_response["startPageToken"], body=body)
        .execute()
    )

    print("Watch response:", json.dumps(response, indent=2))


if __name__ == "__main__":
    drive_creds, _ = load_credentials()

    watch_changes(drive_creds)

    app.run(port=4545)
