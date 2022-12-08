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

from rules import GameRules
from .card import Card

logger = logging.getLogger(__name__)


class Deck:
    """ Class to hold Cards, according to rules """
    __NUMBER_OF_CARDS: Final = len(GameRules.VALUES) * len(GameRules.COLORS)

    def __init__(self):
        """
        Generate a Deck with 52 cards. (4 colors, 13 values)
        """
        logger.info("Generating Deck of %s cards.", self.__NUMBER_OF_CARDS)
        self.cards = [Card(value, color)
                      for color in GameRules.COLORS for value in GameRules.VALUES]

    def shuffle(self) -> Deck:
        """Not the most optimized shuffle"""
        random.shuffle(self.cards)
        return self

    def __str__(self):
        """ return class as string """
        return self.cards  # call card.__repr__() on each one
