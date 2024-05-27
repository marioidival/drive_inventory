import abc

from pymongo import MongoClient, TEXT
from pymongo.errors import DuplicateKeyError

from drive_inventory.domain import model
from drive_inventory.config import get_mongodb_uri


class FileAlreadySavedException(Exception):
    pass


class AbstractRepository(abc.ABC):
    def save_file(self, item):
        try:
            self._add("files", item)
        except DuplicateKeyError:
            raise FileAlreadySavedException

    def update_file(self, query, item):
        self._update("files", query, item)

    def save_log(self, item):
        self._add("logs", item)

    def get_file_by(self, query):
        return self._get("files", query)

    @abc.abstractmethod
    def _add(self, collection, item):
        raise NotImplementedError

    @abc.abstractmethod
    def _update(self, collection, query, item):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, collection, query):
        raise NotImplementedError


class MongoRepository(AbstractRepository):
    def __init__(self, uri: str = get_mongodb_uri()) -> None:
        self.client = MongoClient(uri)
        self.db = self.client.inventorypy

        self._create_indexes()

        super().__init__()

    def _create_indexes(self):
        self.db.files.create_index([("external_id", TEXT)], unique=True)

    def _add(self, collection, item):
        self.db[collection].insert_one(item)

    def _update(self, collection, query, item):
        self.db[collection].update_one(query, {"$set": item})

    def _get(self, collection, query):
        return self.db[collection].find_one(query)
