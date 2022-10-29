from __future__ import annotations
import logging
import random
from typing import Final

from .conf import VALUES, COLORS
from .card import Card

logger = logging.getLogger(__name__)


class Deck:
    __number_of_cards: Final = len(VALUES) * len(COLORS)

    def __init__(self):
        """
        Generate a Deck with 52 cards. (4 colors, 13 values)
        """
        self.cards = []
        logger.info(f"Generating Deck")
        for color in COLORS:
            for value in VALUES:
                self.cards.append(Card(value, color))

    def shuffle(self) -> Deck:
        """Not the most optimized shuffle"""
        random.shuffle(self.cards)
        return self

    def __str__(self):
        return [card for card in self.cards]  # call card.__repr__() on each one
