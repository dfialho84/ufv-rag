from ufvrag.models import Url
from .base import UrlRepository
from pymongo.collection import Collection


class MongoUrlRepository(UrlRepository):
    """
    A MongoDB implementation of the UrlRepository protocol.
    This class provides methods to interact with a MongoDB collection for URL storage.
    """

    def __init__(self, collection: Collection[Url]) -> None:
        self.collection = collection

    def find_by_url(self, url: str) -> Url | None:
        """
        Check if a URL exists in the MongoDB collection.

        Args:
            url (str): The URL to check.

        Returns:
            Optional[Url]: The Url object if it exists, None otherwise.
        """
        return self.collection.find_one({"url": url})

    def insert(self, url: Url) -> bool:
        """
        Insert a new URL into the MongoDB collection.

        Args:
            url (Url): The Url object to insert.

        Returns:
            bool: True if the URL was inserted successfully, False otherwise.
        """
        if self.find_by_url(url["url"]) is not None:
            return False
        result = self.collection.insert_one(url)
        return result.acknowledged

    def update(self, url: Url) -> bool:
        """
        Update an existing URL in the MongoDB collection.

        Args:
            url (Url): The Url object to update.

        Returns:
            bool: True if the URL was updated successfully, False otherwise.
        """
        result = self.collection.update_one({"url": url["url"]}, {"$set": url})
        return result.modified_count > 0
