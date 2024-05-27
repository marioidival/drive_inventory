import logging

from drive_inventory.adapters.drive import DriveAdapter
from drive_inventory.adapters.notifications import EmailNotifications
from drive_inventory.adapters.repository import MongoRepository
from drive_inventory.config import load_credentials
from drive_inventory.service_layer.sync_files import DriveService


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level="INFO"
)
logger = logging.getLogger(__name__)


def main():
    logging.info("loading credential")
    drive_creds, gmail_creds = load_credentials()
    logging.info("loading drive adapter")
    google_drive = DriveAdapter(drive_creds)
    logging.info("loading gmail notification")
    gmail = EmailNotifications(gmail_creds)

    logging.info("loading mongodb repository")
    mongo = MongoRepository()

    sync_files_service = DriveService(
        drive_adapter=google_drive, mail_adapter=gmail, db_adapter=mongo
    )

    while True:
        logging.info("entrypoint: sync files")
        sync_files_service.sync_files()


if __name__ == "__main__":
    main()
