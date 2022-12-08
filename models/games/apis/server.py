# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/17/22
"""
import logging
import os
import random
import string
from abc import ABC, abstractmethod
from typing import Final

# import CORS as CORS
# import Migrate as Migrate
from flask import Flask

from models import ROOT_LOGGER
from models.games.apis import apis_conf  # , ma
from models.games.apis.apis_conf import SERVER_HOST
from models.utils import GameFinder


class Server(Flask, ABC):
    """ Base class handling Flask Server

    """
    # Instances Shared attributes
    # Will only be generated on first run of an instance, while GameManager runs
    _SUPER_PRIVATE: Final = os.getenv('SECRET_KEY',
                                      ''.join(random.choices(string.hexdigits, k=100)))
    if not os.environ.get("SECRET_KEY"):
        os.putenv("SECRET_KEY", _SUPER_PRIVATE)
    _SECRET_KEY = os.environ.get("SECRET_KEY")

    # Internal status
    _PROTOCOL = "http"
    OFFLINE = 0
    STARTING = 10
    SERVER_RUNNING = 200
    GAME_RUNNING = 230
    PROCESSING = 300
    ERROR = 400
    CRITICAL = 500

    @abstractmethod
    def __init__(self, import_name: str, *args):
        super().__init__(import_name)
        self.local_process = None
        self.logger = logging.getLogger(__class__.__name__)
        self.name = import_name
        self.status = self.OFFLINE
        self._last_message_sent: dict = None
        self._last_message_received: dict = None
        self._messages_to_send: list[dict] = []
        self.config.setdefault("APPLICATION_ROOT", "/")
        self.config.setdefault("PREFERRED_URL_SCHEME", "https")
        self.config.setdefault("SERVER_NAME", self.name)
        self.config.setdefault("DEBUG", ROOT_LOGGER.level == logging.DEBUG)
        self.config.setdefault("SECRET_KEY", self._SECRET_KEY)
        self.config.setdefault("CORS_HEADER", 'Content-Type')
        self.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", True)
        self.config.setdefault("SQLALCHEMY_DATABASE_URI", f"{apis_conf.DB_TYPE}:"
                                                          f"//{apis_conf.DATABASE_USER}:"
                                                          f"{apis_conf.DATABASE_PASS}"
                                                          f"@{apis_conf.DATABASE_HOST}:"
                                                          f"{apis_conf.DATABASE_PORT}"
                                                          f"/{self.import_name}" \
            if apis_conf.DB_TYPE != "sqlite" else \
            'sqlite:///' + os.path.join(apis_conf.BASEDIR, self.name))

        self._init_server(import_name)
        self.app_context().push()
        self.logger.debug("instantiated Server (requires run)")

    @abstractmethod
    def _init_server(self, name):
        """ base method to initialize various securities to Flask server, before running """
        # migrate = Migrate()
        # db.init_app(self)
        # bcrypt.init_app(self)
        # ma.init_app(self.__app)
        # migrate.init_app(self.__app, db)
        # try:
        #     db.create_all()  # not in use ATM
        # except:
        #     pass
        # self.__cors = CORS(self.__app, resources={r"/*": {"origins": "*"}})

    def run_server(self, port: int = 0):
        """ Emulate server running to accept connexions """
        self.status = self.STARTING
        host, port = None, None
        try:
            self.status = self.PROCESSING
            finder = GameFinder(target=apis_conf.SERVER_HOST, port=port)
            if not finder.availabilities:
                self.logger.critical("No open ports found. Please free one of those :")
                self.logger.critical(finder.running_servers)
                raise ConnectionError()

            host, port = finder.availabilities[0]
            self.status = self.SERVER_RUNNING
            self.run(SERVER_HOST, port)
        except KeyboardInterrupt:
            self.status = self.OFFLINE
            self.logger.critical("Closing Server %s...", self.name)

        # except Exception as e:
        #     print(f'nope {e}')

    @abstractmethod
    def _send(self, destination, msg):
        """ check file integrity before you can _send """
        if not (msg and destination):
            return
        self.logger.debug("Preparing : %s for %s", msg, destination)
        self._last_message_sent = msg

    @abstractmethod
    def receive(self, msg: dict):
        """ base method to verify content of a received message, before you can process it"""
        assert isinstance(msg, dict) and msg.get("message") \
               and msg.get("player")
        self.logger.info("Receiving : %s", msg)
        self._last_message_received = msg

    @abstractmethod
    def to_json(self):
        """ Serializing method for exchanges between Server and players"""
        # su = super(Server, self).to_json()
        return {
            'name': self.name,
            'status': self.status,
            'messages': self._messages_to_send,  # messages for everyone
        }
