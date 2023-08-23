# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/15/22
"""
from __future__ import annotations

from typing import Final

from conf import ROOT_LOGGER
from models.utils import SerializableClass


class Message(SerializableClass):
    """ Base class for messages templates """
    TIMEOUT: Final = 40  # seconds


# DO NOT EDIT CLASSES BELOW (unless you change code accordingly)!
# Game will fail


class MessageError(Exception):
    """ Base Exception for Messages Errors """
    def __init__(self, msg):
        ROOT_LOGGER.critical(f"{msg}")
        # Non blocking Error ?


class RequiredName:
    """ Base class for Messages restrictions in communications """
    REQUIRED = '<player>'  # on change, edit game's routes methods to accept the same param


class Restricted(RequiredName):
    """ Defines Messages base-headers for restricted access """
    headers = {"token": None, "player": None}
    # ROUTES: ("Play", "Give",
    #          "Connect", "Disconnect",
    #          "Start", "Update")


class GET(Message):
    """ Defines method GET as a class"""
    methods = ("GET",)


class POST(Message):
    """ Defines method POST as a class"""
    methods = ("POST",)


class Connect(POST, Restricted):
    """ Defines Connect Message as a class"""
    request: dict = {'message': "Connect"}


class Disconnect(POST, Restricted):
    """ Defines Disconnect Message as a class"""
    request: dict = {'message': "Disconnect"}


class Play(POST, Restricted):
    """ Defines Connect Play as a class"""
    request: dict = {'message': "Play", 'plays': []}
    # POSSIBLE_VALUES = GameRules.VALUES
    # POSSIBLE_COLORS = GameRules.COLORS


class Give(POST, Restricted):
    """ Defines Give Message as a class"""
    request: dict = {'message': "Give", 'plays': []}
    # POSSIBLE_VALUES: GameRules.VALUES
    # POSSIBLE_COLORS: GameRules.COLORS


class Start(POST, Restricted):
    """ Defines Start Message as a class"""
    request: dict = {'message': "Start", 'rules': {}}


class Update(GET, Restricted):
    """ Defines Update Message as a class"""
    # auto-restricted for player update, not for Game
    request: dict = {'message': "Update", 'content': ''}
    # POSSIBLE_VALUES = ("Game", "Player")


class GameUpdate(POST, Restricted):
    """ Defines Update Message as a class"""
    # auto-restricted for player update, not for Game
    request: dict = {'message': "GameUpdate", 'content': ''}
    # POSSIBLE_VALUES = ("Game", "Player")


class Question(GET, Restricted):
    """ Defines Question Message as a class to wait for an answer """
    request: dict = {'message': "Question", 'content': ''}


class Answer(POST, Restricted):
    """ Defines Answer Message as a class in response to a question """
    request: dict = {'message': "Question", 'content': ''}


class AnomalyDetected(POST, Restricted):
    """ Defines Anomaly Message as a class to report anomalies detected in every instances communicating with server """
    request: dict = {'message': 'Report', 'anomaly': dict}
