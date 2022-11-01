import unittest

from models import PresidentGame


class TestGameExercice3(unittest.TestCase):

    def test_winner_ladder_no_neutrals(self):
        game = PresidentGame(2, 2)
        for player in game.players:
            game.increment_round()
            game.set_win(player)

        ladder = [winner for winner in game.winners()]
        # scanning for "round -> rank"
        self.assertRegex(str(ladder), "1 -> Pres")
        self.assertRegex(str(ladder), "2 -> Vice-P")
        self.assertRegex(str(ladder), "3 -> Trouf")
        self.assertRegex(str(ladder), "4 -> Vice-T")
        self.assertNotRegex(str(ladder), "-> Neut")

    def test_winner_ladder_two_neutrals(self):
        game = PresidentGame(4, 2)
        for player in game.players:
            game.increment_round()
            game.set_win(player)
        ladder = [winner for winner in game.winners()]
        # scanning for "round -> rank"
        self.assertRegex(str(ladder), "1 -> Pres")
        self.assertRegex(str(ladder), "2 -> Vice-P")
        self.assertRegex(str(ladder), "3 -> Neut")
        self.assertRegex(str(ladder), "4 -> Neut")
        self.assertRegex(str(ladder), "5 -> Vice-T")
        self.assertRegex(str(ladder), "6 -> Trouf")


    def test_revolution(self):
        game = PresidentGame(3, 0, "Mistayan")
        strongest_before = game.strongest_card
        game.set_revolution()
        # After revolution, values should be reversed
        strongest_after = game.strongest_card
        self.assertNotEqual(strongest_before, strongest_after)
