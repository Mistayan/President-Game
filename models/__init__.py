# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 26/10/22
"""
import os

import colorama as colorama

from setup import ENV_NAME
# sub_modules MUST be in MRO order !!!

from .conf import ROOT_LOGGER, BASEDIR
from .games import CardGame, PresidentGame, Card, CheaterDetected
from .players import Player, AI, Human

if not os.path.exists(os.path.join(BASEDIR, ENV_NAME)):
    raise EnvironmentError("You MUST setup a virtual environment to use this project.\n"
                           f"{colorama.Fore.LIGHTGREEN_EX}"
                           f">>> python -m venv {ENV_NAME}\n"
                           f">>> activate\n"
                           ">>> pip install -r requirements.txt"
                           f"{colorama.Fore.RESET}")