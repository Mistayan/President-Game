import unittest

from models import PresidentGame


class TestGameExercice3(unittest.TestCase):

    def test_winner_ladder_no_neutrals(self):
        game = PresidentGame(2, 2)
        p1 = game.players[0]
        p2 = game.players[1]
        p3 = game.players[2]
        p4 = game.players[3]
        game.set_win(p1)
        game.set_win(p2)
        game.set_win(p3)
        game.set_win(p4)
        ladder = [winner for winner in game.winners()]
        self.assertNotRegex(str(ladder), "Neutre")

    def test_winner_ladder_two_neutrals(self):
        game = PresidentGame(2, 3)
        p1 = game.players[0]
        p2 = game.players[1]
        p3 = game.players[2]
        p4 = game.players[3]
        p5 = game.players[4]
        game.set_win(p1)
        game.set_win(p2)
        game.set_win(p3)
        game.set_win(p4)
        game.set_win(p5)
        ladder = [winner for winner in game.winners()]
        print(ladder)
