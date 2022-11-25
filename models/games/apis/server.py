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

from models import root_logger
from models.games.apis import db, apis_conf  # , ma


class Server(Flask, ABC):
    # Instances Shared attributes
    # Will only be generated on first run of an instance, while GameManager runs
    _super_shared_private: Final = ''.join(random.choices(string.hexdigits, k=100))
    if not os.environ.get("SECRET_KEY"):
        os.putenv("SECRET_KEY", _super_shared_private)
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
        self.logger = logging.getLogger(__class__.__name__)
        self.name = import_name
        self.status = self.OFFLINE
        self._last_message_sent: dict = None
        self._last_message_received: dict = None
        self._messages_to_send: list[dict] = []
        self.config.setdefault("APPLICATION_ROOT", "/")
        self.config.setdefault("PREFERRED_URL_SCHEME", "https")
        self.config.setdefault("SERVER_NAME", self.name)
        self.config.setdefault("DEBUG", root_logger.level == logging.DEBUG)
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

        self.init_server(import_name)
        self.app_context().push()
        self.logger.debug("instantiated Server (requires run)")

    @abstractmethod
    def init_server(self, name):
        # migrate = Migrate()
        db.init_app(self)
        # bcrypt.init_app(self)
        # ma.init_app(self.__app)
        # migrate.init_app(self.__app, db)
        try:
            db.create_all()  # not in use ATM
        except:
            pass
        # self.__cors = CORS(self.__app, resources={r"/*": {"origins": "*"}})

    def run_server(self, port: int):
        """ Emulate server running to accept connexions """
        self.status = self.STARTING
        try:
            self.status = self.PROCESSING
            ...
            self.status = self.SERVER_RUNNING
            self.run("localhost", port)

        except KeyboardInterrupt:
            self.status = self.OFFLINE
            self.logger.critical(f"Closing Server {self.name}...")

        # except Exception as e:
        #     print(f'nope {e}')

    @abstractmethod
    def send(self, destination, msg):
        """ check file integrity before you can send """
        assert msg and destination
        self.logger.debug(f"Preparing : {msg} for {destination}")
        self._last_message_sent = msg
        pass

    @abstractmethod
    def receive(self, msg: dict):
        assert isinstance(msg, dict) and msg.get("message") \
               and msg.get("player")
        self.logger.info(f"Receiving : {msg}")
        self._last_message_received = msg
        pass

    @abstractmethod
    def to_json(self):
        # su = super(Server, self).to_json()
        update = {
            'name': self.name,
            'status': self.status,
            'messages': self._messages_to_send,  # messages for everyone
        }
        # su.update(update)
        return update
