from dataclasses import asdict
from datetime import datetime, timezone
from drive_inventory.adapters.drive import AbstractDrive
from drive_inventory.adapters.notifications import AbstractNotifications
from drive_inventory.adapters.repository import (
    AbstractRepository,
    MongoRepository,
    FileAlreadySavedException,
)
from drive_inventory.domain.model import File, Log


class DriveService:
    def __init__(
        self,
        drive_adapter: AbstractDrive,
        mail_adapter: AbstractNotifications,
        db_adapter: AbstractRepository = MongoRepository(),
    ) -> None:
        self._drive = drive_adapter
        self._mail = mail_adapter
        self._repo = db_adapter

    def sync_files(self):
        next_page = None
        while True:
            for opts in self._process_files(next_page):
                file, permissions, next_page_token = opts
                next_page = next_page_token

                try:
                    self._repo.save_file(asdict(file))
                except FileAlreadySavedException:
                    to_update = self._repo.get_file_by(
                        {
                            "external_id": file.external_id,
                            "updated_at": {"$ne": file.updated_at},
                        },
                    )
                    if to_update:
                        query = {"externar_id": file.external_id}
                        self._repo.update_file(query, asdict(file))
                finally:
                    if file.visibility == "public" and file.owned_by_me:
                        for perm in permissions:
                            if perm["type"] == "anyone":
                                self.make_file_private(file, perm["id"])
                                break

            if next_page is None:
                print("finished fetch files")
                break

    def make_file_private(self, file, permission_id):
        self._drive.remove_permission(file.external_id, permission_id)

        self._repo.update_file(
            {"external_id": file.external_id},
            {"visibility": "private"},
        )

        self._mail.send(
            file.owner_file,
            "InventoryPy - notice about file visibility",
            f"The file {file.filename} visibility was changed to private",
        )

        self._repo.save_log(
            asdict(
                Log(
                    file_id=file.external_id,
                    changes={"visibility": ["public", "private"]},
                    timestamp=self._get_timestamp(),
                )
            )
        )

    def _get_timestamp(self):
        current_time = datetime.now(timezone.utc)
        formatted_time = current_time.isoformat(timespec="milliseconds")
        formatted_time_with_z = formatted_time.replace("+00:00", "Z")
        return formatted_time_with_z

    def _process_files(self, next_page_token=None):
        results = self._drive.list_files(next_page_token)
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return

        for item in items:
            file = File(
                external_id=item["id"],
                filename=item["name"],
                file_extension=item.get("fileExtension"),
                updated_at=item["modifiedTime"],
                mimetype=item.get("mimeType"),
                owned_by_me=any(owner["me"] for owner in item.get("owners", [])),
                checksum=item.get("md5Checksum"),
                visibility=(
                    "public"
                    if any(
                        p["id"] == "anyoneWithLink" for p in item.get("permissions", [])
                    )
                    else "private"
                ),
                # currently, only certain legacy files may have more than one owner.
                # I would like to take the first item on the list anyway
                owner_file=item["owners"][0]["emailAddress"],
            )

            # this will fix the issues whet a google files comes in the result
            # the idea is take the last part of mimetype and turn it as file extension for
            # google files
            if not file.file_extension:
                file.file_extension = item["mimeType"].split(".")[-1]

            permissions = []
            if file.visibility == "public":
                permissions = item.get("permissions", [])

            yield (file, permissions, results.get("nextPageToken"))
