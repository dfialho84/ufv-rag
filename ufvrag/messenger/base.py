from types import TracebackType
from typing import TypeVar, Generic, Callable, Any, Optional, Type
from abc import abstractmethod, ABC

T = TypeVar("T")


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


U = TypeVar("U", contravariant=True)
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


class Consumer(ABC, Generic[T]):
    """
    A protocol for message consumers that can consume messages.
    """

    @abstractmethod
    def consume(self, timeout_sec: int) -> Optional[T]:
        """
        Consume a message from a topic.

        Args:
            timeout_sec (int): The timeout in seconds for consuming a message.

        Returns:
            Optional[T]: The consumed message, or None if no message was available within the timeout.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """
        Close the consumer, releasing any resources.
        """
        ...

    @abstractmethod
    def __enter__(self) -> "Consumer[T]":
        """
        Enter the context manager, returning the consumer instance.
        """
        ...

    @abstractmethod
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
        ...
