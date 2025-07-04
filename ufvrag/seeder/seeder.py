from typing import Any
from ufvrag.config import get_urls_producer

producer = get_urls_producer()


def delivery_report(err: Exception, msg: Any) -> None:
    """
    Callback function to report the delivery status of messages.

    Args:
        err (Exception): The error if delivery failed, None if successful.
        msg (Message): The message that was delivered.
    """

    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(
            f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )


def seed_url(url: str) -> None:
    """
    Seed the starting point of the crawler with the given URL.

    Args:
        url (str): The URL to seed.
    """
    print(f"Seeding URL: {url}")
    producer.produce(url, callback=delivery_report)
    producer.flush()
    print("URL seeding complete.")
