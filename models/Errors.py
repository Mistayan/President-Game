# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import logging
from typing import Final

critical: Final = "".join(["\n", "🚨" * 25, "\n"])


class CheaterDetected(Exception):

    def __init__(self, e=None):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)
        logger.critical("".join([critical, str(e), critical]))
        raise Exception(e)


class PlayerNotFound(Exception):

    def __init__(self, e):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)
        logger.critical("".join([critical, f"Player Not Found : {str(e)}", critical]))
        raise Exception(e)
