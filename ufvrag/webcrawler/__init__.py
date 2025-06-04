import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse
import hashlib

from ufvrag.config.repository_config import url_repository

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


def url_has_changed(url: str, content: str) -> bool:
    """
    Check if the URL has changed by comparing its checksum.

    Args:
        url (str): The URL to check.
        content (str): The content of the URL to compare against.

    Returns:
        bool: True if the URL has changed, False otherwise.
    """
    existing_url = url_repository.find_by_url(url)
    if existing_url is None:
        return True  # URL does not exist, so it has changed

    existing_checksum = existing_url.get("digest")
    if existing_checksum is None:
        return True  # No checksum stored, so it has changed

    new_checksum = checksum(content)
    return new_checksum != existing_checksum


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


def look_for_links(url: str) -> list[str]:
    """
    Look for links in the given URL.

    Args:
        url (str): The URL to look for links.

    Returns:
        list[str]: A list of links found in the URL.
    """

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses

        if not url_has_changed(url, response.text):
            print(f"URL {url} has not changed, skipping.")
            return []

        if not url_repository.find_by_url(url):
            url_repository.insert({"url": url, "digest": checksum(response.text)})
        else:
            url_repository.update({"url": url, "digest": checksum(response.text)})

        content_type = response.headers.get("Content-Type", "")
        if not is_html_like(content_type=content_type):
            print(f"URL {url} is not HTML-like, skipping.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links: list[str] = []
        for a_tag in soup.find_all("a", href=True):
            if not isinstance(a_tag, Tag):
                continue
            href = a_tag.get("href")
            if not isinstance(href, str):
                continue
            link: str = urljoin(url, href)
            if not belong_to_domain(link, ".ufv.br"):
                print(f"URL {link} does not belong to ufv.br, skipping.")
                continue
            links.append(link)
        return links
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return []
