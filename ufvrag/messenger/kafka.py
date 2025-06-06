import time
from types import TracebackType
from typing import TypeVar, Optional, Type
from confluent_kafka import (
    Producer as KafkaProducerLib,
    Consumer as KafkaConsumerLib,
    Message as KafkaMessage,
)
from .base import Producer, MessageParser, ProducerCallback, Consumer

T = TypeVar("T")


class KafkaProducer(Producer[T]):
    """
    A Kafka producer that implements the Producer protocol.
    This class is a placeholder for Kafka producer functionality.
    """

    message_parser: MessageParser[T]
    topic: str
    producer: KafkaProducerLib

    def __init__(
        self, message_parser: MessageParser[T], topic: str, producer: KafkaProducerLib
    ) -> None:
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
        while True:
            try:
                print(f"Producing: {str_msg}")
                self.producer.produce(
                    topic=self.topic, value=str_msg, callback=callback
                )
                break
            except Exception as e:
                print(e)
                time.sleep(2)

    def flush(self) -> None:
        """
        Flush the producer, ensuring all messages are sent.
        """
        self.producer.flush()


class KafkaConsumer(Consumer[T]):
    """
    A Kafka consumer that implements the Consumer protocol.
    This class is a placeholder for Kafka consumer functionality.
    """

    message_parser: MessageParser[T]
    topic: str
    consumer: KafkaConsumerLib

    def __init__(
        self,
        message_parser: MessageParser[T],
        topic: str,
        consumer: KafkaConsumerLib,
    ) -> None:
        self.message_parser = message_parser
        self.topic = topic
        self.consumer = consumer

    def consume(self, timeout_sec: int) -> Optional[T]:
        """
        Consume a message from a topic.

        Args:
            timeout_sec (int): The timeout in seconds for consuming a message.

        Returns:
            Optional[T]: The consumed message, or None if no message was available within the timeout.
        """
        msg: KafkaMessage = self.consumer.poll(timeout_sec)
        if msg is None:
            return None
        if msg.error():
            return None
        return self.message_parser.parse(msg.value().decode("utf-8"))

    def close(self) -> None:
        """
        Close the consumer, releasing any resources.
        """
        self.consumer.close()

    def __enter__(self) -> "KafkaConsumer[T]":
        """
        Enter the context manager, returning the consumer instance.
        """
        self.consumer.subscribe([self.topic])
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """
        Exit the context manager, handling any exceptions that occurred.

        Args:
            exc_type (Optional[Type[BaseException]]): The type of the exception, if any.
            exc_value (Optional[BaseException]): The value of the exception, if any.
            traceback (Optional[TracebackType]): The traceback of the exception, if any.

        Returns:
            Optional[bool]: Whether to suppress the exception.
        """
        self.close()
        if exc_value:
            return False
        return True
