import logging
import unittest

import coloredlogs

from models.deck import Deck


class TestDeck(unittest.TestCase):
    def test_deck_has_52_cards(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52, 'The president is a card game '
                                              'requiring 52 cards')

    def test_deck_shuffling(self):
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
