import unittest

from models import PresidentGame
from models.Errors import CheaterDetected
from rules import GameRules


class TestGameExercice3(unittest.TestCase):

    def test_winner_ladder_no_neutrals(self):
        game = PresidentGame(0, 4, skip_inputs=True)
        game.start(override_test=True)

        print(game._rounds_winners)
        ladder = game.winners()
        # scanning for "round -> rank"
        print(ladder)
        self.assertRegex(str(ladder), "Pres")
        self.assertRegex(str(ladder), "Vice-P")
        self.assertRegex(str(ladder), "Vice-T")
        self.assertRegex(str(ladder), "Trouf")
        self.assertNotRegex(str(ladder), "Neut")

    def test_winner_ladder_two_neutrals(self):
        game = PresidentGame(0, 6, skip_inputs=True)
        game.start(override_test=True)
        ladder = [winner for winner in game.winners()]
        # scanning for "round -> rank"
        self.assertRegex(str(ladder), "Pres")
        self.assertRegex(str(ladder), "Vice-P")
        self.assertRegex(str(ladder), "Neut")
        self.assertRegex(str(ladder), "Neut")
        self.assertRegex(str(ladder), "Vice-T")
        self.assertRegex(str(ladder), "Trouf")

    def test_revolution(self):
        game = PresidentGame(3, 0, "Mistayan", skip_inputs=True)
        strongest_before = game.strongest_card
        GameRules.USE_REVOLUTION = True
        game.set_revolution()
        # After revolution, values should be reversed
        strongest_after = game.strongest_card
        self.assertNotEqual(strongest_before, strongest_after)

    def test_one_game_3_AIs(self):
        # the simple fact that it runs until the end is proof
        game = PresidentGame(0, 3, skip_inputs=True)
        game.game_loop()

    def test_three_games_3_AIs_no_exchanges(self):
        # the simple fact that it runs until the end is proof
        game = PresidentGame(0, 3, skip_inputs=3)
        game.game_loop()
        game._initialize_game()
        game._rounds_winners = []
        game.game_loop()
        game._initialize_game()
        game._rounds_winners = []
        game.game_loop()

    def test_two_games_3_AIs_one_exchange(self):
        # the simple fact that it runs until the end is a proof in itself
        game = PresidentGame(0, 3, skip_inputs=2)
        game.start(override_test=True)
        total = 0
        players_save = game.players.copy()
        for pile in game.last_rounds_piles:
            total += len(pile)
        for player in game.players:
            total += len(player.hand)
        self.assertEqual(total, 52)
        print(players_save)

    def test_trigger_CheaterDetected_Error(self):
        self.assertRaises(CheaterDetected)


