import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def get_mongodb_uri():
    host = os.environ.get("DB_HOST", "localhost")
    # port = 54321 if host == "localhost" else 27017
    port = os.environ.get("DB_PORT", 27017)
    # password = os.environ.get("DB_PASSWORD", "abc123")
    # user, db_name = "allocation", "allocation"
    # return f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
    return f"mongodb://{host}:{port}/"


def load_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    drive_service = build("drive", "v3", credentials=creds)
    gmail_service = build("gmail", "v1", credentials=creds)
    return drive_service, gmail_service
