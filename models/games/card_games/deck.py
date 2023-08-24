# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/19/22
"""
from __future__ import annotations

import logging
import random
from typing import Final

from rules import CardGameRules
from .card import Card

logger = logging.getLogger(__name__)


class Deck:
    """ Class to hold Cards, according to rules """
    __NUMBER_OF_CARDS: Final = len(CardGameRules.VALUES) * len(CardGameRules.COLORS)

    def __init__(self, rules: CardGameRules = None):
        """
        Generate a Deck with 52 cards. (4 colors, 13 values)
        """
        if not rules:
            raise ValueError("No rules given to Deck.")
        logger.info("Generating Deck of %s cards.", self.__NUMBER_OF_CARDS)
        self.cards = [Card(value, color)
                      for color in CardGameRules.COLORS for value in CardGameRules.VALUES]

    def shuffle(self) -> Deck:
        """Not the most optimized shuffle"""
        random.shuffle(self.cards)
        return self

    def __str__(self):
        """ return class as string """
        return self.cards  # call card.__repr__() on each one
