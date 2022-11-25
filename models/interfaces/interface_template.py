# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import functools
import logging
from json import JSONDecodeError

import requests

from models.players.player import Human
from models.games.apis.server import Server
from models.responses import *  # over 5 modules, and less than 20% unused, it's permitted
from models.utils import ValidateBuffer, GameFinder


class Interface(Server):
    """
    Instantiate basics for Game interfaces
    """

    DISCONNECTED = 8
    CONNECTED = 10
    WAITING_NEW_GAME = 12
    ACTION_REQUIRED = 21
    PLAY_REQUIRED = 22
    GIVE_REQUIRED = 23

    def __init__(self, player: Human):
        super().__init__("Player_Interface")
        self.__token = None
        self.__msg_buffer = None
        self.__game_dict = None
        self.logger = logging.getLogger(__class__.__name__)
        self.__game = None
        self.__player: Human = player

        # another way to establish a property; bad practice ;)

    @property
    def action_required(self):
        return self.__player.action_required

    @property
    def game_dict(self):
        return self.__game_dict

    def connect(self, uri: str, port: int):
        """ Set a connection to Game """
        assert uri and type(uri) is str
        assert port and type(port) is int
        self.__msg_buffer = Connect
        self.__msg_buffer.request.setdefault("player", self.__player.name)
        response = self.send(destination=f"{uri}:{port}")  # first time require destination
        if response:
            if response.status_code == 200:
                self.status = self.CONNECTED
                self.__game = f"{uri}:{port}"  # If succeeded, we know the game exists
            self.logger.debug(response.headers)
            if response.headers.get('token') != self.__token:
                self.__update_token(response.headers.get('token'))
                assert self.__token == response.headers.get('token')
        self.logger.debug(self.__token)
        return response

    def disconnect(self):
        """ Disconnect from the Game """
        if not self.__game:
            return
        self.__msg_buffer = Disconnect
        if self.send().status_code == 200:
            self.status = self.CONNECTED

    @property
    def game_addr(self):
        return self.__game

    @property
    def game_token(self):
        return self.__token

    def receive(self, msg: dict):
        return super().receive(msg)

    def send(self, destination=None, msg=None):
        """
        Send messages to game
        Everytime the game wants to send a message, we have to retrieve those by updating
        """
        target = destination or self.__game
        super(Interface, self).send(target, self.__msg_buffer)
        message = self.__msg_buffer()
        message_method, *others = message.methods
        message.request = self._fill_request(message, self.__player, self.__token)
        self.logger.debug(f"{message_method} : {message.request}")
        self.logger.info(f"sending {message.__class__.__name__} request to {target}")
        response = requests.request(
            method=message_method,
            url=f"{self._PROTOCOL}://{target}/{message.request['message']}/{self.__player.name}",
            headers=message.headers,
            cert=None,  # yet...
            json=message.to_json(),
        )
        return response

    @ValidateBuffer
    def __apply_message(self, msg):  # WIP
        """
        Whenever we receive a message, we are required to apply it
        """
        msg_test = msg.copy()
        match self.__msg_buffer["action"]:
            case "Play":
                self.__msg_buffer.setdefault("action", self.__player.play(msg['required_cards']))
            case "Give":
                self.__msg_buffer.setdefault("action", self.__player.choose_cards_to_give())
            case "Info":
                print(self.__msg_buffer["message"])
            case _:
                raise MessageError(f"Non of the given message is valid: {self.__msg_buffer}")
        return self.send()

    @staticmethod
    def _fill_request(msg: SerializableClass, player, token) -> dict:
        """
        Complete 'msg.request' with required information
        :param msg: Any Message class
        :param player: player sending message
        :param token: interface's token
        :return:
        """
        # instantiate message buffer to memory, so any modification is not in file
        _j = msg.to_json()
        _request = _j.get("request")
        _request["player"] = player.name
        _request["token"] = token
        return _request

    def update(self):
        """
        Update game status, then player status.
        :return response: player_update response (game always succeed, unless server down)
        """
        assert self.__game
        response = self.__get_update()
        try:
            if response.headers["Content-Type"] == "application/json":
                _json = response.json()
                self.__serialize_game(_json=_json['game'])
                if response.status_code == 200:
                    self.__serialize_player(_json=_json['player'])
        except JSONDecodeError as e:
            self.logger.critical(e)
        return response

    def __get_update(self):
        self.__msg_buffer = Update
        self.__msg_buffer.request.update({"content": self.__player.name})
        res = self.send()
        return res

    def send_start_game_signal(self):
        if not self.__game:
            return print("Impossible")
        self.__msg_buffer = Start
        self.__msg_buffer.request.update({"rules": {}, })

        if self.send().status_code == 200:
            self.status = self.GAME_RUNNING

    def __serialize_game(self, _json):
        self.logger.debug(f"Serializing Game from : {type(_json)}  ->  {_json}")
        self.__game_dict = _json

    def __serialize_player(self, _json):
        self.logger.debug(f"Serializing player from : {type(_json)}  ->  {_json}")
        self.__player.from_json(_json=_json)

    def request_player_action(self):
        # self.__msg_buffer = Play or Give or Answer
        plays = self.__player.play(required_cards=self.game_dict.get("required_cards"))
        if plays or self.__player.folded:
            self.__msg_buffer = Play
            self.__msg_buffer.request["plays"] = [c.unicode_safe() for c in plays if c]
            self.send()

    def __update_token(self, token):
        self.__token = token
        self.logger.debug(f"Updated token to {self.__token}")

    @staticmethod
    def __menu_ask_row(rows):
        answer = None
        while answer is None:
            _in = input("select an option... : \r")
            try:
                num = int(_in)
                if 1 <= num <= len(rows):
                    answer = num
                else:
                    print(f"answer required between 1 and {len(rows)}")
            except ValueError:
                answer = None
                print("Requires a number")
        return answer

    def menu(self, name: str = "main menu", options: dict = None):
        """
        CLI Menu
        :return: requested method's results
        """
        if options is None:
            options = {"Find Game": self.find_game,
                       # "Start a new server of your own": self.create_game,  # WIP
                       "Exit Interface": functools.partial(exit, 0)}
            if self.__game:  # Display more options if interface successfully connected to a game
                options.setdefault("Start Game", self.send_start_game_signal)
                options.setdefault("Game Options [Game, rules] (WIP)", self.set_game_options)
            else:
                options.setdefault("Reconnect", self.reconnect)

        while True:
            print("#" * 20 + f" {name.upper()} " + "#" * 20)
            for i, option in enumerate(options):
                print(f"{i + 1} : {option}")
            choice = self.__menu_ask_row(options)
            for i, (info, action) in enumerate(options.items()):
                if i + 1 == choice:
                    return action()

    def __enter__(self):
        # ttysetattr etc goes here before opening and returning the file object
        return self

    def __aenter__(self):
        # Prevision for asynchronous processes (allow faster requests and processing)
        return self

    def __exit__(self, _type, value, traceback):
        self.disconnect()
        self.logger.critical(_type)
        self.logger.critical(value)
        self.logger.critical(traceback)

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __delete__(self, instance):
        self.disconnect()

    def __del__(self):
        self.disconnect()

    def find_game(self):
        """ Allow interface to find other games running """
        finder = GameFinder()
        self.logger.debug(f"Not running : {finder.availabilities}")
        options = {(s, p): functools.partial(self.connect, s, p)
                   for s, p in finder.running_servers}
        return self.menu("Choose Game", options)

    def create_game(self):
        """ Allows player to start a new server locally """
        pass

    def set_game_options(self):
        pass

    def reconnect(self):
        self.__token = input("token ? >")
        self.find_game()

    def init_server(self, name):
        pass

    def to_json(self):
        pass
