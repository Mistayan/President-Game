# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/15/22
"""
from __future__ import annotations

from typing import Final

from models import root_logger
from models.utils import SerializableClass


class Message(SerializableClass):
    timeout: Final = 40  # seconds


# DO NOT EDIT CLASSES BELOW (unless you change code accordingly)!
# Game will fail


class MessageError(Exception):

    def __init__(self, msg):
        root_logger.critical(f"{msg}")
        raise


class RequiredName:
    REQUIRED = '<player>'  # on change, edit game's routes methods to accept the same param


class Restricted(RequiredName):
    headers = {"token": None, "player": None}
    # ROUTES = ("Play", "Give",
    #           "Connect", "Disconnect",
    #           "Start", "Update")


class GET(Message):
    methods = ("GET",)


class POST(Message):
    methods = ("POST",)


class Connect(POST, Restricted):
    request: dict = {'message': "Connect"}


class Disconnect(POST, Restricted):
    request: dict = {'message': "Disconnect"}


class Play(POST, Restricted):
    request: dict = {'message': "Play", 'plays': []}
    # POSSIBLE_VALUES = GameRules.VALUES
    # POSSIBLE_COLORS = GameRules.COLORS


class Give(POST, Restricted):
    request: dict = {'message': "Give", 'plays': []}
    # POSSIBLE_VALUES = GameRules.VALUES
    # POSSIBLE_COLORS = GameRules.COLORS


class Start(POST, Restricted):
    request: dict = {'message': "Start", 'rules': {}}


class Update(GET, Restricted):
    # auto-restricted for player update, not for Game
    request: dict = {'message': "Update", 'content': ''}
    # POSSIBLE_VALUES = ("Game", "Player")


class Question(GET, Restricted):
    request: dict = {'message': "Question", 'content': ''}


class Answer(POST, Restricted):
    request: dict = {'message': "Question", 'content': ''}
