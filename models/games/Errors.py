# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import logging
from typing import Final

CRITICAL: Final = "".join(["\n", "!" * 25, "\n"])


class CheaterDetected(BaseException):
    """
    Exception Raised if a player is caught cheating
    """

    def __init__(self, e=""):
        super().__init__(e)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)
        logger.critical("".join([CRITICAL, str(e), CRITICAL]))
        raise self


class PlayerNotFound(BaseException):
    """
    Exception Raised if a player is not found amongst active players
    """

    def __init__(self, e):
        super().__init__(e)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)
        logger.critical("".join([CRITICAL, f"Player Not Found : {str(e)}", CRITICAL]))
        raise self
