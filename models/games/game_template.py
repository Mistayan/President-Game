# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import json
import logging
from abc import abstractmethod, ABC
from threading import Thread  # required for Background server task
from typing import Any

from flask import request, make_response

from models.players import Player, Human, AI
from models.responses import Connect, Disconnect, Start, Update
from models.utils import SerializableObject
from .Errors import CheaterDetected
from .apis.server import Server
from .db import Database
from .plays import GamePlay


class Game(Server, ABC, SerializableObject):

    @abstractmethod
    def __init__(self, nb_players=0, nb_ai=3, *players_names, save=True):
        super(Game, self).__init__("Game_Server")  # test: init only when start server

        self.players_limit = 100  # Arbitrary Value
        self.__game_log = logging.getLogger(__class__.__name__)
        self.players: list[Player.__class__] = []
        self._winners: list[Player.__class__, int, GamePlay] = []
        self.losers: list[Player.__class__, int, GamePlay] = []
        self.disconnected_players: list[Player] = []  # players logged out while game started
        self.awaiting_players: list[Player] = []  # players that registered after game started
        self.plays: list[list] = []
        self._turn = 0
        self._run = False
        self.__db: Database = None
        self.__game_daemon: Thread = None
        self.__save = save
        self.__register_players(nb_players, nb_ai, *players_names)

    @abstractmethod
    def _initialize_game(self):
        """
        Reset loser queue, then remove disconnected players for next game.
        Then add as many awaiting players as possible to game (no ranks)
        If player count is too high, remove last registered players until limit reached

        """
        self.losers = []
        self.disconnected_players = []
        # as long as we can, add players for next game
        while self.awaiting_players and len(self.players) < self.players_limit:
            self.players.append(self.awaiting_players.pop())
        # Check players count before starting, remove extra players before starting.
        while len(self.players) > self.players_limit:
            for player in self.players[::-1]:
                self.awaiting_players.append(self.players.pop(self.players.index(player)))
        self.__game_log.info(' '.join(["#" * 15, "PREPARING NEW GAME", "#" * 15]))
        self._init_db()

    @abstractmethod
    def start(self, override_test=False):
        # super(Game, self).__init__(self.game_name)
        pass

    @abstractmethod
    def player_give_to(self, player: Player, give: Any, to: Any):
        """ In almost every game, Someone can give something to someone/something else"""
        pass

    @abstractmethod
    def player_lost(self, player):
        pass

    def _init_db(self):
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
        self.game_name = name  # Override name

    def __winners_unicode_safe(self, winners):
        json_winners = []
        for winner in winners:
            ww = winner.copy()
            if winner['last_play']:
                ww["last_play"] = winner["last_play"].unicode_safe() or None
            json_winners.append(ww)
        return json_winners

    def save_results(self, name) -> dict:
        to_save = {
            "game": name,
            "players": [player.name for player in self.players],
            "winners": self.__winners_unicode_safe(self.winners()),
            "plays": self.__plays_to_unicode_safe(),
        }
        if not self.__db:
            self.__game_log.info("Could not save. Game has been created with save = False")
            return to_save
        self.__db.update(to_save)

    def register(self, player: Player or str, token: str = None) -> Player:
        """ Every game need to register players before they are able to play """
        if not isinstance(player, (AI, Player, str)):
            raise ValueError(f"{player} not a Player")
        # Player already 'in-game'
        p = self.get_player(player)
        if p and token == p.token:
            return p

        # Player Re-Connect
        p = self.get_disonnected(player)
        if p and self._run:
            self.logger.debug(f"Re-Connecting {player}")
            p = self.disconnected_players.pop(self.disconnected_players.index(p))
            self.players.append(p)
            return p

        # player register to the game after it started
        if player in self.awaiting_players and not self._run:
            self.logger.debug(f"Done Waiting {player}")
            p = self.awaiting_players.pop(self.awaiting_players.index(player))
            p.reset()  # Ensure player is set to default when joining the game
        else:  # Player registers for first time (or after being voided)
            self.logger.debug(f"Registering {player}")
            p = Human(player) if type(player) is str else player
            not p.is_human or p.renew_token()
            self.__game_log.info(f"{p} registered to the game"
                                 f"{' with token ' + str(p.token) if p.is_human else ''}")

        if self._run is True and p not in self.players:
            self.awaiting_players.append(p)
        if self._run is False:
            self.players.append(p)

        # server-side assignment only.
        p.set_game(self)  # important to remind: self is a reference to last sub_class in MRO
        return p

    def unregister(self, player: Player or str) -> None:
        """ Every game needs to register players before they are able to play"""
        if not isinstance(player, (Human, str)):
            raise ValueError(f"Unclear player type Not Allowed.")
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
        self.__game_log.debug(f"\nwinners : {self._winners}\nLosers : {self.losers}")
        if self.losers:
            # Losers are to be added from the end. First loser is last 'winner'
            [self._winners.append(player_infos) for player_infos in self.losers[::-1]]
            self.losers = []  # Once over, erase loser queue for next calls

        rank_gen = [{"player": player_infos[0].name,
                     "rank": i + 1,
                     "round": player_infos[1],
                     "last_play": player_infos[2].unicode_safe()
                     } for i, player_infos in enumerate(self._winners)]
        return rank_gen

    def _reset_winner(self):
        self._winners = []

    def show_winners(self):
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
            self.__game_log.info(f"{player} won the place N°{len(self._winners) + 1}")
            winner_data = [player, self._turn, player.last_played[0]]
            self._winners.append(winner_data)
            player.set_win()
        else:
            self._set_lost(player, 'did not win')
        return True

    def _set_lost(self, player, reason=None) -> None:
        """ Set player status to winner and append [Player, Rank] to _rounds_winners"""
        if player.won:
            return
        self.__game_log.info(f"{player} Lost the game.")
        last_played = player.hand[-1] if player.hand and not reason \
            else player.last_played[-1] if player.last_played else None

        self.losers.append([player, self._turn, last_played])
        player.set_win()  # It just means that a player cannot play anymore for current game

    @staticmethod
    def get_player_from(player: Player or str, _from: list[Player]) -> Player:
        for test in _from:
            if isinstance(test, Player) and test == player:
                return test

    def get_player(self, player: Player or str) -> Player or Human or AI:
        return self.get_player_from(player, self.players)

    # ###################### SERVER IMPLEMENTATIONS TO GAME  #######################

    @abstractmethod
    def init_server(self, name):
        """ Children must implement their own routes """
        super(Game, self).init_server(name)

        # ALL ROUTES LISTED BELOW ARE HUMANS INTENDED !!!! ONLY !!!!

        @self.route(f"/{Connect.request['message']}/{Connect.REQUIRED}", methods=Connect.methods)
        def register(player):
            if not self.get_player(player):
                player: Human = self.register(player)  # If previously disconnected, log back in
                if player.is_human:
                    player.set_game(self)
                    return make_response('OK', 200, {'Connected': '"Registered to the game"',
                                                     'token': player.token})

            return make_response('Nope', 401, {'ConnectError': '"Could not register to the game"'})

        @self.route(f"/{Disconnect.request['message']}/{Disconnect.REQUIRED}",
                    methods=Disconnect.methods)
        def unregister(player: str):
            player: Human = self.get_player(player) or self.get_awaiting(player)
            if player and player.is_human and request.headers["Content-Type"].find("json"):
                datas = json.loads(request.data)["request"]
                if player.token == datas.get("token"):
                    self.unregister(player)
                    return make_response('OK', 200, {'Disconnected': '"Disconnected from game"'})
            return make_response('Nope', 401, {'ConnectError': '"Could not Disconnect from game"'})

        @self.route(f"/{Update.request['message']}/{Update.REQUIRED}", methods=Update.methods)
        def update(player: str):
            """
            Send back Game_Server status.
            Also, if player is given,
            """
            json_response: dict = {}
            json_response.setdefault("game", self.game_infos)
            status, player_json = self.player_infos(player)
            json_response.setdefault("player", player_json)
            return make_response(json_response, status)

        @self.route(f"/{Start.request['message']}/{Start.REQUIRED}", methods=Start.methods)
        async def start_from_player(player):
            assert request.headers["Content-Type"] == "application/json"
            p: Human = self.get_player(player)
            assert p and p == player
            assert request.is_json and p.token == request.json.get('request').get('token')
            if not self._run:
                self.status = self.GAME_RUNNING
                self.__game_daemon = self.__start_server_mode()  # True to override local_cli prompts
                return make_response("SERVER_RUNNING", 200)
            return make_response("Cannot start another game. Server busy.")
            pass  # Find a way for server or no server to play the same way

    ########################################################################

    def send_all(self, msg):
        """ Send a message containing 'msg' to every Human player"""
        if type(msg) is str:
            return self.send_all({'message': "Info", 'content': msg})

        if self.status == self.OFFLINE:
            return print(msg)
        for player in self.players:
            if player.is_human:
                self.send(player, msg)

    def send(self, player, msg):
        player.messages.append(msg)

    def receive(self, msg: dict):
        """ Received a message, apply it to the game if valid """
        pass
    #     super(Game, self).receive(msg)
    #     self.__game_log.info(f"Receiving : {msg}...")
    #     try:
    #         if msg["message"] in ("Connect", "Disconnect", "Start"):
    #             return self.__apply_message(msg)
    #         else:
    #             for player in self.players:
    #                 if player == msg["player"] or msg["player"] == "all":
    #                     if msg["message"] in ("give", "play"):
    #                         msg.setdefault("player", player)
    #                         return self.__apply_message_to_player(msg, player)
    #     except Exception:
    #         self.__game_log.error(f"{msg['player']} -> {msg['message']} : Failed")
    #         raise
    #
    # def __apply_message_to_player(self, msg, player):
    #     """
    #
    #     :param msg:
    #     :param player:
    #     :return:
    #     """
    #     print(msg, player)
    #     match msg["message"]:
    #         case "Play":
    #             self.logger.info("received Play Message")
    #             pass
    #         case "Give":
    #             self.logger.info("received Give Message")
    #             pass
    #         case _:
    #             self.logger.info(f"received Unknown Message: {msg}")
    #             raise
    #     pass
    #
    # def __apply_message(self, msg):
    #     match msg["message"]:
    #         case "Connect":
    #             self.logger.info("received Connect Message")
    #             return self.register(Human(msg["player"], self))
    #             pass
    #         case "Disconnect":
    #             self.logger.info("received Disconnect Message")
    #             return self.unregister(msg["player"])
    #             pass
    #         case _:
    #             self.logger.info("received Unknown Message: ", msg)
    #             raise
    #     pass

    @abstractmethod
    def to_json(self) -> dict:
        su: dict = super(Game, self).to_json()
        update = {
            "game": self.game_name,
            "running": self._run,
            "turn": self._turn,
            "players": [(p.name, len(p.hand)) for p in self.players],
            # players in-game, waiting to reconnect
            "disconnected": [[p.name, len(p.hand)] for p in self.disconnected_players],
            "winners": [[p.name, turn, [card.unicode_safe()]] for p, turn, card in self._winners],
            "losers": [[p.name, turn, [card.unicode_safe()]] for p, turn, card in self.losers],
            "plays": [[c.number for c in pile] for pile in self.plays],
            # players that registered after game started
            "awaiting": [p.name for p in self.awaiting_players],
        }
        su.update(update)
        return su

    @property
    def game_infos(self) -> (str, int, dict):
        """
        collect information on game (Public method, for potential future viewing system)
        :param pname: player to get infos from
        :return: "MSG", status_code, game_as_json
        """
        self.logger.debug(self.to_json())
        return self.to_json()

    def get_disonnected(self, player: Player or str) -> Player and Human:
        return self.get_player_from(player, self.disconnected_players)

    def get_awaiting(self, player: Player or str) -> Player and Human:
        return self.get_player_from(player, self.awaiting_players)

    def player_infos(self, pname):
        """
        collect information on player, if given token is checked, player is registered and HUMAN !
        gather messages then remove those for future calls
        :param pname: player to get infos from
        :return: "MSG", status_code, player_as_json
        """
        p: Human = self.get_player(pname) or \
            self.get_disonnected(pname) or self.get_awaiting(pname)
        content = None
        if not p:
            status = 404
        else:
            assert p.is_human
            if p.token != request.json.get('request').get('token'):
                status = 403
            else:
                status = 200
                content = p.to_json()
                p.messages = []
        return status, content

    def __start_server_mode(self):
        daemon = Thread(target=self.start, args=(True,), daemon=True, name='Game')
        daemon.start()
        return daemon
