# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import logging
from typing import Final

from models.games.Errors import CheaterDetected
from models.players.player import Player
from rules import PresidentRules


class PresidentRank:
    __possible_rank: Final = [rank_name for rank_name in PresidentRules.RANKINGS]
    __advantages: Final = [PresidentRules.RANKINGS[rank] for rank in __possible_rank]

    def __init__(self, n, player: Player, nb_players: int):
        """ Ranks classifications for President Game """
        self.logger = logging.getLogger(__class__.__name__)
        self.nb_players = nb_players
        self.logger.debug(f"nb_players : {nb_players}, currently requested rank: {n}")
        if nb_players < 3 or nb_players > 6:
            raise CheaterDetected()

        # Vice-president and Vice-troufion Ranks exists ?
        vice_exists = nb_players > PresidentRules.MEDIUM_RANKS["exists_above"]

        # President is always the first player, vice-president is always second
        if n == 1 or vice_exists and n == 2:
            self.rank_name = self.__possible_rank[n - 1]
        # Troufion is always the last player, vice-troufion is always second last
        elif n == nb_players or vice_exists and n == nb_players - 1:
            self.rank_name = self.__possible_rank[::-1][nb_players - n]
        # Anyone else is supposed to be neutral
        else:
            self.rank_name = self.__possible_rank[2]
        player.set_rank(self)

    @property
    def advantage(self) -> int:
        """
        advantages are re-evaluated on each game, so if a player disconnect, it works just fine.
        - 3 players -> 1 card to give for President / Troufion
        - 4+ players -> 2 cards for President / Troufion and 1 card for Vice-...
        ^^^^^^^^^^^^^ May vary depending on rules sets
        :return: the current rank's advantage as number_of_cards: int
        """
        adv = PresidentRules.RANKINGS.get(self.rank_name)
        if adv is None:  # president / troufion -> adv = None
            rnk = PresidentRules.EXTREME_RANKS
            adv = rnk["give"] if self.nb_players > rnk["above"] else rnk["else"]
            adv = - adv if self.rank_name == self.__possible_rank[-1] else adv
        return adv

    def __str__(self):
        return self.rank_name

    def __repr__(self):
        return self.__str__()
