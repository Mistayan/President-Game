# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
from __future__ import annotations

import functools
import io
import logging
import os
import time
from json import JSONDecodeError
from subprocess import Popen
from typing import Any, List

import PIL.Image
import colorama
import requests
from requests import Response

from conf import BASEDIR, VENV_PYTHON
from models import CardGame, utils
from models.networking.communicant import Communicant
from models.players.player import Human
from models.responses import *
from models.utils import GameFinder, SerializableClass
from rules import CardGameRules, PresidentRules


class Interface(Communicant):
    """
    Instantiate basics for Game interfaces
    """

    def __init__(self, player: Human, **kwargs):
        self.__status = None
        if not isinstance(player, Human):
            raise TypeError("Interface's players MUST be Humans.")
        super().__init__("Player_Interface")
        self.__token = None
        self.__msg_buffer = None
        self.__game_dict = {}
        self.__game_rules = None
        self.logger = logging.getLogger(__class__.__name__)
        self._game = None
        self.__player: Human = player
        if not kwargs.get("nobanner"):
            self.__banner()
        self.__run = True

    @property
    def is_action_required(self):
        """ returns True if interface's user action is required """
        return self.__player.is_action_required

    @property
    def game_dict(self):
        """ returns game state as dict"""
        return self.__game_dict

    def connect(self, uri: str, port: int):
        """ Set a connection to Game """
        assert uri and isinstance(uri, str)
        assert port and isinstance(port, int)
        self.__msg_buffer = Connect
        self.__msg_buffer.request.setdefault("player", self.__player.name)
        # first time requires destination
        response = self._send(destination=f"{uri}:{port}")
        self.logger.debug("%s %s", response, response.status_code)
        if response and response.status_code == 200:
            self.__status = self.CONNECTED
            self._game = f"{uri}:{port}"  # If succeeded, we know the game exists
            self.logger.debug(response.headers)
            if response.headers.get('token') != self.__token:
                self.__update_token(response.headers.get('token'))
                assert self.__token == response.headers.get('token')
                # success to authenticate, load game rules

            self.logger.debug(self.__token)
        else:
            self._game = None
            Interface.print('Failed to connect')
        return response

    def disconnect(self):
        """ Disconnect from the Game """
        if not self._game:
            return
        self.__msg_buffer = Disconnect
        if self._send().status_code == 200:
            self.__status = self.CONNECTED

    @property
    def game_addr(self):
        """ Returns game's address """
        return self._game

    @property
    def game_token(self):
        """ Returns token given by server """
        return f"{self.__token}"

    def receive(self, msg: dict):
        return super().receive(msg)

    def _send(self, destination=None, msg=None):
        """
        Send messages to game
        Everytime the game wants to _send a message, we have to retrieve those by
         updating
        """
        target = destination or self._game
        if not target:
            return self.not_found(target)
        super()._send(target, self.__msg_buffer)
        message = self.__msg_buffer()  # Instantiate before filling request
        message_method, *_ = message.methods  # Gather only first element from tuple
        message.headers = self._fill_headers(message)
        message.request = self.__msg_buffer.request
        self.logger.debug("{%s} // {%s} // : {%s}", message_method, message.headers, message.request)
        self.logger.info("sending %s request to %s", message.__class__.__name__, target)
        crypt = functools.partial(utils.xor if self.__token else str)
        response = requests.request(
            method=message_method,
            url=f"{self._PROTOCOL}://{target}/{message.request['message']}/{self.__player.name}",
            headers=message.headers,  # utils.xor(data, token)
            cert=None,  # yet...
            json=message.to_json(),  # utils.xor(data, token)
        )
        self.logger.debug("Received %s, %s, %s", response.status_code, response.headers, response.content)
        self.__msg_buffer = None
        return response if response.status_code != 500 else self.not_found(target)

    def _fill_headers(self, msg: SerializableClass) -> dict:
        """
        Complete 'msg.request' with required information
        :param msg: Any Message class
        :return:
        """
        # instantiate message buffer to memory, so any modification is not in file
        _j = msg.to_json()
        _request = _j.get("headers")
        _request["player"] = self.__player.name
        _request["token"] = self.__token
        return _request

    def update(self):
        """
        Update game status, then player status.
        :return response: player_update response (game always succeed, unless server down)
        """
        if not self._game:
            return self.select_from_menu()
        try:
            response = self.__get_update()
            self.logger.debug(response)
        except ConnectionError:
            Interface.print("Impossible to connect to designated server... sending back to main menu")
            self.select_from_menu()
            response = self.not_found(self._game)
        try:
            # if response and response.headers["Content-Type"] == "application/json":
            _json = response.json()
            self.__game_dict = _json['game']
            self.__serialize_game()
            if response.status_code == 200:
                self.__serialize_player(_json=_json['player'])
            self.logger.debug("do i have to play ? => %s ", self.__player.is_action_required)

        except JSONDecodeError as ex:
            self.logger.critical(ex)
        except TypeError:
            pass
        return response

    def __get_update(self):
        self.__msg_buffer = Update
        self.__msg_buffer.request.update({"content": self.__player.name})
        res = self._send()
        return res

    def send_start_game_signal(self):
        """ send server a signal to run a game """
        if not self._game:
            Interface.print("Impossible")
            return
        self.__msg_buffer = Start
        self.__msg_buffer.request.update({"rules": {}, })

        if self._send().status_code == 200:
            self.__status = self.GAME_RUNNING

    def __serialize_game(self):
        """ Serialize game from json to actualize game state """
        self.logger.debug("Serializing Game from : %s -> %s", type(self.__game_dict), self.__game_dict)
        self.__update_game_rules(self.__game_dict)

    def __serialize_player(self, _json):
        """ Serialize game from json to actualize player state """
        self.logger.debug("Serializing player from : %s -> %s", type(_json), _json)
        try:
            self.__player.from_json(_json=_json)
            self.__player.set_game_rules(self.__game_rules)
        except MessageError:
            self.__msg_buffer = AnomalyDetected
            self.__msg_buffer.request.update("anomaly", **_json)
            self._send()

    def request_player_action(self):
        """ send player a play request """
        plays = self.__player.play(required_cards=self.__game_dict.get("required_cards"))
        if plays:
            self.__msg_buffer = Play
            self.__msg_buffer.request["plays"] = [c.unicode_safe() for c in plays if c]
        else:
            self.__msg_buffer = Update
        if self.__player.folded:
            self.__msg_buffer = Fold
        self._send()

    def __update_token(self, token):
        """ update player token to given one"""
        self.__token = token
        self.logger.debug("Updated token to %s", self.__token)

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
                    Interface.print(f"answer required between 1 and {len(rows)}")
            except ValueError:
                answer = None
                Interface.print("Requires a number")
        return answer

    @property
    def __base_menu(self):
        options = {
            "Find Game": self.find_game,
            # "Start a game locally": self.start_new_local_game,
            "Exit Interface": functools.partial(exit, 0)}
        if self._game:  # Display more options if interface successfully connected to a game
            options.setdefault("Start Game", self.send_start_game_signal)
            options.setdefault("Game Options [Game, rules] (WIP)", self.set_game_options)
            if not self.__token:
                options.setdefault(" !! I already have a token !! ", self._set_token)

        elif not self._game:
            if self.__token:
                options.setdefault("Reconnect", self.reconnect)
            if not self._local_process and not self._game:
                options.setdefault("Start a new server of your own", self.start_game_server)

        elif self._local_process:
            options.setdefault("Stop server", self.stop_game_server)

        return options

    def select_from_menu(self, name: str = "main menu", options: dict = None, edit: bool = False) -> Any:
        """
        CLI Menu
        :return: requested method's results
        """
        if options is None:
            options = self.__base_menu

        action = -1
        if len(options):
            while action == -1:
                Interface.print("#" * 20 + f" {name.upper()} " + "#" * 20)
                for i, option in enumerate(options):
                    Interface.print(f"{i + 1} : {option}")
                choice = self.__select_option_number(options)
                for i, (key, action) in enumerate(options.items()):
                    if i + 1 == choice:
                        if not edit:
                            action = action()
                        else:
                            action = key
                        break
        else:
            Interface.print("No menu to display")
        return action

    def __enter__(self):
        # ttysetattr etc. goes here before opening and returning the file object
        Interface.print(f"Welcome, {self.__player}")
        return self

    def __aenter__(self):
        # Prevision for asynchronous processes (allow faster requests and processing)
        return self

    def _set_token(self):
        self.__token = input("Token ?")

    def __banner(self):
        ascii_map = ["@", "#", "$", "%", "?", "!", "*", "+", ":", ",", ".", ".", "."]
        banner_width = 75
        max_lines = 25

        def pixel_to_ascii(img):
            pixels = img.getdata()
            ascii_str = ""
            ascii_map.reverse()
            for pixel in pixels:
                ascii_str += ascii_map[(pixel // (255 // len(ascii_map))) % len(ascii_map)]
            return ascii_str

        try:
            self.logger.info("Preparing Interface ... ")
            req = requests.get(
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTzA-OJMj_asPXQM-1TAlC3"
                "_yn03sPkArzvMd5qglLom5-nzyOr09596kof0xauehvc31M&usqp=CAU",
                stream=True, timeout=5)
            self.logger.info("self assigning : %d", req.status_code)
            image_bytes = io.BytesIO(req.content)
            self.logger.info("Transposing ...")
            image = PIL.Image.open(image_bytes)
            self.logger.info("Transforming ...")
            image = image.convert(mode="L")  # GreyScales
            self.logger.info("Resizing ...")
            image = image.resize((banner_width, max_lines))
            self.logger.info("Manipulating ...")
            banner = pixel_to_ascii(image)
            self.logger.debug("Printing ...")
            prev = 0
            for line in range(0, max_lines):
                Interface.print(banner[prev:line * banner_width])
                prev = line * banner_width
        except Exception as ex:
            self.logger.critical(ex)

    def __exit__(self, _type, value, traceback):
        try:
            self.disconnect()
            if self._local_process:
                self._local_process.terminate()
        except Exception:
            self.logger.critical(_type)
            self.logger.critical(value)
            self.logger.critical(traceback)
        finally:
            Interface.print(colorama.Style.BRIGHT + colorama.Fore.BLACK + colorama.Back.GREEN,
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
        self.logger.debug("Not running : %s", finder.availabilities)
        options = {(s, p): functools.partial(self.connect, s, p)
                   for s, p in finder.running}
        if len(options):
            return self.select_from_menu("Choose Game", options)
        if self.__player.ask_yes_no("No game Found. Start a server yourself ? :)"):
            Interface.print("starting background task : ", os.path.join(BASEDIR, "run_server.py"))
            self.start_game_server()
            time.sleep(3)  # let time for server to start
            return self.find_game()
        return -1

    def __edition_menu(self, menu: dict) -> dict:
        return_dict = {}
        for key, value in menu.items():  # Remove values that should not be edited
            if isinstance(value, bool):
                return_dict.update({f"{key} [{value}]": value})  # then add key: value pair as title, so we know
        return return_dict

    def set_game_options(self):
        """
        Set game's options like QUEEN_OF_HEART_STARTS
        if no game is given, and connected to a server that accepts it, edit game's rules
        """
        menu = self.__edition_menu(self.__game_rules.to_json())
        menu.update({"Exit": self.select_from_menu})
        # Edit game options
        changes = False
        choice = None
        while choice != "Exit":
            choice = self.select_from_menu("edit game options", menu, edit=True)
            test = menu.get(choice)
            if isinstance(test, bool):
                changes = self.__update_dict_value(menu, choice, not menu[choice])
            else:  # Exit
                if self.__send_options(self.__game_rules.to_json()).status_code == 200:
                    Interface.print("Game options updated")
                elif changes:
                    Interface.print("Failed to update game options")
                break
        return

    def __update_dict_value(self, menu: dict, choice, new_value):
        real_var = str(choice).split()[0]
        menu.pop(choice)
        menu.update({f"{real_var} [{new_value}]": new_value})
        menu.pop("Exit")
        menu.update({"Exit": self.select_from_menu})
        self.__game_rules.update({real_var: new_value})
        return True

    def __send_options(self, options: dict) -> Response:
        """ Send game options to server """
        self.logger.debug("Sending game options")
        self.__msg_buffer = GameUpdate
        self.__msg_buffer.request.update({"content": options})
        res = self._send()
        return res

    def reconnect(self):
        """ If a session token is found from previous connection, try to reconnect to game"""
        if not self.__token or not self._game:
            return Interface.print("No previous connection established")

        # __game is formatted like "host:port".
        # calling * on a list or a tuple decomposes it like *args
        return self.connect(*self._game.split(":"))

    def _init_server(self, name):
        """Interface won't handle server on the same thread,
         so interface doesn't need to init the server"""
        pass

    def to_json(self):
        """Interface won't send its content"""
        pass

    def not_found(self, target=None):
        """ Generate log info and basic response type """
        if target is None:
            target = self._game
        self.logger.info("Could not connect to server %s", target)
        res = Response
        res.status_code = 404
        return res

    def start_new_local_game(self):
        """
        Choose a game from a list of available games styles
        and set games options before starting it.
        """
        game = self.select_from_menu("Choose game", {
            "Card Game": functools.partial(CardGame, 1, 3),
            "President Game": functools.partial(CardGame, 1, 3),
        })
        self.__player.set_game(game)  # necessary to play local
        self.set_game_options()  # WIP
        game.start()
        # Game is over, and player chose not to start another one
        self.__player.set_game(None)  # reset game pointer, in case he wants to go 'online'

    def start_game_server(self, port=5001, exec_path=BASEDIR) -> None:
        """ start a game server in a background task """
        self.logger.critical(f"{os.path.join(BASEDIR, VENV_PYTHON)} ==> {os.path.join(exec_path, 'run_server.py')}")
        self._local_process = Popen([
            os.path.join(BASEDIR, VENV_PYTHON),
            os.path.join(exec_path, "run_server.py")])
        time.sleep(3)

    def stop_game_server(self) -> None:
        self.disconnect()
        self._game = None
        self.__token = None
        if self._local_process:
            self._local_process.terminate()
        self._local_process = None
        return self.select_from_menu()

    def run_interface(self) -> None:
        """
        Run the interface for user to interact with
        as long as player does not intentionally exit via menu or use KeyboardInterrupts,
         it will run
        """
        try:
            self.select_from_menu()  # Connect or exit
            while self.__run and self.update():  # As long as we are connected, with no errors

                if self.is_action_required is True:
                    self.request_player_action()
                else:
                    self.select_from_menu()
        except KeyboardInterrupt:
            Interface.print("Shutting down Interface...")
            Interface.print(f"here is your token to reconnect : {self.__token}")

    @classmethod
    def print(cls, *params):
        print(*params)

    def __update_game_rules(self, game_dict):
        games_rules = {
            "CardGame": CardGameRules,
            "PresidentGame": PresidentRules,
        }
        game_name = game_dict.get("game")
        game_rules = game_dict.get("game_rules", dict())
        players: List = game_dict.get("players")
        if not self.__game_rules:
            self.__game_rules = games_rules.get(game_name, CardGameRules)(len(players))
        self.__game_rules.update(game_rules)
