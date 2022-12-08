# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/26/22
"""
import os
import sys
from subprocess import Popen

from setuptools import setup

from models.conf import VENV_PYTHON, ENV_NAME, BASEDIR

if sys.argv and not len(sys.argv) >= 2:
    if not os.path.exists(os.path.join(BASEDIR, "venv")):
        print(f"Creating virtual environment : {ENV_NAME}")
        # communicate, so we know what happens
        init = Popen(f"python -m venv {ENV_NAME}".split()).communicate()  # <==
    print("Upgrading pip and wheel :\n"
          "\t- upgrading pip ensure you match last security standards \n"
          "\t- wheel is faster than pip, allowing smaller downloads and faster install")
    print(VENV_PYTHON)
    check_pip = Popen(f"{VENV_PYTHON} -m pip install --upgrade pip".split()).communicate()
    check_wheel = Popen(f"{VENV_PYTHON} -m pip install --upgrade wheel".split()).communicate()
    print("Applying requirements (Flask, names, requests, ...)")
    install = Popen(f"{VENV_PYTHON} -m pip install -r requirements.txt".split()).communicate()

    # argparse.ArgumentParser(
    #     prog="setup.py",
    #     exit_on_error=True,
    #     parents=[]
    #                         )
else:
    setup(
        name='Game-Servers-Generator',
        version='0.42.0',
        description="""For now, this is a simple Card Game with variance President Game.""",
        author='Mistayan',
        url='https://github.com/Mistayan/President-Game',
        author_email='helixmastaz@gmail.com',
        packages=['models',
                  'models.games',
                  'models.games.apis', 'models.games.card_games',
                  'models.games.card_games.variances',
                  'models.interfaces', 'models.players', ],
        requires=['Python (>=3.9)'],
        install_requires=[
            "coloredlogs>=15",
            "MarkupSafe>=2.1.1",
            "names==0.3.0",
            "Werkzeug==2.2.2",
            "Flask==2.2.2",
            "flask-SQLAlchemy==3.0.2",
            "requests>=2.28",
            "pillow==9.3",
        ],  # external packages as dependencies
        license="MIT",
        long_description="""
        Future plans :
                    - Make APIs accept other Game types to plug-and-play
                    - Make Player accept other Game styles
                    - Make graphical Interface that plug on Interface_template
        """
    )
