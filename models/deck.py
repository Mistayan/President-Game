import random
from typing import Final

from .card import Card


class Deck:
    __number_of_cards: Final = 52
    __values: Final = [str(num) for num in range(3, 11)] + ["J", "Q", "K", "A", "2"]
    __colors: Final = {'♡', '♦', '♤', '♣'}

    def __init__(self):
        """
        Generate a Deck with 52 cards. (4 colors, 13 values)
        """
        self.cards = []
        for color in self.__colors:
            for value in self.__values:
                self.cards.append(Card(value, color))

    def shuffle(self):
        """Not the most optimized shuffle"""
        return random.shuffle(self.cards)

    def __str__(self):
        return [card for card in self.cards]  # call card.__str__() on each one
