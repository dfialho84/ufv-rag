from typing import Any, Iterable, Optional, Protocol

from ufvrag.models import Url


class UrlRepository(Protocol):
    def find_by_url(self, url: str) -> Optional[Url]:
        """
        Check if a URL exists in the repository.

        Args:
            url (str): The URL to check.

        Returns:
            Optional[Url]: The Url object if it exists, None otherwise.
        """
        ...

    def find_by_digest(self, digest: str) -> Optional[Url]:
        """
        Check if a URL with the specified digest exists in the repository.

        Args:
            digest (str): The digest to check.

        Returns:
            Optional[Url]: The Url object if it exists, None otherwise.
        """
        ...

    def get_urls_list(self, **kwargs: Any) -> Iterable[Url]:
        """
        Get the list of URLs according to kwargs filter

        Args:
            kwargs (): dict of filters
        """
        ...

    def insert(self, url: Url) -> bool:
        """
        Insert a new URL into the repository.

        Args:
            url (Url): The Url object to insert.

        Returns:
            bool: True if the URL was inserted successfully, False otherwise.
        """
        ...

    def update(self, url: Url) -> bool:
        """
        Update an existing URL in the repository.

        Args:
            url (Url): The Url object to update.

        Returns:
            bool: True if the URL was updated successfully, False otherwise.
        """
        ...
