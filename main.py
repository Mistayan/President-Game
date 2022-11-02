import logging

from models.game import PresidentGame

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # INIT
    game = PresidentGame(1, 3, "Ready Player 1")
    game.start()
