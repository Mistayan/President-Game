# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/20/22
"""

# -*- coding: utf-8 -*-
import os
from types import MappingProxyType
from typing import Final

import coloredlogs

version = (1, 0, 0)

SERVER_HOST = '0.0.0.0'  # Allows distant access
SERVER_PORT = '5001'

BASEDIR = os.path.abspath(os.getcwd())
DB_TYPE = os.environ.get("DATABASE_TYPE", "sqlite")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "game_db")
DATABASE_USER = os.environ.get("DATABASE_USER", "user")
DATABASE_PASS = os.environ.get("DATABASE_PASS", "password")

if DB_TYPE != "sqlite":
    DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.environ.get("DATABASE_PORT", "5432")
else:
    DATABASE_HOST, DATABASE_PORT = None, None
VERBOSITY_COUNT_TO_LEVEL: Final = MappingProxyType({
    0: "CRITICAL",
    1: "ERROR",
    2: "INFO",
    3: "WARNING",
    4: "DEBUG",
})

DEBUG_LEVEL: Final = VERBOSITY_COUNT_TO_LEVEL[2]  # prod config
coloredlogs.install(DEBUG_LEVEL)
