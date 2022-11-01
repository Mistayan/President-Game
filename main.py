import logging

from models.game import PresidentGame

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # INIT
    game = PresidentGame(number_of_players=3, number_of_ai=0)
    game.start()
