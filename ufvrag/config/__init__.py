from confluent_kafka import Producer as KafkaProducerLib
from ufvrag.messenger.kafka import KafkaProducer
from ufvrag.messenger.parsers import UrlParser



def get_urls_producer() -> KafkaProducer[str]:
    """
    Get a Kafka producer for URLs.

    Returns:
        KafkaProducer[str]: A Kafka producer configured for URLs.
    """

    conf = {
        "bootstrap.servers": "localhost:9092",
    }
    
    kafka_producer = KafkaProducerLib(conf)
    url_parser = UrlParser()
    
    return KafkaProducer[str](message_parser=url_parser, topic="urls", producer=kafka_producer)