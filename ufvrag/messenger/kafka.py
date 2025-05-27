from typing import TypeVar
from confluent_kafka import Producer as KafkaProducerLib
from .base import Producer, MessageParser, ProducerCallback

T = TypeVar('T')

class KafkaProducer(Producer[T]):
    """
    A Kafka producer that implements the Producer protocol.
    This class is a placeholder for Kafka producer functionality.
    """
    message_parser: MessageParser[T]
    topic: str
    producer: KafkaProducerLib

    def __init__(self, message_parser: MessageParser[T], topic: str, producer: KafkaProducerLib) -> None:
        self.message_parser = message_parser
        self.topic = topic
        self.producer = producer

    def produce(self, message: T, callback: ProducerCallback = None) -> None:
        """
        Produce a message to a Kafka topic.
        
        Args:
            message (str): The message to produce.
        """
        str_msg: str = self.message_parser.serialize(message)
        self.producer.produce(topic=self.topic, value=str_msg, callback=callback)

    def flush(self) -> None:
        """
        Flush the producer, ensuring all messages are sent.
        """
        self.producer.flush()