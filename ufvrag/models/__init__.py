from typing import Optional, TypedDict


class Url(TypedDict):
    """A simple URL class to hold the URL string."""

    url: str
    digest: Optional[str]
