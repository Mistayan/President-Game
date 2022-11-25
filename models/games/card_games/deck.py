from __future__ import annotations

import logging
import random
from typing import Final

from models.games.card_games import Card
from rules import GameRules

logger = logging.getLogger(__name__)


class Deck:
    __number_of_cards: Final = len(GameRules.VALUES) * len(GameRules.COLORS)

    def __init__(self):
        """
        Generate a Deck with 52 cards. (4 colors, 13 values)
        """
        logger.info(f"Generating Deck of {self.__number_of_cards} cards.")
        self.cards = [Card(value, color)
                      for color in GameRules.COLORS for value in GameRules.VALUES]

    def shuffle(self) -> Deck:
        """Not the most optimized shuffle"""
        random.shuffle(self.cards)
        return self

    def __str__(self):
        return [card for card in self.cards]  # call card.__repr__() on each one
