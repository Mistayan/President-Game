# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import logging
import unittest

import coloredlogs

from tests import TestGame, TestCards, TestDeck, TestPlayers, TestPresidentGame
# from tests.test_interfaces import TestInterfaces


class TestAll(unittest.TestCase):
    """ Test every aspect of the project"""
    def test_1(self):
        """ test cards and deck for card games """
        TestCards()
        TestDeck()

    def test_2(self):
        """ test players and base game """
        TestPlayers()
        TestGame()

    def test_3(self):
        """ Test president game """
        TestPresidentGame()

    # Tests above are considered to be tests for core functionalities
    # def test_4(self):
    #     """ Tests interfaces """
    #     TestInterfaces()


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    unittest.main()
