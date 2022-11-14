# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import logging
import random
import string
from abc import abstractmethod, ABC
from typing import Any, Final

from models.Errors import CheaterDetected
from models.db import Database
from models.players import Player, Human, AI


class Game(ABC):
    # Instances Shared attributes
    # Will only be generated on first run of an instance, while GameManager runs
    _super_shared_private: Final = ''.join(random.choices(string.hexdigits, k=100))

    @abstractmethod
    def __init__(self, nb_players=3, nb_ai=0, *players_names, save=True):
        self.__game_log = logging.getLogger(__class__.__name__)
        self.players: list[Player] = []
        self.game_name = "IMPOSSIBLE GAME"
        self._winners = []
        self.losers: list[Player.__class__, int, Any] = []
        self.plays: list[list] = []
        self._turn = 0
        self._run = False
        self.__db: Database = None
        self.__save = save
        self.__register_players(nb_players, nb_ai, *players_names)

    def _init_db(self):
        self.__db = Database(self.game_name or __class__.__name__)

    def __register_players(self, number_of_players, number_of_ai, *players_names):
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
        for pile in self.plays:
            json_pile = []
            for card in pile:
                json_pile.append(card.unicode_safe())
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

    def save_results(self, name) -> (dict | None):
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

    def register(self, player: Player) -> None:
        if not isinstance(player, (AI, Player)):
            raise ValueError(f"{player} not a Player")
        self.__game_log.info(f"{player} registered to the game")
        player.reset()  # Ensure player is set to default when joining the game
        player.set_game(self)  # important to remind: self is a reference to last sub_class in MRO
        self.players.append(player)

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
                         "last_play": player_infos[2]
                         } for i, player_infos in enumerate(self._winners)]
        return rank_gen

    def _reset_winner(self):
        self._winners = []

    def show_winners(self):
        print("".join(["#" * 15, "WINNERS", "#" * 15]))
        for winner in self.winners():
            print(winner)

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

    @abstractmethod
    def _initialize_game(self):
        """ Reset loser queue """
        self.__game_log.info(' '.join(["#" * 15, "PREPARING NEW GAME", "#" * 15]))
        self.__save and self._init_db()
        self.losers = []

    @abstractmethod
    def start(self, override_test=False):
        self._init_db()

    @abstractmethod
    def player_lost(self, player):
        pass
