from dotenv import load_dotenv
import os
from confluent_kafka import Producer as KafkaProducerLib
from ufvrag.messenger.kafka import KafkaProducer
from ufvrag.messenger.parsers import UrlParser

load_dotenv()

def get_urls_producer() -> KafkaProducer[str]:
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
    
    return KafkaProducer[str](message_parser=url_parser, topic=topic, producer=kafka_producer)