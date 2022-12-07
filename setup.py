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

if not len(sys.argv) >= 2:
    BASEDIR = os.path.abspath(os.getcwd())
    _ENV = "venv"
    venv_py = f"{_ENV}/Scripts/python"
    if not os.path.exists(os.path.join(BASEDIR, "venv")):
        print(f"Creating virtual environment : {_ENV}")
        init = Popen(f"python -m venv {_ENV}".split()).communicate()
        print("Checking for new pip && wheel versions... last security version.")
        check_pip = Popen(f"{venv_py} -m pip install --upgrade pip".split()).communicate()
        check_wheel = Popen(f"{venv_py} -m pip install --upgrade wheel".split()).communicate()
        if not os.path.exists(os.path.join(BASEDIR, _ENV)):
            raise EnvironmentError("You must setup a virtual environment to use this method.\n"
                                   f">>> python venv {_ENV}\n>>> activate\n"
                                   ">>>pip install -r requirements.txt")
    if os.path.exists(os.path.join(BASEDIR, _ENV)):
        print("Applying requirements")
        install = Popen(f"{venv_py} -m pip install -r requirements.txt".split()).communicate()

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
