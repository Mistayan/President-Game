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
    possible_rank: Final = ["President", "Vice-President", "Neutre", "Vice-Trouduc", "Trouduc"]
    rank: int
    rank_name: str

    def __init__(self, n, players):
        """ Ranks classifications for President Game """
        self.rank = n
        _max = len(players)
        current_player = players[n - 1]
        if _max < 3 or _max > 6:
            raise CheaterDetected()

        # 'Neutre' can only be a valid state whenever there is an odd number of players
        # Or when there is 6 players
        neutral = _max % 2 and n in (2, 3, 4)
        # President is always the first player
        president = n == 1
        # Vice-president  and Vice-trouduc only exists if _max > 3
        vice_president = _max > 3 and n == 2
        vice_trouduc = _max > 3 and n == _max - 1
        # Trouduc is the last player:
        trouduc = n == _max

        if neutral:
            self.rank_name = self.possible_rank[2]
        if president or vice_president:
            self.rank_name = self.possible_rank[n - 1]
        if vice_trouduc or trouduc:
            self.rank_name = self.possible_rank[::-1][_max - n]
        try:
            self.rank_name
        except:
            self.rank_name = "CHEATER"
            raise CheaterDetected("No such Rank")
        current_player.rank = self

    def __str__(self):
        return self.rank_name
