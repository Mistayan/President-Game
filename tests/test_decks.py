"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/17/22
"""
import logging
import unittest

import coloredlogs

from models.games.card_games.deck import Deck
from models.utils import measure_perf


class TestDeck(unittest.TestCase):
    """ Test many aspects of Deck class """
    @measure_perf
    def test_deck_has_52_cards(self):
        """ A basic card game has 52 cards """
        deck = Deck()
        self.assertEqual(len(deck.cards), 52, 'The president is a card game '
                                              'requiring 52 cards')

    @measure_perf
    def test_deck_shuffling(self):
        """ after shuffle, cards are not positioned the same """
        deck_1 = Deck()
        deck_2 = Deck()
        self.assertEqual(deck_1.cards, deck_2.cards,
                         'A new deck should not be automatically shuffled')
        deck_2.shuffle()
        self.assertNotEqual(deck_1.cards, deck_2.cards, 'Shuffling a deck randomizes the '
                                                        'cards order')


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    unittest.main()
