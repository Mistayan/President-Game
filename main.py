from models.game import PresidentGame

if __name__ == '__main__':
    # INIT
    humans_names = (input("Player Name ?"), )
    game = PresidentGame(1, 3, *humans_names)

    # Start the game. (no TK so far)
    game.start()
