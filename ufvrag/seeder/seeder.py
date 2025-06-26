from ufvrag.config import create_urls_producer

producer = create_urls_producer()


def seed_url(url: str) -> None:
    """
    Seed the starting point of the crawler with the given URL.

    Args:
        url (str): The URL to seed.
    """
    print(f"Seeding URL: {url}")
    producer.produce(url)
    producer.flush()
    print("URL seeding complete.")
