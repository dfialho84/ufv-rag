from typing import TypeVar, Generic, Callable, Any, Optional
from abc import abstractmethod, ABC

T = TypeVar('T')


class MessageParser(ABC, Generic[T]):
    """
    A protocol for message parsers that can parse a message from a string.
    """

    @abstractmethod 
    def parse(self, message: str) -> T:
        """
        Parse a message from a string.

        Args:
            message (str): The message to parse.

        Returns:
            T: The parsed message.
        """
        ...

    @abstractmethod
    def serialize(self, message: T) -> str:
        """
        Serialize a message to a string.

        Args:
            message (T): The message to serialize.

        Returns:
            str: The serialized message.
        """
        ...


U = TypeVar('U', contravariant=True)
ProducerCallback = Optional[Callable[[Exception, Any], None]]

class Producer(ABC, Generic[U]):
    """
    A protocol for message producers that can produce messages.
    """

    @abstractmethod
    def produce(self, message: U, callback: ProducerCallback = None) -> None:
        """
        Produce a message to a topic.

        Args:
            message (T): The message to produce.
        """
        ...

    @abstractmethod
    def flush(self) -> None:
        """
        Flush the producer, ensuring all messages are sent.
        """
        ...

