from typing import Any
import asyncio
import random
from ufvrag.config import create_urls_producer, create_urls_consumer
from ufvrag.webcrawler import look_for_links

producer = create_urls_producer()
consumer = create_urls_consumer()


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


async def process_message(msg: str) -> None:
    """Simula processamento assíncrono de um item"""
    # tempo = random.uniform(1, 3)  # Simula tempo variável
    print(f"Iniciando processamento do item {msg})")
    # await asyncio.sleep(tempo)
    links = look_for_links(msg)
    for link in links:
        print(f"Link encontrado: {link}")
        producer.produce(link, callback=delivery_report)
    print(f"Finalizando processamento do item {msg})")
    # print(f"✓ Item {msg} processado em {tempo:.1f}s")


async def consume_messages() -> None:
    print("Waiting for messages to be consumed...")
    with consumer as consumer_instance:
        try:
            while True:
                msg = consumer_instance.consume(10)
                if msg:
                    print(f"Consumed message: {msg}")
                    asyncio.create_task(process_message(msg))
                else:
                    print("No messages consumed.")
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass


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
    asyncio.run(consume_messages())
