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


if __name__ == '__main__':
    BASEDIR = os.path.abspath(os.getcwd())
    if not os.path.exists(os.path.join(BASEDIR, "venv")):
        print("Checking for new pip version... it is required to have last version for security.")
        check_pip = Popen("python -m pip install --upgrade pip".split()).communicate()
        print("Creating venv")
        init = Popen("python -m venv venv".split()).communicate()
        print("Applying requirements")
        install = Popen("./venv/Scripts/python ./venv/Scripts/activate_this && "
                     "./venv/Scripts/pip install -r requirements.txt".split()).communicate()
        if not os.path.exists(os.path.join(BASEDIR, "venv")):
            raise EnvironmentError("You must setup a virtual environment to use this method.\n"
                                   ">>> python venv venv\n>>> activate\n"
                                   ">>>pip install -r requirements.txt")
    # argparse.ArgumentParser(
    #     prog="setup.py",
    #     exit_on_error=True,
    #     parents=[]
    #                         )

    if sys.argv and len(sys.argv) == 2 and sys.argv[1] in ('install', 'build'):
        setup(
            name='Game-Servers-Generator',
            version='1.0',
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
