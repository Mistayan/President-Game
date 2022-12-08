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
    """ Define the game_rank name and advantage of a player.
    Depends on PresidentRules

    How to :
    player.game_rank = PresidentRank(
                                player's game_rank from game (int: 1-len(players)),
                                player,
                                len(in-game-players)
                                )
    """
    __POSSIBLE_RANKS: Final = [rank_name for rank_name in PresidentRules.RANKINGS]
    __RANK_ADVANTAGE: Final = [PresidentRules.RANKINGS[rank] for rank in __POSSIBLE_RANKS]

    def __init__(self, game_rank: int, player: Player, nb_players: int):
        """ Ranks classifications for President Game """
        self.logger = logging.getLogger(__class__.__name__)
        self.nb_players = nb_players
        self.logger.debug("nb_players : %d, currently requested game_rank: %s", nb_players, game_rank)
        if nb_players < 3 or nb_players > 6:
            raise CheaterDetected()

        # Vice-president and Vice-troufion Ranks exists ?
        vice_exists = nb_players > PresidentRules.MEDIUM_RANKS["exists_above"]

        # President is always the first player, vice-president is always second
        if game_rank == 1 or vice_exists and game_rank == 2:
            self.rank_name = self.__POSSIBLE_RANKS[game_rank - 1]
        # Troufion is always the last player, vice-troufion is always second last
        elif game_rank == nb_players or vice_exists and game_rank == nb_players - 1:
            self.rank_name = self.__POSSIBLE_RANKS[::-1][nb_players - game_rank]
        # Anyone else is supposed to be neutral
        else:
            self.rank_name = self.__POSSIBLE_RANKS[2]
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
            adv = - adv if self.rank_name == self.__POSSIBLE_RANKS[-1] else adv
        return adv

    def __str__(self):
        """ return rank's nomination """
        return self.rank_name

    def __repr__(self):
        """ return rank's nomination in listings"""
        return self.__str__()

    def __dict__(self):
        return {
            "rank": self.rank_name,
            "adv": self.advantage
        }
