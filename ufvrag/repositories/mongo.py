from dataclasses import asdict
from typing import Any, Iterable, Mapping, Optional, TypeGuard

from pymongo.collection import Collection

from ufvrag.models import Url

from .base import UrlRepository


def dict_to_url(d: Optional[Mapping[str, Any]]) -> Optional[Url]:
    if d is not None:
        return Url(**{k: v for k, v in d.items() if k != "_id"})
    return None


def iterable_dict_to_url(urls: Iterable[Mapping[str, Any]]) -> Iterable[Url]:
    def filter_not_none(url: Optional[Url]) -> TypeGuard[Url]:
        return isinstance(url, Url)

    return filter(filter_not_none, map(dict_to_url, urls))


class MongoUrlRepository(UrlRepository):
    """
    A MongoDB implementation of the UrlRepository protocol.
    This class provides methods to interact with a MongoDB collection for URL storage.
    """

    def __init__(self, collection: Collection[Mapping[str, Any]]) -> None:
        self.collection = collection

    def find_by_url(self, url: str) -> Optional[Url]:
        """
        Check if a URL exists in the MongoDB collection.

        Args:
            url (str): The URL to check.

        Returns:
            Optional[Url]: The Url object if it exists, None otherwise.
        """
        return dict_to_url(self.collection.find_one({"url": url}))

    def find_by_digest(self, digest: str) -> Optional[Url]:
        """
        Check if a URL with the specified digest exists in the repository.

        Args:
            digest (str): The digest to check.

        Returns:
            Optional[Url]: The Url object if it exists, None otherwise.
        """
        return dict_to_url(self.collection.find_one({"digest": digest}))

    def get_urls_list(self, **kwargs: Any) -> Iterable[Url]:
        """
        Get the list of URLs according to kwargs filter

        Args:
            kwargs (): dict of filters
        """
        print(kwargs)
        return iterable_dict_to_url(self.collection.find(kwargs))

    def insert(self, url: Url) -> bool:
        """
        Insert a new URL into the MongoDB collection.

        Args:
            url (Url): The Url object to insert.

        Returns:
            bool: True if the URL was inserted successfully, False otherwise.
        """
        if self.find_by_url(url.url) is not None:
            return False
        result = self.collection.insert_one(asdict(url))
        return result.acknowledged

    def update(self, url: Url) -> bool:
        """
        Update an existing URL in the MongoDB collection.

        Args:
            url (Url): The Url object to update.

        Returns:
            bool: True if the URL was updated successfully, False otherwise.
        """
        result = self.collection.update_one({"url": url.url}, {"$set": asdict(url)})
        return result.modified_count > 0
