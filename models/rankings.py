# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import logging
from typing import Final

from models.Errors import CheaterDetected
from models.player import Player


class PresidentRank:
    __possible_rank: Final = ["President", "Vice-President",  # positive advantages
                              "Neutre",  # Neutral advantages
                              "Vice-Troufion", "Troufion"]  # negative advantages

    __advantages: Final = [2, 1, 0, -1, -2]
    players = []  # Classes Instances shared attribute

    def __init__(self, n, player, players: list[Player]):
        """ Ranks classifications for President Game """
        self.logger = logging.getLogger(__class__.__name__)
        self.players = players if not self.players else self.players
        _max = len(self.players)
        self.logger.info(f"nb_players : {_max}, currently requested rank: {n}")
        if _max < 3 or _max > 6:
            raise CheaterDetected()

        # 'Neutre' can only be a valid state whenever there is an odd number of players
        # Or when there is 6 players
        neutral = (_max % 2 or _max == 6) and n in {2, 3, 4}
        # President is always the first player
        president = n == 1
        # Vice-president  and Vice-troufion only exists if _max > 3
        vice_president = _max > 3 and n == 2
        vice_troufion = _max > 3 and n == _max - 1
        # troufion is the last player:
        troufion = n == _max

        if neutral:
            self.rank_name = self.__possible_rank[2]
        if president or vice_president:
            self.rank_name = self.__possible_rank[n - 1]
        if vice_troufion or troufion:
            self.rank_name = self.__possible_rank[::-1][_max - n]
        try:
            self.rank_name
        except AttributeError:  # Attribute not set means no possible rank found
            self.rank_name = "CHEATER"
            raise CheaterDetected("No such Rank")
        player.set_rank(self)

    @property
    def advantage(self) -> int:
        """
        - 3 players -> 1 card to give for President / Troufion
        - 4+ players : 2 cards for President / Troufion and 1 card for Vice-...
        :return: the current rank's advantage as number_of_cards: int
        """
        index = self.__possible_rank.index(self.rank_name)
        self.logger.debug(f"index: {index} -> advantage of {self.__advantages[index]}")
        return self.__advantages[index] // 2 if len(self.players) <= 3\
            else self.__advantages[index]

    def __str__(self):
        return self.rank_name

    def __repr__(self):
        return self.__str__()
