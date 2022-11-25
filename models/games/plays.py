# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/25/22
"""
from abc import ABC, abstractmethod


class GamePlay(ABC):
    """ Base Play class for Game """
    @abstractmethod
    def unicode_safe(self):
        """ Every Game-Plays MUST have a unicode_safe method for json exchanges """
        pass
