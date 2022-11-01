# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
from typing import Final

from models.Errors import CheaterDetected
from models.player import Player


class PresidentRank:
    __possible_rank: Final = ["President", "Vice-President",  # positive advantages
                              "Neutre",  # Neutral advantages
                              "Vice-Trouffion", "Trouffion"]  # negative advantages

    __advantages: Final = [2, 1, 0, -1, -2]
    rank: int
    rank_name: str
    players = []  # Classes Instances shared attribute

    def __init__(self, n, players: list[Player]):
        """ Ranks classifications for President Game """
        self.rank = n
        self.players = players if not self.players else self.players
        _max = len(self.players)
        self.current_player = players[n - 1]
        if _max < 3 or _max > 6:
            raise CheaterDetected()

        # 'Neutre' can only be a valid state whenever there is an odd number of players
        # Or when there is 6 players
        neutral = (_max % 2 or _max == 6) and n in (2, 3, 4)
        # President is always the first player
        president = n == 1
        # Vice-president  and Vice-trouduc only exists if _max > 3
        vice_president = _max > 3 and n == 2
        vice_trouduc = _max > 3 and n == _max - 1
        # Trouduc is the last player:
        trouduc = n == _max

        if neutral:
            self.rank_name = self.__possible_rank[2]
        if president or vice_president:
            self.rank_name = self.__possible_rank[n - 1]
        if vice_trouduc or trouduc:
            self.rank_name = self.__possible_rank[::-1][_max - n]
        try:
            self.rank_name
        except AttributeError:  # Attribute not set means no possible rank found
            self.rank_name = "CHEATER"
            raise CheaterDetected("No such Rank")
        print(f"{self.current_player}'s rank -> {self}")
        self.current_player.set_rank(self)  # Give pointer

    @property
    def advantage(self) -> int:
        """
        :return: the current rank's advantage as number_of_cards: int
        """
        index = self.__possible_rank.index(self.rank_name)
        return self.__advantages[index]

    def __str__(self):
        return self.rank_name
