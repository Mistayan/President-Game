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

from flask import Flask

import conf
from conf import ROOT_LOGGER
from models.games.apis import apis_conf  # , ma
from models.games.apis.apis_conf import SERVER_HOST
from models.networking.communicant import Communicant
from models.utils import GameFinder


class Server(Flask, Communicant, ABC):
    """ Base class handling Flask Server
        Must be inherited to implement init_server
    """
    # Instances Shared attributes
    # Will only be generated on first run of an instance, while GameManager runs
    _SUPER_PRIVATE: Final = os.getenv('SECRET_KEY',
                                      ''.join(random.choices(string.hexdigits, k=100)))
    if not os.environ.get("SECRET_KEY"):
        os.putenv("SECRET_KEY", _SUPER_PRIVATE)
    _SECRET_KEY = os.environ.get("SECRET_KEY")

    @abstractmethod
    def __init__(self, import_name: str, *args):
        super().__init__(import_name)
        self._local_process = None
        self._logger = logging.getLogger(__class__.__name__)
        self.name = import_name
        self.status = self.OFFLINE
        self.config.setdefault("APPLICATION_ROOT", "/")
        self.config.setdefault("PREFERRED_URL_SCHEME", self._PROTOCOL)
        self.config.setdefault("SERVER_HOST", SERVER_HOST)
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
            'sqlite:///' + os.path.join(conf.BASEDIR, self.name))

        self._init_server(import_name)
        self.app_context().push()
        self._logger.debug("instantiated Server (requires run)")

    @abstractmethod
    def _init_server(self, name):
        """ base method to initialize various securities to Flask server, before running """
        pass

    @abstractmethod
    def to_json(self):
        """ Serializing Server's infos for exchanges between Server and players"""
        return {
            'name': self.name,
            'status': self.status,
            'messages': self._messages_to_send,  # messages for everyone
        }

    def run_server(self):
        """ Emulate server running to accept connexions """
        self.status = self.STARTING
        host, port = None, None
        try:
            self.status = self.PROCESSING
            finder = GameFinder(target=apis_conf.SERVER_HOST, port=port)
            if not finder.availabilities:
                self._logger.critical("No open ports found. Please free one of those :")
                self._logger.critical(finder.running)
                raise ConnectionError()

            host, port = finder.availabilities[0]
            self.status = self.SERVER_RUNNING
            self._logger.info("starting server %s on %s:%s", self.name, host, port)
            self.run(SERVER_HOST, port)
        except KeyboardInterrupt:
            self.status = self.OFFLINE
            self._logger.critical("Closing Server %s...", self.name)

    def _send(self, player, msg):
        """
        Sends a message to a given player.
        :param player: the player to send the message to
        :param msg: the message to send
        """
        player.messages.append(msg)

    def receive(self, msg: dict):
        """
        Receives a message and applies it to the game if valid.
        :param msg: the message to receive
        """
        # log message depending on its type
        if msg["message"] == "Info":
            self._logger.info(msg["content"])
        elif msg["message"] == "Error":
            self._logger.error(msg["content"])
        elif msg["message"] == "Warning":
            self._logger.warning(msg["content"])
