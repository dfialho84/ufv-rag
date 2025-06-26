from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Url:
    """A simple URL class to hold the URL string."""

    url: str
    digest: Optional[str] = None
    content_type: Optional[str] = None
    ingestion_time: Optional[datetime] = None
    loaded: Optional[bool] = None

    # def __str__(self) -> str:
    #     return self.url
