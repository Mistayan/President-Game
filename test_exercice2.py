import unittest
import models

class TestCardsExercice2(unittest.TestCase):
    def test_player_constructor(self):
        player_trump = models.Player('Trump')
        self.assertTrue(player_trump.name == 'Trump')

    def test_incognito_player_should_have_random_name(self):
        player_incognito = models.Player()
        self.assertFalse(player_incognito.name == '')

    def test_default_game_has_three_players(self):
        game = models.PresidentGame()
        self.assertTrue(len(game.players) == 3)

    def test_game_launch_distributes_cards(self):
        """ Game generation should distribute cards evenly. """
        game = models.PresidentGame()
        player_1 = game.players[0]
        player_2 = game.players[1]
        print(player_1.hand)
        self.assertTrue(len(player_1.hand) > 0)
        self.assertTrue(len(player_1.hand) >= len(player_2.hand))

if __name__ == '__main__':
    unittest.main()
