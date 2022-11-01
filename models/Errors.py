# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/01/22
"""
import logging

from models import root_logger


class CheaterDetected(Exception):
    critical = ["🚨\t" * 25]

    def __init__(self, e=None):
        root_logger.setLevel(logging.CRITICAL)
        root_logger.critical("🚨".join(self.critical + str(e).split() + self.critical))
