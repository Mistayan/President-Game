import unittest

from models import PresidentGame


class TestGameExercice3(unittest.TestCase):

    def test_winner_ladder_no_neutrals(self):
        game = PresidentGame(2, 2)
        for player in game.players:
            game.increment_round()
            game.set_win(player)
            game._run = False

        ladder = game.winners()
        # scanning for "round -> rank"
        print(ladder)
        self.assertRegex(str(ladder), "Pres")
        self.assertRegex(str(ladder), "Vice-P")
        self.assertRegex(str(ladder), "Vice-T")
        self.assertRegex(str(ladder), "Trouf")
        self.assertNotRegex(str(ladder), "Neut")

    def test_winner_ladder_two_neutrals(self):
        game = PresidentGame(4, 2)
        for player in game.players:
            game.increment_round()
            game.set_win(player)
            game._run = False
        ladder = [winner for winner in game.winners()]
        # scanning for "round -> rank"
        self.assertRegex(str(ladder), "Pres")
        self.assertRegex(str(ladder), "Vice-P")
        self.assertRegex(str(ladder), "Neut")
        self.assertRegex(str(ladder), "Neut")
        self.assertRegex(str(ladder), "Vice-T")
        self.assertRegex(str(ladder), "Trouf")

    def test_revolution(self):
        game = PresidentGame(3, 0, "Mistayan")
        strongest_before = game.strongest_card
        game.set_revolution()
        # After revolution, values should be reversed
        strongest_after = game.strongest_card
        self.assertNotEqual(strongest_before, strongest_after)

    def test_one_game_3_AIs(self):
        # the simple fact that it runs until the end is proof
        game = PresidentGame(0, 3, skip_inputs=1)
        game.game_loop()

    def test_two_games_3_AIs_one_exchange(self):
        # the simple fact that it runs until the end is proof
        game = PresidentGame(0, 3, skip_inputs=2)
        game.game_loop()

    def test_three_games_3_AIs(self):
        # the simple fact that it runs until the end is proof
        game = PresidentGame(0, 3, skip_inputs=3)
        game.game_loop()


