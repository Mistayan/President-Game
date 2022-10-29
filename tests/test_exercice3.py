import unittest

import models
from models import PresidentGame, Player, VALUES
from models.utils import player_give_card_to


class TestCardsExercice3(unittest.TestCase):
    def test_revolution(self):
        game = PresidentGame(3, 0, "Ste")
        initial_values = VALUES[::]
        strongest_before = game.strongest_card
        game.set_revolution()
        # After revolution, values should be reversed
        strongest_after = game.strongest_card
        self.assertNotEqual(strongest_before, strongest_after)
