# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/17/22
"""
import logging
import time
import unittest

import coloredlogs

from models import Human
from models.interfaces import Interface


class TestInterfaces(unittest.TestCase):
    """ In order to perform these tests, Game_Server MUST be running """
    player = Human()  # Player 1 is used to test basics functions
    interface = Interface(player=player)  # tie player to interface
    player2 = Human()  # Player 2 is used to test server behaviour when disconnecting IN-GAME
    interface2 = Interface(player2)

    def test_game_player_interface_connexions(self):
        """ test connection, disconnect, update when game not running """
        # game = CardGame(nb_players=0, nb_ai=2, nb_games=1, save=False)
        # Connect first time
        self.interface.connect("localhost", 5001)  # ask the interface to connect to the game
        self.assertIsNone(self.player.game)
        self.assertIsNotNone(self.interface.game_token, "Once connected, game sent a token")
        self.assertIsNotNone(self.interface.game_addr, "player should have a game addr registered")

        # Update first time
        response = self.interface.update()
        self.assertEqual(response.status_code, 200,
                         "Player is registered and should have access to his status on server")
        self.assertIsNone(self.player.game,
                          "Interface-Side player should never have a game-pointer")
        previous_len = len(self.interface.game_dict.get("players"))
        self.assertTrue(previous_len >= 3,
                        "after player registered, game have more than 2 initial players")
        self.assertEqual(self.interface.game_dict.get("players")[-1][0], self.player.name,
                         "player registered after AIs, last in line")

        # save previous token, to ensure it has been renewed
        token = self.interface.game_token

        # Disconnect first time
        self.interface.disconnect()
        self.assertIsNone(self.player.game,
                          "Interface-Side player should never have a game-pointer")

        response = self.interface.update()
        self.assertEqual(response.status_code, 404,
                         "After unregistered, server should not find the requested player")
        self.assertIsNone(self.player.game,
                          "Interface-Side player should never have a game-pointer")
        self.assertNotEqual(self.interface.game_dict.get("players")[-1][0], self.player.name,
                            "player unregistered should not appear in active players")
        self.assertEqual(len(self.interface.game_dict.get("disconnected")), 0,
                         "player unregistered while game is not running should be voided")
        self.assertNotEqual(len(self.interface.game_dict.get("players")), previous_len,
                            "after player unregistered, game have less players")
        #  test re-connect
        self.interface.connect("localhost", 5001)
        self.assertNotEqual(token, self.interface.game_token,
                            "After registration, token should have changed")
        response = self.interface.update()
        self.assertEqual(response.status_code, 200,
                         "Player should be able to re-connect")
        self.assertTrue(len(self.interface.game_dict.get("players")) == previous_len,
                        "Player just reconnected. Should appear in game")

    def test_h_second_player_joining_game_before_start(self):
        self.interface2.connect("localhost", 5001)  # ask the interface to connect to the game
        self.interface2.update()
        self.assertEqual(self.interface2.game_dict.get("players")[-1][0], self.player2,
                         "A player that joined before the game started should play")

    def test_interface_start_game(self):
        """Player cannot start a game if he is not registered with a token"""
        # Player already connected should not renew their token
        # self.interface.connect("localhost", 5001)  # ask the interface to connect to the game

        self.interface.send_start_game_signal()
        time.sleep(0.2)
        self.interface.update()
        self.assertTrue(self.interface.game_dict.get("running"),
                        "After game started, server should show 'running")
        self.assertNotEqual(self.player.hand, [],
                            "After game started, it should have distributed cards")
        self.assertIsNone(self.player.game)

    def test_second_player_disconnect_and_reconnect_after_game_started(self):
        """ MUST be run after game started and player 2 connected """
        self.assertEqual(self.interface2.update().status_code, 200,
                         "Connected player should be able to view his profile")
        self.assertTrue(self.interface.game_dict.get("running"),
                        "After game started, server should show 'running")
        self.interface2.disconnect()
        self.assertEqual(self.interface2.update().status_code, 404,
                         "Disconnected player should not be able to view his profile")
        self.interface2.connect("localhost", 5001)
        self.assertEqual(self.interface2.update().status_code, 200,
                         "Player re-joined and should be able to update")
        self.assertEqual(self.interface2.game_dict.get("players")[-1][0], self.player2,
                         "A player that joined before the game started should be able to re-join")

    def test_third_player_join_after_game_started(self):
        player3 = Human()
        interface3 = Interface(player3)
        interface3.connect("localhost", 5001)  # ask the interface to connect to the game
        self.assertEqual(interface3.update().status_code, 404,
                         "After game started, cannot update profile, since waiting")
        self.assertNotEqual(interface3.game_dict.get("awaiting"), [],
                            "A player that joined after the game started should be waiting")
        self.assertNotEqual(interface3.game_dict.get("players")[-1][0], player3,
                            "A player that joined after the game started should be waiting")


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    unittest.main()
