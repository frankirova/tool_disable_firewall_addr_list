"""MongoDB adapter — persists option IPs via the OptionsRepository port."""

from __future__ import annotations

from pymongo import MongoClient

from refactor.core.interfaces import OptionsRepository
from refactor.core.config import config


class MongoOptionsRepository(OptionsRepository):
    """Stores/fetches option IPs from a MongoDB collection."""

    def __init__(self) -> None:
        self._client: MongoClient | None = None

    def _get_collection(self):
        if self._client is None:
            self._client = MongoClient(config.mongo_uri)
        db = self._client[config.mongo_db_name]
        return db[config.mongo_collection_options]

    async def add(self, option: str) -> None:
        self._get_collection().insert_one({"option": option})

    async def add_many(self, options: list[str]) -> None:
        coll = self._get_collection()
        for opt in options:
            coll.insert_one({"option": opt})

    async def get_all(self) -> list[str]:
        coll = self._get_collection()
        return [doc["option"] for doc in coll.find()]

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
