# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import functools
import io
import logging
import os
import time
from json import JSONDecodeError
from subprocess import Popen

import colorama
import requests
from requests import Response

from models import CardGame
from models.conf import BASEDIR
from models.games.apis.server import Server
from models.players.player import Human
from models.responses import *  # over 5 modules, and less than 20% unused, it's permitted
from models.utils import ValidateBuffer, GameFinder


class Interface(Server):
    """
    Instantiate basics for Game interfaces
    """
    local_process: Popen
    DISCONNECTED = 8
    CONNECTED = 10
    WAITING_NEW_GAME = 12
    ACTION_REQUIRED = 21
    PLAY_REQUIRED = 22
    GIVE_REQUIRED = 23

    def __init__(self, player: Human, **kwargs):
        if not isinstance(player, Human):
            raise TypeError("Interface's players MUST be Humans.")
        super().__init__("Player_Interface")
        self.__token = None
        self.__msg_buffer = None
        self.__game_dict = None
        self.logger = logging.getLogger(__class__.__name__)
        self.__super = self.logger.level
        self.__game = None
        self.__player: Human = player
        if not kwargs.get("nobanner"):
            self.__banner()
        self.__run = True

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
        response = self._send(destination=f"{uri}:{port}")  # first time require destination
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
        if self._send().status_code == 200:
            self.status = self.CONNECTED

    @property
    def game_addr(self):
        return self.__game

    @property
    def game_token(self):
        return self.__token

    def receive(self, msg: dict):
        return super().receive(msg)

    def _send(self, destination=None, msg=None):
        """
        Send messages to game
        Everytime the game wants to send a message, we have to retrieve those by updating
        """
        target = destination or self.__game
        if not target:
            return self.not_found(target)
        super()._send(target, self.__msg_buffer)
        message = self.__msg_buffer()  # Instantiate before filling request
        message_method, *others = message.methods  # Gather only first element from tuple
        message.request = self._fill_request(message, self.__player, self.__token)
        self.logger.debug(f"{message_method} : {message.request}")
        self.logger.info(f"sending {message.__class__.__name__} request to {target}")
        response = self.not_found(target)
        try:
            response = requests.request(
                method=message_method,
                url=f"{self._PROTOCOL}://{target}/{message.request['message']}/{self.__player.name}",
                headers=message.headers,
                cert=None,  # yet...
                json=message.to_json(),
            )
        except ConnectionError:
            print(f"Server {target} Not responding. {response}")

        return response

    @ValidateBuffer
    def __apply_message(self, msg):  # WIP
        """
        Whenever we receive a message, we are required to apply it
        """
        test = self.__msg_buffer["action"]
        if test == "Play":  # changed to if/elif for python 3.9 compatibility
            self.__msg_buffer.setdefault("action", self.__player.play(msg['required_cards']))
        elif test == "Give":
            self.__msg_buffer.setdefault("action", self.__player.choose_cards_to_give())
        elif test == "Info":
            print(self.__msg_buffer["message"])
        else:
            raise MessageError(f"Non of the given message is valid: {self.__msg_buffer}")
        return self._send()

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
        if not self.__game:
            return self.menu()
        try:
            response = self.__get_update()
        except ConnectionError:
            print("Impossible to connect to designated server... sending back to main menu")
            self.menu()
            response = self.not_found(self.__game)
        try:
            # if response and response.headers["Content-Type"] == "application/json":
            _json = response.json()
            self.__serialize_game(_json=_json['game'])
            if response.status_code == 200:
                self.__serialize_player(_json=_json['player'])
            # else:
            #     print("not json")
        except JSONDecodeError as e:
            self.logger.critical(e)
        return response

    def __get_update(self):
        self.__msg_buffer = Update
        self.__msg_buffer.request.update({"content": self.__player.name})
        res = self._send()
        return res

    def send_start_game_signal(self):
        if not self.__game:
            return print("Impossible")
        self.__msg_buffer = Start
        self.__msg_buffer.request.update({"rules": {}, })

        if self._send().status_code == 200:
            self.status = self.GAME_RUNNING

    def __serialize_game(self, _json):
        self.logger.debug(f"Serializing Game from : {type(_json)}  ->  {_json}")
        self.__game_dict = _json

    def __serialize_player(self, _json):
        self.logger.debug(f"Serializing player from : {type(_json)}  ->  {_json}")
        try:
            self.__player.from_json(_json=_json)
        except MessageError:
            self.__msg_buffer = AnomalyDetected
            self.__msg_buffer.request.update("anomaly", **_json)
            self._send()

    def request_player_action(self):
        # self.__msg_buffer = Play or Give or Answer
        plays = self.__player.play(required_cards=self.game_dict.get("required_cards"))
        if plays or self.__player.folded:
            self.__msg_buffer = Play
            self.__msg_buffer.request["plays"] = [c.unicode_safe() for c in plays if c]
            self._send()

    def __update_token(self, token):
        self.__token = token
        self.logger.debug(f"Updated token to {self.__token}")

    @staticmethod
    def __select_option_number(rows):
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
                       "Start a new server of your own": self.start_GameServer,
                       # "Start a game locally": self.start_new_local_game,
                       "Exit Interface": functools.partial(exit, 0)}
            if self.__game:  # Display more options if interface successfully connected to a game
                options.setdefault("Start Game", self.send_start_game_signal)
                options.setdefault("Game Options [Game, rules] (WIP)", self.set_game_options)
                self.__token and options.setdefault("Reconnect", self.reconnect)
        action = -1
        if len(options):
            while action == -1:
                print("#" * 20 + f" {name.upper()} " + "#" * 20)
                for i, option in enumerate(options):
                    print(f"{i + 1} : {option}")
                choice = self.__select_option_number(options)
                for i, (info, action) in enumerate(options.items()):
                    if i + 1 == choice:
                        action = action()
                        break
        else:
            print("No menu to display")
        return action

    def __enter__(self):
        # ttysetattr etc goes here before opening and returning the file object
        print(f"Welcome, {self.__player}")
        return self

    def __aenter__(self):
        # Prevision for asynchronous processes (allow faster requests and processing)
        return self

    def __banner(self):
        import PIL.Image
        ascii_map = ["@", "#", "$", "%", "?", "!", "*", "+", ":", ",", ".", ".", "."]
        BANNER_WIDTH = 75
        MAX_LINES = 25

        def pixel_to_ascii(img):
            pixels = img.getdata()
            ascii_str = ""
            ascii_map.reverse()
            for pixel in pixels:
                ascii_str += ascii_map[(pixel // (255 // len(ascii_map))) % len(ascii_map)]
            return ascii_str

        def resize(img):
            return img.resize((BANNER_WIDTH, MAX_LINES))

        try:
            self.logger.info("Preparing Interface ... ")
            req = requests.get(
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTzA-OJMj_asPXQM-1TAlC3"
                "_yn03sPkArzvMd5qglLom5-nzyOr09596kof0xauehvc31M&usqp=CAU",
                stream=True)
            self.logger.info(f"self assigning : {req.status_code}")
            image_bytes = io.BytesIO(req.content)
            self.logger.info("Transposing ...")
            image = PIL.Image.open(image_bytes)
            self.logger.info(f"Transforming ...")
            image = image.convert(mode="L")  # GreyScales
            self.logger.info(f"Resizing ...")
            image = resize(image)
            self.logger.info(f"Manipulating ...")
            banner = pixel_to_ascii(image)
            self.logger.info(f"Printing ...")
            prev = 0
            for line in range(0, MAX_LINES):
                print(banner[prev:line * BANNER_WIDTH])
                prev = line * BANNER_WIDTH
        except Exception as e:
            self.logger.critical(e)

    def __exit__(self, _type, value, traceback):
        self.disconnect()
        if self.local_process:
            self.local_process.terminate()
        self.logger.critical(_type)
        self.logger.critical(value)
        self.logger.critical(traceback)
        print(colorama.Style.BRIGHT + colorama.Fore.BLACK + colorama.Back.GREEN,
              "\tSee you soon :D\t\t" + colorama.Style.RESET_ALL)

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __delete__(self, instance):
        self.disconnect()

    def __del__(self):
        self.disconnect()

    def find_game(self) -> int:
        """
        Allow interface to find other games running
        :return: either server index selected or -1 in case of error
        """
        finder = GameFinder()
        self.logger.debug(f"Not running : {finder.availabilities}")
        options = {(s, p): functools.partial(self.connect, s, p)
                   for s, p in finder.running_servers}
        if len(options):
            return self.menu("Choose Game", options)
        elif self.__player.ask_yes_no("No game Found. Start a server yourself ? :)"):
            print("starting background task : ", os.path.join(BASEDIR, "run_server.py"))
            self.start_GameServer()
            time.sleep(3)  # let time for server to start
            return self.find_game()
        return -1

    def set_game_options(self, game=None):
        """
        Set game's options like QUEEN_OF_HEART_STARTS
        if no game is given, and connected to a server that accepts it, edit game's rules
        """
        pass

    def reconnect(self):
        """ If a session token is found from previous connection, try to reconnect to game"""
        if not self.__token:
            return print("No previous connection established")

        # __game is formatted like "host:port".
        # calling *on a list or a tuple decomposes it like *args
        self.connect(*self.__game.split(":"))

    def _init_server(self, name):
        pass

    def to_json(self):
        pass

    def not_found(self, target=None):
        res = Response
        res.status_code = 404
        return res

    def start_new_local_game(self):
        """
        Choose a game from a list of available games styles
        and set games options before starting it.
        """
        game = self.menu("Choose game", {
            "Card Game": functools.partial(CardGame, 1, 3),
            "President Game": functools.partial(CardGame, 1, 3),
        })
        self.__player.set_game(game)  # necessary to play local
        self.set_game_options(game)  # WIP
        game.start()
        # Game is over, and player chose not to start another one
        self.__player.set_game(None)  # reset game pointer, in case he wants to go 'online'

    def start_GameServer(self, port=5001, exec_path=BASEDIR):
        self.local_process = Popen([
            os.path.join(exec_path, "venv/Scripts/python"),
            os.path.join(exec_path, f"run_server.py"),
            f"-p {port}",
        ])
        if self.__super:
            print(self.__super)
            self.local_process.communicate()

    def run_interface(self):
        try:
            while self.__run:

                self.menu()  # Connect or exit
                while self.update():  # As long as we are connected, with no errors
                    if self.action_required is True:
                        self.request_player_action()
                    elif self.game_dict and self.game_dict.get('running') is False:
                        self.menu()
        except KeyboardInterrupt as e:
            print("Shutting down Interface...")
