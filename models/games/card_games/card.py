# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 01/10/22
"""

from __future__ import annotations

from models.networking.plays import GamePlay
from rules import CardGameRules


class Card(GamePlay):
    """ CardGame's Play Type"""

    def __init__(self, *args, **kwargs):
        """
        Instantiate a Card for a Deck
        :param number: the strength of the card
        :param color: the color of the card
        """
        number, color = self.validate(*args, **kwargs)
        self.number = number
        self.color = color

    @staticmethod
    def validate(*args, **kwargs):
        """ validate if num and color are valid inputs """
        assert len(args) == 2 or len(kwargs) == 2
        num, color = args or kwargs
        if str(num) not in CardGameRules.VALUES:
            raise ValueError(f"Card number is not in {CardGameRules.VALUES}")
        if color not in CardGameRules.COLORS:
            raise ValueError(f"Card color must be in {CardGameRules.COLORS}")
        return num, color

    def __eq__(self, other):
        """ test card's numbers equity (see __ne__ for value & color comparison) """
        if not other:
            raise ValueError("Cannot compare to Empty Element")
        self_value = CardGameRules.VALUES.index(self.number)
        other_value = CardGameRules.VALUES.index(other.number) if isinstance(other, Card) else \
            CardGameRules.VALUES.index(other)
        return self_value == other_value

    def __ne__(self, other):
        """ Ensure cards have different number and color"""
        if not other:
            raise ValueError("Cannot compare to Empty Element")
        if not isinstance(other, type(self)):
            raise ValueError("Cards.__ne__ requires Cards to compare")
        self_color = list(CardGameRules.COLORS).index(self.color)
        other_color = list(CardGameRules.COLORS).index(other.color)
        return not self == other and not self_color == other_color

    def __gt__(self, other):
        """ Compare values of cards """
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = CardGameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_value = CardGameRules.VALUES.index(other.number)
        else:
            other_value = CardGameRules.VALUES.index(other)
        return self_i > other_value

    def __ge__(self, other):
        """ Compare values of cards """
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = CardGameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_i = CardGameRules.VALUES.index(other.number)
        else:
            other_i = CardGameRules.VALUES.index(other)
        return self_i >= other_i

    def __lt__(self, other):
        """ Compare values of cards """
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = CardGameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_i = CardGameRules.VALUES.index(other.number)
        else:
            other_i = CardGameRules.VALUES.index(other)
        return self_i < other_i

    def __le__(self, other):
        """ Compare values of cards """
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = CardGameRules.VALUES.index(self.number)
        if isinstance(other, Card):
            other_i = CardGameRules.VALUES.index(other.number)
        else:
            other_i = CardGameRules.VALUES.index(other)
        return self_i <= other_i

    def unicode_safe(self):
        """ Whenever you require unicode safe strings, use this method """
        return f"{self.number},{CardGameRules.COLORS[self.color]}"

    def __str__(self):
        """ Card as unsafe characters (prettier) """
        return f"{self.number}{self.color}"

    def __repr__(self):
        """ Card as unsafe characters (prettier) """
        return self.__str__()

    def same_as(self, card: Card):
        """ compare addresses in memory to assert the cards are strictly the same"""
        return self is card

    @staticmethod
    def from_unicode(unisafe_color):
        """ Transform cards unicode_safe color to unsafe """
        for key, value in CardGameRules.COLORS.items():
            if value == unisafe_color:
                return key
