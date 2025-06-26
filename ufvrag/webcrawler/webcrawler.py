import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from ufvrag.config.repository_config import url_repository
from ufvrag.models import Url
from typing import Final
from dotenv import load_dotenv
import os

load_dotenv()

domains_to_crawl: list[str] = os.getenv("DOMAINS_TO_CRAWL", "").split(",")


@dataclass
class CrawlResponse:
    url_for_embbeding: Optional[str] = None
    links: Optional[Iterable[str]] = None


EMPTY_CRAWL_RESPONSE: Final[CrawlResponse] = CrawlResponse()

# Tipos considerados "html-like"
html_like_types = [
    "text/html",
    "application/xhtml+xml",
    "application/x-javascript",  # raramente usado
    "application/javascript",
    "application/x-httpd-php",  # para servidores que ainda o usam
]


def is_html_like(content_type: str) -> bool:
    """
    Check if the content type of the URL is HTML-like.
    Args:
        content_type (str): The content type to check.
    Returns:
        bool: True if the content type is HTML-like, False otherwise.
    """
    ct = content_type.lower()
    return any(t in content_type for t in html_like_types)


def checksum(content: str) -> str:
    """
    Generate a checksum for the given content.

    Args:
        content (str): The content to generate a checksum for.

    Returns:
        str: The checksum of the content.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def belong_to_domain(url: str, domain: str) -> bool:
    """
    Check if the URL belongs to the given domain.

    Args:
        url (str): The URL to check.
        domain (str): The domain to check against.

    Returns:
        bool: True if the URL belongs to the domain, False otherwise.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        return hostname is not None and hostname.endswith(domain)
    except Exception:
        return False


def is_in_db(url: Url) -> bool:
    """
    Check if the url (or another one with the same content) if already in database.

    Args:
        url (Url): The URL to check.

    Returns:
        bool: True if the Url is the db, False otherwise.
    """
    if url.digest is not None and url_repository.find_by_digest(url.digest) is not None:
        return True
    if url_repository.find_by_url(url.url) is not None:
        return True

    return False


def is_embeddabble(content_type: str) -> bool:
    """
    Check if the content type is embbeddable.

    Args:
        content_type (str): The Content Type.

    Returns:
        bool: True if the Content Type is Embeddable
    """
    return content_type.lower() in html_like_types or content_type in (
        "application/pdf"
    )


def should_be_embedded(url: Url) -> bool:
    """
    Check if the url should be embedded.

    Args:
        url (Url): The URL to check.

    Returns:
        bool: True if the Url should be embedded, False otherwise.
    """
    if is_in_db(url=url):
        return False

    if url.content_type is None:
        return False

    return is_embeddabble(url.content_type)


def look_for_links(url: str, content: str) -> list[str]:
    """
    Look for links in the given URL.

    Args:
        url (str): The URL to look for links.

    Returns:
        list[str]: A list of links found in the URL.
    """
    try:
        soup = BeautifulSoup(content, "html.parser")
        links: list[str] = []
        for a_tag in soup.find_all("a", href=True):
            if not isinstance(a_tag, Tag):
                continue
            href = a_tag.get("href")
            if not isinstance(href, str):
                continue
            link: str = urljoin(url, href)
            if not link.startswith("http"):
                continue
            belong = any(belong_to_domain(link, domain) for domain in domains_to_crawl)
            if not belong:
                print(f"\tURL {link} does not belong domains list, skipping.")
                continue
            if link == url:
                continue
            if url_repository.find_by_url(link) is not None:
                continue
            links.append(link)
        return links
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return []


def crawl_url(url: str) -> CrawlResponse:
    print(f"Crawling URL: {url}")
    if url_repository.find_by_url(url) is not None:
        print(f"\tURL {url} already in database. Skipping")
        return EMPTY_CRAWL_RESPONSE
    try:
        url_for_emebedding: Optional[str] = None

        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses

        digest = checksum(response.text)
        content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
        url_object = Url(
            url=url,
            digest=digest,
            content_type=content_type,
            ingestion_time=datetime.now(),
        )

        if is_in_db(url=url_object):
            print(f"\tUrl {url} is already in Database")
            if url_repository.find_by_url(url) is None:
                url_object.loaded = True
                url_repository.insert(url=url_object)
        else:
            print(f"\tSaving URL {url} in database")
            url_repository.insert(url=url_object)
            url_for_emebedding = url

        if not is_html_like(content_type=content_type):
            print(f"\t *** URL {url} is not HTML-like, skipping. ***")
            if should_be_embedded(url_object):
                return CrawlResponse(url_for_embbeding=url_for_emebedding)
            else:
                return EMPTY_CRAWL_RESPONSE

        links = look_for_links(url=url, content=response.text)
        return CrawlResponse(url_for_embbeding=url_for_emebedding, links=links)
    except requests.RequestException as e:
        print(f"\tErro ao acessar {url}: {e}")
        return EMPTY_CRAWL_RESPONSE
