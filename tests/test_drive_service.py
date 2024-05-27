from drive_inventory.adapters.repository import FileAlreadySavedException
import pytest

from unittest.mock import Mock
from datetime import datetime

from drive_inventory.service_layer.sync_files import DriveService


@pytest.fixture
def drive_service():
    _drive = Mock()
    _mail = Mock()
    _repo = Mock()
    return DriveService(_drive, _mail, _repo)


def test_sync_files_new_file(drive_service):
    drive_service._drive.list_files.return_value = {
        "files": [
            {
                "id": "1",
                "name": "Test File",
                "mimeType": "text/plain",
                "owners": [{"me": True, "emailAddress": "owner@example.com"}],
                "visibility": "private",
                "modifiedTime": datetime.utcnow().isoformat(),
            }
        ],
        "nextPageToken": None,
    }

    drive_service.sync_files()

    drive_service._repo.save_file.assert_called_once()
    drive_service._repo.save_log.assert_not_called()
    drive_service._mail.send.assert_not_called()


def test_sync_files_no_files_returned(drive_service):
    drive_service._drive.list_files.return_value = {
        "files": [],
        "nextPageToken": None,
    }

    drive_service.sync_files()

    drive_service._repo.save_file.assert_not_called()
    drive_service._repo.save_log.assert_not_called()
    drive_service._mail.send.assert_not_called()


def test_sync_files_update_file(drive_service):
    modified_time = datetime.utcnow().isoformat()
    drive_service._drive.list_files.return_value = {
        "files": [
            {
                "id": "1",
                "name": "Test File",
                "mimeType": "text/plain",
                "owners": [{"me": True, "emailAddress": "owner@example.com"}],
                "visibility": "private",
                "modifiedTime": modified_time,
            }
        ],
        "nextPageToken": None,
    }

    drive_service._repo.save_file.side_effect = FileAlreadySavedException

    drive_service._repo.get_file_by.return_value = {
        "id": "1",
        "name": "Old File",
        "mimeType": "text/plain",
        "owner": "owner@example.com",
        "visibility": "private",
        "modified_time": "old_time",
    }

    drive_service.sync_files()

    drive_service._repo.save_file.assert_called_once()
    drive_service._repo.save_log.assert_not_called()
    drive_service._mail.send.assert_not_called()


def test_sync_files_change_visibility(drive_service):
    modified_time = datetime.utcnow().isoformat()
    drive_service._drive.list_files.return_value = {
        "files": [
            {
                "id": "1",
                "name": "Test File",
                "mimeType": "text/plain",
                "owners": [{"me": True, "emailAddress": "owner@example.com"}],
                "permissions": [{"id": "anyoneWithLink", "type": "anyone"}],
                "visibility": "public",
                "modifiedTime": modified_time,
            }
        ],
        "nextPageToken": None,
    }

    drive_service._repo.get_file_by.return_value = {
        "id": "1",
        "name": "Test File",
        "mimeType": "text/plain",
        "owner": "owner@example.com",
        "visibility": "public",
        "modified_time": modified_time,
    }

    drive_service.sync_files()

    drive_service._drive.remove_permission.assert_called()
    drive_service._mail.send.assert_called_once()
    drive_service._repo.save_file.assert_called()
    drive_service._repo.save_log.assert_called()
