from __future__ import annotations
import logging
import random
from typing import Final

from .card import Card

logger = logging.getLogger(__name__)


class Deck:
    __number_of_cards: Final = 52
    __values: Final = [str(num) for num in range(3, 11)] + ["J", "Q", "K", "A", "2"]
    __colors: Final = {'♡', '♦', '♤', '♣'}

    def __init__(self):
        """
        Generate a Deck with 52 cards. (4 colors, 13 values)
        """
        self.cards = []
        logger.info(f"Generating Deck")
        for color in self.__colors:
            for value in self.__values:
                self.cards.append(Card(value, color))

    def shuffle(self) -> Deck:
        """Not the most optimized shuffle"""
        random.shuffle(self.cards)
        return self

    def __str__(self):
        return [card for card in self.cards]  # call card.__repr__() on each one
