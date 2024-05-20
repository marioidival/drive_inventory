import os.path
import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)
        output = process_files(service)

        pprint.pprint(output)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def process_files(service):
    next_page_token = None
    output = []
    while True:
        results = (
            service.files()
            .list(
                pageSize=100,
                fields="nextPageToken, files(id, name, owners, permissions, sharingUser, fileExtension, modifiedTime, mimeType, md5Checksum)",
                pageToken=next_page_token,
                corpora="user",
            )
            .execute()
        )
        items = results.get("files", [])

        if not items:
            print("No files found.")
            break

        for item in items:
            db = {
                "filename": item["name"],
                "id": item["id"],
                "file_extension": item.get("fileExtension"),
                "updated_at": item["modifiedTime"],
                "mimetype": item.get("mimeType"),
                "owned_by_me": any(owner["me"] for owner in item.get("owners", [])),
                "checksum": item.get("md5Checksum"),
                "visibility": (
                    "public"
                    if any(
                        p["id"] == "anyoneWithLink" for p in item.get("permissions", [])
                    )
                    else "private"
                ),
            }

            if len(item["owners"]) > 0:
                # currently, only certain legacy files may have more than one owner.
                # I would like to take the first item on the list anyway
                db["owner_file"] = item["owners"][0]["emailAddress"]

            if not db["file_extension"]:
                # this will fix the issues whet a google files comes in the result
                # the idea is take the last part of mimetype and turn it as file extension for
                # google files
                db["file_extension"] = db["mimetype"].split(".")[-1]

            output.append(db)

        # next_page_token = results.get("nextPageToken")
        if next_page_token is None:
            break

    return output


if __name__ == "__main__":
    main()
