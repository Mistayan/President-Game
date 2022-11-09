import unittest

from models import Human
from models.game import PresidentGame
from models.player import Player


class TestPlayers(unittest.TestCase):
    def test_player_constructor(self):
        player_trump = Human('Trump')
        self.assertTrue(player_trump.name == 'Trump')

    def test_incognito_player_should_have_random_name(self):
        player_incognito = Human()
        self.assertFalse(player_incognito.name == '')

    def test_player_is_active(self):
        player = Human()
        self.assertTrue(player.is_active)
        player.set_fold()
        self.assertFalse(player.is_active)
        player.set_fold(False)
        player.set_played()
        self.assertFalse(player.is_active)
        player.set_played(False)
        player.set_win()
        self.assertFalse(player.is_active)


class TestGame(unittest.TestCase):
    def test_default_game_has_three_players(self):
        game = PresidentGame(skip_inputs=True)
        self.assertTrue(len(game.players) == 3)

    def test_game_launch_distributes_cards(self):
        """ Game generation should distribute cards as evenly as possible. """
        game = PresidentGame(3, 0, skip_inputs=True)
        player_1 = game.players[0]
        player_2 = game.players[1]
        player_3 = game.players[2]
        self.assertTrue(len(player_1.hand) > 0)
        self.assertTrue(len(player_1.hand) >= len(player_2.hand))
        self.assertFalse(len(player_1.hand) == len(player_2.hand) == len(player_3.hand))

    def test_game_human_or_ai(self):
        """ verifies that AI are not humans """
        game = PresidentGame(1, 2, skip_inputs=True)
        human = game.players[0]
        ai_1 = game.players[1]
        ai_2 = game.players[2]
        self.assertTrue(human.is_human)
        self.assertFalse(ai_1.is_human)
        self.assertFalse(ai_2.is_human)

    def test_game_player_give_card(self):
        """
         Player giving a card should have 1 less card,
         self receiving should have 1 more card, which is the given card
        """
        game = PresidentGame(3, 0, skip_inputs=True)
        player_1: Player = game.players[0]
        player_2 = game.players[1]
        p1_copy = player_1.hand[::]
        p2_copy = player_2.hand[::]
        ori_len_1 = len(p1_copy)
        ori_len_2 = len(p2_copy)
        card = player_1.hand[0]
        game.player_give_card_to(player_1, card, player_2)

        # Ensure both players hands changes
        self.assertNotEqual(ori_len_1, len(player_1.hand))
        self.assertNotEqual(player_1.hand, p1_copy)
        self.assertNotEqual(ori_len_2, len(player_2.hand))
        self.assertNotEqual(player_2.hand, p2_copy)
        self.assertTrue(card in player_2.hand)  # __eq__


if __name__ == '__main__':
    unittest.main()
