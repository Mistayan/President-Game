import unittest

from models.card import Card
from models.deck import Deck


class TestCardsExercice1(unittest.TestCase):
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


class TestDeckExercice1(unittest.TestCase):
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
        self.assertNotEqual(deck_1.cards, deck_2.cards, 'Shuffling a deck '
                                                        'randomizes the '
                                                        'cards order')


if __name__ == '__main__':
    unittest.main()
