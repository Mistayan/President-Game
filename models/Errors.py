# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import logging


class CheaterDetected(Exception):
    critical = "".join("\n", "🚨" * 25, "\n")

    def __init__(self, e=None):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)
        logger.critical("".join([self.critical, str(e), self.critical]))
        raise Exception(e)
