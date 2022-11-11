from models.games import PresidentGame

if __name__ == '__main__':
    # INIT
    humans_names = (input("Player Name ?"),)
    game = PresidentGame(nb_players=1, nb_ai=3)

    # Start the game. (no TK so far)
    game.start()
