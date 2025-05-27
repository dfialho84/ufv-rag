from .base import MessageParser

class UrlParser(MessageParser[str]):
    """
    A class to parse URLs.
    """

    def parse(self, message: str) -> str:
        return message

    def serialize(self, message: str) -> str:
        return message