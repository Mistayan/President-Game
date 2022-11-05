import logging

from models.game import PresidentGame

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # INIT
    humans_names = (input("Player Name ?"), )
    game = PresidentGame(1, 3, *humans_names)
    game.start()
