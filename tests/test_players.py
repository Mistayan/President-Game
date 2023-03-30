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

from models import Human, Card
from models.utils import measure_perf


class TestPlayers(unittest.TestCase):
    """
    Test many aspects of player module to ensure everything works as expected
    """

    @measure_perf
    def test_player_constructor(self):
        """ ensure a player is built as expected """
        player_trump = Human('Trump')
        self.assertTrue(player_trump.name == 'Trump')

    @measure_perf
    def test_incognito_player_should_have_random_name(self):
        """ An Unnamed player should have a random name"""
        player_incognito = Human()
        self.assertFalse(player_incognito.name == '')

    @measure_perf
    def test_player_is_active(self):
        """ Test that a player is active depending on different cases """
        player = Human()
        self.assertTrue(player.is_human)
        self.assertTrue(player.is_active)
        player.set_fold()
        self.assertFalse(player.is_active)
        player.set_fold(False)
        player.set_played()
        self.assertFalse(player.is_active)
        self.assertTrue(player.played)
        player.set_played(False)
        player.set_win()
        self.assertFalse(player.is_active)
        player.set_played()
        self.assertFalse(player.is_active)
        player.set_win(False)
        player.set_fold()
        self.assertFalse(player.is_active)
        self.assertEqual(player.max_combo, 0)

    @measure_perf
    def test_player_hand(self):
        """ Ensure a player's hand behaves as expected """
        player = Human()
        self.assertRaises(ValueError, player.add_to_hand, "2")
        card = Card('2', '♥')
        player.add_to_hand(card)
        self.assertTrue(len(player.hand) == player.max_combo == 1)
        played: list[Card] = player._play_cli(n_cards_to_play=1, override="2")
        self.assertNotEqual(played, [],
                            "player only tell the game what they want to play,"
                            " and the game take the cards from player's hand.")
        self.assertTrue(card.same_as(played[0]))
        self.assertEqual(player.hand, [])
        player.add_to_hand(card)
        player.add_to_hand(card)  # Nothing tells us that we cannot have the same card twice
        self.assertEqual(player.hand, [card, card])


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    unittest.main()
