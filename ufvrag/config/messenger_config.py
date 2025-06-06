from dotenv import load_dotenv
import os
from confluent_kafka import Producer as KafkaProducerLib, Consumer as KafkaConsumerLib
from ufvrag.messenger.base import Consumer, Producer
from ufvrag.messenger.kafka import KafkaProducer, KafkaConsumer
from ufvrag.messenger.parsers import UrlParser

load_dotenv()


def create_urls_producer() -> Producer[str]:
    """
    Get a Kafka producer for URLs.

    Returns:
        KafkaProducer[str]: A Kafka producer configured for URLs.
    """

    conf = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    }

    kafka_producer = KafkaProducerLib(conf)
    url_parser = UrlParser()
    topic = os.getenv("KAFKA_URLS_TOPIC")
    if not topic:
        raise ValueError("KAFKA_URLS_TOPIC environment variable is not set.")

    return KafkaProducer[str](
        message_parser=url_parser, topic=topic, producer=kafka_producer
    )


def create_urls_consumer() -> Consumer[str]:
    """
    Get a Kafka consumer for URLs.

    Returns:
        KafkaConsumer[str]: A Kafka consumer configured for URLs.
    """

    conf = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        "group.id": os.getenv("KAFKA_GROUP_ID", "default_group"),
        "auto.offset.reset": "beginning",
    }

    kafka_consumer = KafkaConsumerLib(conf)
    url_parser = UrlParser()
    topic = os.getenv("KAFKA_URLS_TOPIC")
    if not topic:
        raise ValueError("KAFKA_URLS_TOPIC environment variable is not set.")

    return KafkaConsumer[str](
        message_parser=url_parser, topic=topic, consumer=kafka_consumer
    )


def create_embeddings_consumer() -> Consumer[str]:
    """
    Get a Kafka consumer for Embeddings.

    Returns:
        KafkaConsumer[str]: A Kafka consumer configured for URLs.
    """

    conf = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        "group.id": os.getenv("KAFKA_RAG_GROUP_ID", "default_group"),
        "auto.offset.reset": "beginning",
    }

    kafka_consumer = KafkaConsumerLib(conf)
    url_parser = UrlParser()
    topic = os.getenv("KAFKA_EMBEDDING_TOPIC")
    if not topic:
        raise ValueError("KAFKA_EMBEDDING_TOPIC environment variable is not set.")

    return KafkaConsumer[str](
        message_parser=url_parser, topic=topic, consumer=kafka_consumer
    )

def create_embeddings_producer() -> Producer[str]:
    """
    Get a Kafka producer for Embeddings.

    Returns:
        KafkaProducer[str]: A Kafka producer configured for URLs.
    """

    conf = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    }

    kafka_producer = KafkaProducerLib(conf)
    url_parser = UrlParser()
    topic = os.getenv("KAFKA_EMBEDDING_TOPIC")
    if not topic:
        raise ValueError("KAFKA_EMBEDDING_TOPIC environment variable is not set.")

    return KafkaProducer[str](
        message_parser=url_parser, topic=topic, producer=kafka_producer
    )
