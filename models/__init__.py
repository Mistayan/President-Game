# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 26/10/22
"""
import os

import colorama as colorama

from .conf import ENV_NAME
# sub_modules MUST be in MRO order !!!

from .conf import ROOT_LOGGER, BASEDIR
from .games import CardGame, PresidentGame, Card, CheaterDetected
from .players import Player, AI, Human

