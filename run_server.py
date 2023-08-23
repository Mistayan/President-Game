# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/20/22
"""
import logging
import platform
from multiprocessing import Pool
from subprocess import Popen

import coloredlogs

from models import PresidentGame
from models import GameFinder
from conf import VENV_PATH, ROOT_LOGGER


def run_background(game):
    with Pool(processes=1, ) as pool:
        ROOT_LOGGER.info("starting %s", game.__qualname__)
        pool.apply_async(game().run_server())  # Game will find port to run on its own


def run_with_gunicorn(game, port):
    print("running with gunicorn")
    app = Popen(f"{VENV_PATH} gunicorn --bind 0.0.0.0:{port} wsgi:{game}".split())
    app.communicate()


def run_with_waitress(game, port):
    print("running with waitress")
    print(VENV_PATH)
    try:
        app = Popen(f"{VENV_PATH} waitress-serve"
                    f" --host 0.0.0.0 --port {port} --call models:{game}"
                    "".split())
        app.communicate()
    except PermissionError:
        print("Requires admin rights...")
        raise


def auto_run(game):
    system = platform.system()
    try:
        ROOT_LOGGER.info("Scanning for port to run to...")
        _, port = GameFinder(target="localhost").availabilities[0]
        try:
            if system == "Windows":
                run_with_waitress(game, port)
            elif system == "POSIX":
                run_with_gunicorn(game, port)
        except Exception:
            print("Failed to run properly, switching to base methods")
            run_background(game)
    except KeyboardInterrupt as e:
        print("Server Shutting down...")
        ROOT_LOGGER.critical(e)


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    auto_run(PresidentGame)

