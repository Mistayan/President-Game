# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import unittest

from tests import *


class TestAll(unittest.TestCase):

    def test_1(self):
        TestCards()
        TestDeck()

    def test_2(self):
        TestPlayers()
        TestGame()

    def test_3(self):
        TestPresidentGame()


if __name__ == '__main__':
    unittest.main()
