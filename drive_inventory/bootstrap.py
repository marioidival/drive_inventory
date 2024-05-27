import inspect
from typing import Callable
from drive_inventory.adapters.notifications import (
    AbstractNotifications,
    EmailNotifications,
)
from drive_inventory.adapters.repository import AbstractRepository, MongoRepository
from drive_inventory.adapters.drive import AbstractDrive, DriveAdapter
from drive_inventory.config import load_credentials


def bootstrap(
    drive_adapter: AbstractDrive,
    mail_adapter: AbstractNotifications,
    repo: AbstractRepository,
):
    return {
        "drive": drive_adapter,
        "mail": mail_adapter,
        "repo": repo,
    }
