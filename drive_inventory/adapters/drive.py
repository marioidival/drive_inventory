import abc


class AbstractDrive(abc.ABC):
    @abc.abstractmethod
    def list_files(self, page_token):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_permission(self, file_id, permission_id):
        raise NotImplementedError


class DriveAdapter(AbstractDrive):
    def __init__(self, service):
        self.service = service

    def list_files(self, page_token=None, page_size=50):
        results = (
            self.service.files()
            .list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, owners, permissions, sharingUser, fileExtension, modifiedTime, mimeType, md5Checksum)",
                pageToken=page_token,
                corpora="user",
            )
            .execute()
        )
        return results

    def remove_permission(self, file_id, permission_id):
        try:
            self.service.permissions().delete(
                fileId=file_id,
                permissionId=permission_id,
            ).execute()
        except Exception as e:
            print(f"failed to remove the permission: {e}")
