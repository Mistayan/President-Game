"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import logging
import unittest
from collections import Counter

import coloredlogs

from models import CheaterDetected
from models import PresidentGame, Card
from models.utils import measure_perf
from rules import GameRules, PresidentRules


class TestPresidentGame(unittest.TestCase):
    """ Test all PresidentGame conditions and methods """
    PresidentRules.EXTREME_RANKS = {"give": 2,  # card
                                    "above": 4,
                                    # players // Changing this value will affect medium ranks
                                    "else": 1,  # cards
                                    }

    # Medium = vice-vice
    PresidentRules.MEDIUM_RANKS = {"exists_above": PresidentRules.EXTREME_RANKS["above"],
                                   # players
                                   "give": 1,  # card
                                   }

    # Rankings names and their rewards
    PresidentRules.RANKINGS = {"President": None,  # To be defined on each game, if players leave
                               "Vice-President": PresidentRules.MEDIUM_RANKS["give"],
                               "Neutre": 0,
                               "Vice-Troufion": PresidentRules.MEDIUM_RANKS["give"],
                               "Troufion": None,  # To be defined on each game, if players leave
                               }

    @measure_perf
    def test_winner_ladder_no_neutrals(self):
        """ 4 players default should be President, neutre, neutre, Troufion """
        game = PresidentGame(nb_players=0, nb_ai=4, nb_games=1, save=True)
        game._initialize_game()
        game._play_game()
        ladder = game.winners()
        print(ladder)
        # scanning for "round -> rank"
        self.assertRegex(str(ladder), "Pres")
        self.assertNotRegex(str(ladder), "Vice-P")
        self.assertNotRegex(str(ladder), "Vice-T")
        self.assertRegex(str(ladder), "Trouf")
        self.assertRegex(str(ladder), "Neut")

    @measure_perf
    def test_winner_ladder_two_neutrals(self):
        """ Ensure ladder give ranks as Expected"""
        game = PresidentGame(nb_players=0, nb_ai=6, nb_games=True, save=True)
        game._initialize_game()
        game._play_game()
        ladder = game.winners()
        # scanning for "round -> rank"
        self.assertRegex(str(ladder), "Pres")
        self.assertRegex(str(ladder), "Vice-P")
        self.assertRegex(str(ladder), "Neut")
        self.assertRegex(str(ladder), "Neut")
        self.assertRegex(str(ladder), "Vice-T")
        self.assertRegex(str(ladder), "Trouf")

    @measure_perf
    def test_revolution(self):
        """ Ensure revolution happens when requested """
        game = PresidentGame(1, 4, "Mistayan", nb_games=1, save=False)
        strongest_before = game.strongest_card
        GameRules.USE_REVOLUTION = True
        game.set_revolution()
        # After revolution, values should be reversed
        self.assertNotEqual(strongest_before, game.strongest_card)

        game.set_revolution()
        GameRules.USE_REVOLUTION = False
        self.assertEqual(strongest_before, game.strongest_card)

    @measure_perf
    def test_one_game_3_AIs_with_ladder(self):
        """ Test that winners() triggers as soon as game is over """
        # the simple fact that it runs until the end is proof
        game = PresidentGame(nb_players=0, nb_ai=3, nb_games=1, save=True)
        game._initialize_game()
        self.assertRaises(RuntimeWarning, game.winners)
        game._play_game()
        self.assertIsNotNone(game.winners())

    @measure_perf
    def test_one_game_with_exchange___3_AIs(self):
        """ Test may fail because AI is dumb... given bad instructions
        Ensure exchanges are made properly (AI tested, human is expected to behave almost the same)
        """
        # the simple fact that it runs until the end is a proof in itself
        game = PresidentGame(nb_players=0, nb_ai=3, nb_games=2, save=False)
        game._initialize_game()
        game._play_game()
        total = 0
        for pile in game.plays:
            total += len(pile)
        for player in game.players:
            total += len(player.hand)
        self.assertEqual(total, 52)  # Ensure no cards disappeared from the game
        game.winners()
        game._initialize_game()
        players_before = [Counter(player.hand_as_numbers) for player in game.players]
        game.do_exchanges()
        players_after = [Counter(player.hand_as_numbers) for player in game.players]
        for i, p in enumerate(game.players):
            if p.rank.advantage:
                # This may fail in some rare cases where a player gives back the card he received
                self.assertNotEqual(players_before[i], players_after[i],
                                    "after exchanges, players should not have the same hand")
            else:
                self.assertEqual(players_before[i], players_after[i],
                                 "Neutres should not have given cards")

    @measure_perf
    def test_trigger_cheater_detected(self):
        """
        Ensure Cheaters block the game.
        In the future, it will have to ensure that this player has been kicked and voided"""
        self.assertRaises(CheaterDetected)

    @measure_perf
    def test_do_play(self):
        """ assert if a card can be played or not given different circumstances"""
        game = PresidentGame(0, 3, nb_games=1)
        game._initialize_game()
        player = game.players[0]
        player.hand = []
        player.add_to_hand(Card("2", '♥'))
        # Ensure a card from outside the game cannot be played. (YOU WOULD NOT KNOW !!)
        self.assertRaises(CheaterDetected, game._do_play, 0, player, player.hand)
        player2 = game.players[1]
        # Ensure a player with cards from the game can play them all
        self.assertTrue(game._do_play(1, player2, player2.hand))

    @measure_perf
    def test_next_player(self):
        """ test if next player is the one expected """
        game = PresidentGame(nb_players=0, nb_ai=3)
        GameRules.QUEEN_OF_HEART_STARTS = True
        game._initialize_game()
        game.__queen_of_heart_starts()

        first_player_index, first_player = game._next_player
        first_player.set_played()  # simulate action
        self.assertTrue(first_player.played)

        second_player_index, second_player = game._next_player
        self.assertNotEqual(first_player_index, second_player_index, "second player should not be the same as the first")
        second_player.set_played()  # simulate action

        third_player_index, third_player = game._next_player
        self.assertNotEqual(second_player_index, third_player_index, "next player should not be the same as the last")
        self.assertNotEqual(first_player_index, third_player_index, "last player should not be the same as the first")


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    unittest.main()
