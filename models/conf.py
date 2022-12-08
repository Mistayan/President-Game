# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 26/10/22
Function : Initialize logger, seed and prevail STATIC references
"""
from __future__ import annotations

import logging
import os
import platform
import random
from typing import Final

import coloredlogs

coloredlogs.install()
coloredlogs.set_level(logging.CRITICAL)
random.SystemRandom().seed("no_AI_allowed")
ROOT_LOGGER: Final = logging.getLogger("ROOT_LOGGER")
BASEDIR = os.path.abspath(os.getcwd())
ENV_NAME = "venv"
SYSTEM = platform.system()
if SYSTEM not in ("Windows", "POSIX"):
    raise OSError("Unknown OS type, cannot execute. Please contact software maintainer")
VENV_PATH = os.path.join(BASEDIR, ENV_NAME,
                         "Scripts" if SYSTEM == "Windows" else "bin",  # if not windows, POSIX
                         )
VENV_PYTHON = os.path.join(VENV_PATH,
                           "python")
