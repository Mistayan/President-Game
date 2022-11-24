# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import logging
import unittest

import coloredlogs

from models import Card


class TestCards(unittest.TestCase):
    def test_card_constructor(self):
        self.assertTrue(isinstance(Card('A', '♡'), Card))

    def test_cards_equal_value(self):
        ace_of_hearts = Card('A', '♡')
        ace_of_spades = Card('A', '♤')
        self.assertEqual(ace_of_hearts, ace_of_spades, 'Two cards having '
                                                       'same value should be considered equal')

    def test_cards_comparison(self):
        ace_of_hearts = Card('A', '♡')
        two_of_hearts = Card('2', '♡')
        five_of_hearts = Card('5', '♡')

        self.assertTrue(ace_of_hearts > five_of_hearts)
        self.assertTrue(two_of_hearts > ace_of_hearts > five_of_hearts,
                        'The two card is the highest card')
        self.assertTrue(five_of_hearts < two_of_hearts,
                        'The two card is the highest card')

    def test_cards_strictly_the_same(self):
        ace_of_hearts = Card('A', '♡')
        ace_of_hearts2 = Card('A', '♡')
        two_of_hearts = Card('2', '♡')
        # a card is unique in a deck, no copies should be same_as.
        self.assertIs(ace_of_hearts.same_as(ace_of_hearts2), False)
        self.assertIs(ace_of_hearts.same_as(ace_of_hearts), True)
        self.assertIsNot(ace_of_hearts, ace_of_hearts2)
        self.assertIsNot(ace_of_hearts, two_of_hearts)


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    unittest.main()
