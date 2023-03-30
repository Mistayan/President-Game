# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import json
import logging
import time
from abc import abstractmethod, ABC
from threading import Thread  # required for Background server task
from typing import Any, Union, Optional

from flask import request, make_response, Response

from models.players import Player, Human, AI
from models.responses import Connect, Disconnect, Start, Update, Message, Question
from models.utils import SerializableObject, measure_perf
from rules import GameRules
from .Errors import CheaterDetected
from .apis.server import Server
from .db import Database
from .plays import GamePlay


class Game(Server, SerializableObject, ABC):
    """ Base class of Games Hierarchy,
     implements many functionalities for other games to run """

    @abstractmethod
    def __init__(self, nb_players=0, nb_ai=3, *players_names, save=True):
        super().__init__("Game_Server")  # test: init only when start server

        self.game_name = None
        self.players_limit = 100  # Arbitrary Value
        self.__game_log = logging.getLogger(__class__.__name__)
        self.players: list[Player.__class__] = []
        self._winners: list[Player.__class__, int, GamePlay] = []
        self.losers: list[Player.__class__, int, GamePlay] = []
        self.disconnected_players: list[Player] = []  # players logged out while game started
        self.spectators: list[Player] = []  # players that registered after game started
        self.plays: list[list] = []
        self._turn = 0
        self._run = False
        self.__db: Optional[Database] = None
        self.__game_daemon: Optional[Thread] = None
        self.__save = save
        self.__register_players(nb_players, nb_ai, *players_names)

    @abstractmethod
    def _initialize_game(self):
        self.losers = []
        self.disconnected_players = []
        # as long as we can, add players for next game
        while self.spectators and len(self.players) < self.players_limit:
            self.players.append(self.spectators.pop())
        # Check players count before starting, remove extra players before starting.
        while len(self.players) > self.players_limit:
            for player in self.players[::-1]:
                self.spectators.append(self.players.pop(self.players.index(player)))
        self.__game_log.info(' '.join(["#" * 15, "PREPARING NEW GAME", "#" * 15]))
        self._init_db()

    @abstractmethod
    def start(self, override_test=False):
        """ Enforce this method on children ,
         set actions to be done when you start your game """
        # super(Game, self).__init__(self.game_name)

    @abstractmethod
    def player_give_to(self, player: Player, give: Any, to: Any):
        """ In almost every game, Someone can give something to someone/something else"""

    @abstractmethod
    def player_lost(self, player):
        """ Implement how to determine that a player lost from game's rules """

    def _init_db(self):
        """ Instantiate Database link """
        if self.__save and not self.__db:
            self.__db = Database(self.game_name or __class__.__name__)

    def __register_players(self, number_of_players, number_of_ai, *players_names):
        """ Every game need to register players before they are able to play"""
        self.logger.info("registering base players")
        if number_of_players:
            for name in players_names:  # Named players
                self.register(Human(name=str(name)))
                number_of_players -= 1
            if number_of_players > 0:  # Anonymous Players, random generation
                [self.register(Human()) for _ in range(number_of_players)]
        [self.register(AI()) for _ in range(number_of_ai)]  # AI Players

    def __plays_to_unicode_safe(self):
        """ if there are uni unsafe strings,"""
        json_piles = []
        for matchs in self.plays:
            json_pile = []
            for play in matchs:
                json_pile.append(play.unicode_safe())
            json_piles.append(json_pile)
        return json_piles

    def set_game_name(self, name):
        """ set game's name to given one (use this method after you instantiated super()"""
        self.game_name = name  # Override name

    def save_results(self, name) -> dict:
        """ save game's results to db as a Document """
        to_save = {
            "game": name,
            "players": [player.name for player in self.players],
            "winners": self.winners(),
            "plays": self.__plays_to_unicode_safe(),
        }
        if not self.__db:
            self.__game_log.info("Could not save. Game has been created with save = False")
            return to_save
        self.__db.update(to_save)

    def register(self, player: Union[Human, AI, str], token: str = None) -> Player:
        """ Registers players for the game """
        if not isinstance(player, (AI, Human, str)):
            raise ValueError(f"{player} is not a playable character")

        if self.get_player(player) and player.is_human and token == player.token:
            player = self.get_player(player)
        elif self.get_disconnected(player) and self._run:
            player = self.reconnect_player(player)
        elif self.get_spectator(player) and not self._run:
            player = self.join_game(player)
        elif player:
            player = self.register_new_player(player)
        else:
            self.add_player_to_list(player)
        player.set_game(self)
        return player

    def reconnect_player(self, player):
        """ Handles player reconnection to the game """
        self.logger.debug("Reconnecting %s", player)
        player = self.disconnected_players.pop(self.disconnected_players.index(player))
        self.players.append(player)
        return player

    def join_game(self, player):
        """ Handles player joining the game after it has started """
        self.logger.debug("Joining %s", player)
        player = self.spectators.pop(self.spectators.index(player))
        player.reset()
        return player

    def register_new_player(self, player):
        """ Handles registration of new players """
        self.logger.debug("Registering %s", player)
        player = Human(player) if isinstance(player, str) else player
        if player:
            if player.is_human:
                player.renew_token()
            self.add_player_to_list(player)
            self.__game_log.info("%s has registered for the game %s", player,
                                 ' ' + str(player.token) if player.is_human else '')

        return player

    def add_player_to_list(self, player):
        """ Adds player to either spectators or players list """
        if self._run:
            self.logger.debug("Adding spectator %s", player)
            self.spectators.append(player) if player not in self.spectators else None
        else:
            self.logger.debug("Joining %s", player)
            self.players.append(player) if player not in self.players else None

    def unregister(self, player: Player or str) -> None:
        """ Every game needs to register players before they are able to play"""
        if not isinstance(player, (Human, str)):
            raise ValueError("Unclear player type Not Allowed.")
        for i, p in enumerate(self.players):
            if p == player:
                player = self.players.pop(i)
                self.__game_log.info(f"{player} left the game...")
                if self._run:  # save player ONLY if game is running.
                    self.disconnected_players.append(player)
                    self.__game_log.info("See you soon")
                return

    def winners(self) -> list[dict[str, Any]]:
        """ Generate winners ladder, appends losers starting from the last one"""
        if self._run:
            raise RuntimeWarning("Game still running, cannot display winners")
        self.__game_log.debug("\nwinners : %s\nLosers : %s", self._winners, self.losers)
        if self.losers:
            # Losers are to be added from the end. First loser is last 'winner'
            [self._winners.append(player_infos) for player_infos in self.losers[::-1]]
            self.losers = []  # Once over, erase loser queue for next calls

        rank_gen = [{"player": player_infos[0].name,
                     "rank": i + 1,
                     "round": player_infos[1],
                     "last_play": player_infos[2]
                     } for i, player_infos in enumerate(self._winners)]
        return rank_gen

    def _reset_winner(self):
        """ reset winners and losers queue """
        self._winners = []
        self.losers = []

    def show_winners(self):
        """ send every player game's ladder """
        self.send_all("".join(["#" * 15, "WINNERS", "#" * 15]))
        for winner in self.winners():
            self.send_all(winner)

    def set_win(self, player, win=True) -> bool:
        """
        ONLY IF : player hasn't won, and has no more cards:
        append [Player, Round, Last_Card] to winners/losers
        :param player: the player to check validity as a winner
        :param win: Set player status to winner (True) or looser (False)
        :return: True if player won/lost, False otherwise
        """
        if (len(player.hand) and win) or player.won:
            return False
        for test in self._winners:
            if test[0] == player:
                raise CheaterDetected(f"{player} already in the ladder.")
        if win:
            self.__game_log.info("%s won the place N°%d", player, len(self._winners) + 1)
            winner_data = [player, self._turn, player.last_played[0].unicode_safe()]
            self._winners.append(winner_data)
            player.set_win()
        else:
            self._set_lost(player, 'did not win')
        return True

    def _set_lost(self, player, reason=None) -> None:
        """ Set player status to winner and append [Player, Rank] to _rounds_winners"""
        if player.won:
            return
        self.__game_log.info("%s Lost the game.", player)
        if player.hand and not reason:
            last_played = player.hand[-1]
        elif player.last_played:
            last_played = player.last_played[-1]
        else:
            last_played = None
        reason and self.__game_log.info("Reason : %s", reason)
        self.losers.append([player, self._turn, last_played and last_played.unicode_safe()])
        player.set_win()  # It just means that a player cannot play anymore for current game

    # ###################### SERVER IMPLEMENTATIONS TO GAME  #######################

    @abstractmethod
    @measure_perf
    def _init_server(self, name):
        """ Children must implement their own routes """
        super()._init_server(name)

        # ALL ROUTES LISTED BELOW ARE HUMANS INTENDED !!!! ONLY !!!!
        @self.route(f"/{Connect.request['message']}/{Connect.REQUIRED}", methods=Connect.methods)
        @measure_perf
        def register(player) -> Response:
            """ route to register to a game server """
            self.__game_log.debug("Registering %s", player)
            if not self.get_player(player) or \
                    (self.get_disconnected(player) and player.token == request.headers.get("token")):
                # If previously disconnected, log back in
                player: Human = self.register(player, request.headers.get("token"))
                if player.is_human:
                    player.set_game(self)
                    return make_response('OK', 200, {'Connected': '"Registered to the game"', 'token': player.token})

            return make_response('Nope', 401, {'ConnectError': '"Could not register to the game"'})

        @self.route(f"/{Disconnect.request['message']}/{Disconnect.REQUIRED}", methods=Disconnect.methods)
        @measure_perf
        def unregister(player: str) -> Response:
            """ route to exit a game server """
            player: Human = self.get_player(player) or self.get_spectator(player)
            self.__game_log.debug("Disconnecting %s", player)
            if player and player.is_human and request.headers["Content-Type"].find("json"):
                self.__game_log.debug("Is human")
                datas = json.loads(request.data)["headers"]
                if player.token == datas.get("token"):
                    self.__game_log.debug("Token OK")
                    self.unregister(player)
                    return make_response('OK', 200, {'Disconnected': '"Disconnected from game"'})
                else:
                    self.__game_log.debug("Token not OK")
                    return make_response('Nope', 401, {'ConnectError': '"Could not Disconnect from game"'})
            else:
                self.__game_log.critical("%s Not human", player)
            return make_response('Nope', 401, {'ConnectError': '"Could not Disconnect from game"'})

        @self.route(f"/{Update.request['message']}/{Update.REQUIRED}", methods=Update.methods)
        @measure_perf
        def update(player: str):
            """
            Send back Game_Server status.
            Also, if player is given, and player's token is valid, send back player's state
            """
            json_response: dict = {}
            json_response.setdefault("game", self.game_infos)
            status, player_json = self.player_infos(player, request.headers.get("token"))
            json_response.setdefault("player", player_json)
            return make_response(json_response, status)

        @self.route(f"/{Start.request['message']}/{Start.REQUIRED}", methods=Start.methods)
        async def start_from_player(player):
            """ route to register to a game server """
            assert request.headers["Content-Type"] == "application/json"
            p: Human = self.get_player(player)
            self.logger.debug("ptok %s === tok %s", p.token, request.json.get('headers').get("token"))
            assert p and p == player and p.is_human
            assert request.is_json and p.token == request.json.get('headers').get('token')
            if not self._run:
                self.status = self.GAME_RUNNING
                self.__start_server_mode()  # True to override local_cli prompts
                return make_response("SERVER_RUNNING", 200)
            # Find a way for server or no server to play the same way
            return make_response("Cannot start another game. Server busy.")
    ########################################################################

    @measure_perf
    def _send_player(self, player, msg, method=None):
        assert player and msg

        if not player.is_human:
            return

        if self.status == self.OFFLINE:
            self.logger.info("offline.")
            return method and method(msg) or print(msg)

        if method is input:
            self._handle_input_message(player, msg, method)
        elif method is None:
            player.messages.append(msg)

    def _handle_input_message(self, player: Human, msg, method):
        req = Question().request
        req.setdefault("question", msg)
        player.is_action_required = True
        player.messages.append(req)
        answer = None
        self.__game_log.warning("%s(%s)", method, msg)
        self._wait_player_action(player)
        self.logger.info("waiting for %s...\r", player)
        while answer is None and player in self.players:
            time.sleep(GameRules.TICK_SPEED)
            if self._last_message_received:
                answer = self._last_message_received.get(player.plays)
        self.__game_log.warning("Done Waiting.")
        if player not in self.players:
            self.send_all(f"{player} Disconnected. Skipping turn.")
        return answer

    @measure_perf
    def _wait_player_action(self, player):
        """
        Waits for a player to take an action.
        :param player: the player to wait for
        :return: the player's plays
        """
        self.__game_log.info("awaiting %s to play", player)
        timeout = Message.TIMEOUT
        while player.is_action_required and timeout > 0 and player in self.players:
            time.sleep(GameRules.TICK_SPEED)
            timeout -= GameRules.TICK_SPEED
        return player.plays

    @measure_perf
    def send_all(self, msg):
        """
        Sends a message to all human players.
        :param msg: the message to send
        """
        if type(msg) is str:
            # if type of msg is str, wrap it in a dict before sending
            return self.send_all({'message': "Info", 'content': msg})

        if self.status == self.OFFLINE:  # if game is offline, print message
            return print(msg)

        # send message to every human player in the game
        for player in self.players:
            if player.is_human:
                self._send(player, msg)

    @measure_perf
    def _send(self, player, msg):
        """
        Sends a message to a given player.
        :param player: the player to send the message to
        :param msg: the message to send
        """
        player.messages.append(msg)

    @measure_perf
    def receive(self, msg: dict):
        """
        Receives a message and applies it to the game if valid.
        :param msg: the message to receive
        """
        # log message depending on its type
        if msg["message"] == "Info":
            self.logger.info(msg["content"])
        elif msg["message"] == "Error":
            self.logger.error(msg["content"])
        elif msg["message"] == "Warning":
            self.logger.warning(msg["content"])

    def to_json(self) -> dict:
        """
        Returns the game state as a JSON object.
        :return: the game state as a JSON object
        """
        return {
            "game": self.game_name,
            "running": self._run,
            "turn": self._turn,
            "players": [(p.name, len(p.hand)) for p in self.players],
            "disconnected": [[p.name, len(p.hand)] for p in self.disconnected_players],
            "winners": [[p.name, turn, [card and card]] for p, turn, card in self._winners],
            "losers": [[p.name, turn, [card and card]] for p, turn, card in self.losers],
            "plays": [[c.number for c in pile] for pile in self.plays],
        }

    @property
    @measure_perf
    def game_infos(self) -> (str, int, dict):
        """
        Collects information on the game.
        :return: "MSG", status_code, game_as_json
        """
        self.logger.debug(self.to_json())
        return self.to_json()

    @measure_perf
    def player_infos(self, pname, token):
        """
        Collects information on a given player.
        :param pname: the name of the player to get information on
        :param token: the token to verify the player's identity
        :return: status_code, player_as_json
        """
        player = self.get_player(pname) or self.get_disconnected(pname)
        player_data = {}
        code = 404
        if player and player.is_human and player.token != token:
            code = 403
        elif player:
            code = 200
            player_data = player.to_json()
            player.messages = []  # messages has been sent, clear
        return code, player_data

    @measure_perf
    def __start_server_mode(self) -> None:
        """ Run Game as a Thread, allowing for server to be independent of game logics """
        self.__game_daemon = Thread(target=self.start, args=(True,), daemon=True, name='Game')
        self.__game_daemon.start()

    @staticmethod
    @measure_perf
    def get_player_from(player: Player or str, _from: list[Player]) -> Player:
        """ search player's name (token is already validated if required)
         in current players connected """
        for test in _from:
            if isinstance(test, Player) and test == player:
                return test

    def get_player(self, player: Player or str) -> Player:
        """ get player from players list """
        self.logger.debug(f"Searching for {player} in {self.players}...")
        return self.get_player_from(player, self.players)

    def get_disconnected(self, player: Player or str) -> Player and Human:
        """ Get player from disconnected list """
        self.logger.debug(f"Searching for {player} in {self.disconnected_players}...")
        return self.get_player_from(player, self.disconnected_players)

    def get_spectator(self, player: Player or str) -> Player and Human:
        """ Get player from observers list """
        self.logger.debug(f"Searching for {player} in {self.spectators}...")
        return self.get_player_from(player, self.spectators)
