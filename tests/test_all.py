# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import unittest

from .test_exercice1 import TestCardsExercice1, TestDeckExercice1
from .test_exercice2 import TestPlayers, TestGame
from .test_exercice3 import TestGameExercice3


class TestAll(unittest.TestCase):

    def test_1(self):
        TestCardsExercice1()
        TestDeckExercice1()

    def test_2(self):
        TestPlayers()
        TestGame()

    def test_3(self):
        TestGameExercice3()


if __name__ == '__main__':
    unittest.main()
