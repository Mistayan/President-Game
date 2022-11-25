from __future__ import annotations

from models.games.plays import GamePlay
from rules import GameRules


class Card(GamePlay):

    def __init__(self, number, color):
        """
        Instantiate a Card for a Deck
        :param number: the strength of the card
        :param color: the color of the card
        """
        self.validate(number, color)
        self.number = number
        self.color = color

    @staticmethod
    def validate(num, color):
        """ validate if num and color are valid inputs """
        if str(num) not in GameRules.VALUES:
            raise ValueError(f"Card number is not in {GameRules.VALUES}")
        if color not in GameRules.COLORS:
            raise ValueError(f"Card color must be in {GameRules.COLORS}")

    def __eq__(self, other):
        """ test card's numbers equity (see __ne__ for value & color comparison) """
        if not other:
            raise ValueError("Cannot compare to Empty Element")
        self_value = GameRules.VALUES.index(self.number)
        other_value = GameRules.VALUES.index(other.number) if isinstance(other, Card) else \
            GameRules.VALUES.index(other)
        return self_value == other_value

    def __ne__(self, other):
        """ Ensure cards have different number and color"""
        if not other:
            raise ValueError("Cannot compare to Empty Element")
        if not isinstance(other, type(self)):
            raise ValueError("Cards.__ne__ requires Cards to compare")
        self_color = list(GameRules.COLORS).index(self.color)
        other_color = list(GameRules.COLORS).index(other.color)
        return not self == other and not self_color == other_color

    def __gt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = GameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_value = GameRules.VALUES.index(other.number)
        else:
            other_value = GameRules.VALUES.index(other)
        return self_i > other_value

    def __ge__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = GameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_i = GameRules.VALUES.index(other.number)
        else:
            other_i = GameRules.VALUES.index(other)
        return self_i >= other_i

    def __lt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = GameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_i = GameRules.VALUES.index(other.number)
        else:
            other_i = GameRules.VALUES.index(other)
        return self_i < other_i

    def __le__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = GameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_i = GameRules.VALUES.index(other.number)
        else:
            other_i = GameRules.VALUES.index(other)
        return self_i <= other_i

    def unicode_safe(self):
        """ Whenever you require unicode safe strings, use this method """
        return f"{self.number},{GameRules.COLORS[self.color]}"

    def __str__(self):
        return f"{self.number}{self.color}"

    def __repr__(self):
        return self.__str__()

    def same_as(self, card: Card):
        """ compare addresses in memory to assert the cards are strictly the same"""
        return self is card

    @staticmethod
    def from_unisafe(unisafe):
        for k, v in GameRules.COLORS.items():
            if v == unisafe:
                return k
