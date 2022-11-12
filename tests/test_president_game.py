import unittest

from models import PresidentGame, Card
from models.Errors import CheaterDetected
from rules import GameRules


class InvalidCard(Exception):
    def __init__(self, msg=""):
        raise Exception(msg)


class TestGameExercice3(unittest.TestCase):

    def test_winner_ladder_no_neutrals(self):
        game = PresidentGame(nb_players=0, nb_ai=4, nb_games=True, save=True)
        game.start(override_test=True)

        print(game._winners)
        ladder = game.winners()
        # scanning for "round -> rank"
        print(ladder)
        self.assertRegex(str(ladder), "Pres")
        self.assertRegex(str(ladder), "Vice-P")
        self.assertRegex(str(ladder), "Vice-T")
        self.assertRegex(str(ladder), "Trouf")
        self.assertNotRegex(str(ladder), "Neut")

    def test_winner_ladder_two_neutrals(self):
        game = PresidentGame(nb_players=0, nb_ai=6, nb_games=True, save=True)
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
        game = PresidentGame(1, 4, "Mistayan", nb_games=1, save=False)
        strongest_before = game.strongest_card
        GameRules.USE_REVOLUTION = True
        game.set_revolution()
        # After revolution, values should be reversed
        strongest_after = game.strongest_card
        self.assertNotEqual(strongest_before, strongest_after)

    def test_one_game_3_AIs_with_ladder(self):
        # the simple fact that it runs until the end is proof
        game = PresidentGame(nb_players=0, nb_ai=3, nb_games=1, save=True)
        game._initialize_game()
        game._play_game()
        self.assertIsNotNone(game.winners())

    def test_two_games_3_AIs_one_exchange(self):
        # the simple fact that it runs until the end is a proof in itself
        game = PresidentGame(nb_players=0, nb_ai=3, nb_games=2, save=False)
        GameRules.LOSER_CAN_PLAY = True
        game.start(override_test=True)
        total = 0
        players_save = game.players.copy()
        for pile in game.plays:
            total += len(pile)
        for player in game.players:
            total += len(player.hand)
        self.assertEqual(total, 52)  # Ensure no cards disappeared from the game
        print(players_save)

    def test_trigger_CheaterDetected_Error(self):
        self.assertRaises(CheaterDetected)

    def test_do_play(self):
        game = PresidentGame(0, 3, nb_games=1)
        game._initialize_game()
        player = game.players[0]
        player.hand = []
        player.add_to_hand(Card("2", '♡'))
        # Ensure a card from outside the game cannot be played. (YOU WOULD NOT KNOW !!)
        self.assertRaises(CheaterDetected, game._do_play, 0, player, player.hand)
        player2 = game.players[1]
        # Ensure a player with cards from the game can play them all
        self.assertTrue(game._do_play(1, player2, player2.hand))

    def test_next_player(self):
        game = PresidentGame(0, 3)
        GameRules.QUEEN_OF_HEART_STARTS = True
        game._initialize_game()
        player_index = game.queen_of_heart_starts()
        i, prev = game.next_player.__next__()
        print(i, prev)
        self.assertTrue(player_index == i)
        prev.set_played()
        self.assertTrue(prev.played)
        first = True
        for i, p in game.next_player:  # ensure looping behavior
            if not p:
                # returned index should never be a player index if no player left standing
                self.assertTrue(i not in range(len(game.players)))
                break
            self.assertTrue(i == game.get_player_index(p))
            if first:
                first = not first
                self.assertFalse(player_index == i)
            p and p.set_played()
            game._skip_players = True  # optional ?