from drive_inventory.adapters.drive import DriveAdapter
from drive_inventory.adapters.notifications import EmailNotifications
from drive_inventory.adapters.repository import MongoRepository
from drive_inventory.config import load_credentials
from drive_inventory.service_layer.sync_files import DriveService


def main():
    drive_creds, gmail_creds = load_credentials()
    google_drive = DriveAdapter(drive_creds)
    gmail = EmailNotifications(gmail_creds)
    mongo = MongoRepository()

    sync_files_service = DriveService(
        drive_adapter=google_drive, mail_adapter=gmail, db_adapter=mongo
    )

    while True:
        sync_files_service.sync_files()

        print("sync files ran")


if __name__ == "__main__":
    main()
