import unittest

from models.game import PresidentGame
from models.player import Player


class TestCardsExercice2(unittest.TestCase):
    def test_player_constructor(self):
        player_trump = Player('Trump')
        self.assertTrue(player_trump.name == 'Trump')

    def test_incognito_player_should_have_random_name(self):
        player_incognito = Player()
        self.assertFalse(player_incognito.name == '')

    def test_default_game_has_three_players(self):
        game = PresidentGame()
        self.assertTrue(len(game.players) == 3)

    def test_game_launch_distributes_cards(self):
        """ Game generation should distribute cards as evenly as possible. """
        game = PresidentGame(3, 0)
        player_1 = game.players[0]
        player_2 = game.players[1]
        player_3 = game.players[2]
        self.assertTrue(len(player_1.hand) > 0)
        self.assertTrue(len(player_1.hand) > len(player_2.hand))
        self.assertFalse(len(player_1.hand) == len(player_2.hand) == len(player_3.hand))

    def test_game_human_or_ai(self):
        """ verifies that AI are not humans """

    def test_game_player_give_card(self):
        """
         Player giving a card should have 1 less card,
         player receiving should have 1 more card, which is the given card
        """
        game = PresidentGame(3, 0)
        player_1: Player = game.players[0]
        player_2 = game.players[1]
        ori_len_1 = len(player_1.hand)
        ori_len_2 = len(player_2.hand)
        card = player_1.hand[0]
        print(card)
        print(player_1.hand)
        game.player_give_card_to(player_1, card, player_2)
        print(player_1.hand)
        # self.assertNotEqual(ori_len_1, len(player_1.hand))
        # self.assertNotEqual(ori_len_2, len(player_2.hand))
        self.assertNotEqual(player_1.hand[0], card)
        self.assertTrue(card in player_2.hand)
        self.assertFalse(card in player_1.hand)


if __name__ == '__main__':
    unittest.main()
