from typing import Protocol, TypeVar, Generic

T = TypeVar("T")


class MessageParser(Protocol, Generic[T]):
    """
    A protocol for message parsers that can parse a message from a string.
    """

    def parse(self, message: str) -> T:
        """
        Parse a message from a string.

        Args:
            message (str): The message to parse.

        Returns:
            T: The parsed message.
        """
        ...

    def serialize(self, message: T) -> str:
        """
        Serialize a message to a string.

        Args:
            message (T): The message to serialize.

        Returns:
            str: The serialized message.
        """
        ...


U = TypeVar("U", contravariant=True)


class Producer(Protocol, Generic[U]):
    """
    A protocol for message producers that can produce messages.
    """

    def produce(self, message: U) -> None:
        """
        Produce a message to a topic.

        Args:
            message (T): The message to produce.
        """
        ...

    def flush(self) -> None:
        """
        Flush the producer, ensuring all messages are sent.
        """
        ...
