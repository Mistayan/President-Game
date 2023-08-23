import logging
from abc import ABC, abstractmethod
from typing import Optional


class Communicant(ABC):
    DISCONNECTED = 8
    CONNECTED = 211
    WAITING_NEW_GAME = 212
    ACTION_REQUIRED = 231
    GIVE_REQUIRED = 233
    PLAY_REQUIRED = 232
    # Internal status
    _PROTOCOL = "http"
    OFFLINE = 0
    STARTING = 10
    SERVER_RUNNING = 200
    GAME_RUNNING = 230
    PROCESSING = 300
    _last_message_sent: Optional[dict] = None
    _last_message_received: Optional[dict] = None
    _messages_to_send: list[dict] = []
    __logger = logging.getLogger(__name__)
    _local_process = None

    @abstractmethod
    def __init__(self, import_name: str, *args):
        self.name = import_name

    @abstractmethod
    def _send(self, destination, msg):
        """ check file integrity before you can _send """
        if not (msg and destination):
            return
        self.__logger.debug("Preparing : %s for %s", msg, destination)
        self._last_message_sent = msg

    @abstractmethod
    def receive(self, msg: dict):
        """ base method to verify content of a received message, before you can process it"""
        assert isinstance(msg, dict) and msg.get("message") \
               and msg.get("player")
        self.__logger.info("Receiving : %s", msg)
        self._last_message_received = msg

    @abstractmethod
    def to_json(self):
        pass