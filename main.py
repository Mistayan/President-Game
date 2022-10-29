import logging

from models import PresidentGame, Player

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # INIT
    game = PresidentGame(number_of_players=3, number_of_ai=0)
    turn = 0
    required_cards = 0
    first_play = True
    # On start of the game, players sort their hands for clearer display, and easier strategy planning
    [player.sort_hand() for player in game.players]

    # Game_Loop
    while game.remaining_players > 1:
        print('game loop')
        # Round_loop
        for player in game.players:
            print('round loop')
            player: Player
            if player.is_folded:
                continue  # Skip current player
            user_input = []
            # Player_Loop
            while True:
                print('player loop')
                if player.is_human:
                    print(player.hand)
                    if not required_cards:
                        required_cards = int(input("How many cards do you want to play ?"))
                    for i in range(required_cards):
                        _in = input(f"Select a card to play (2-9 JQKA), or 'FOLD' to skip current round")
                        card = game.validate_user_input(player, _in)

                else:
                    player.play(None, required_cards)
                    break
            # END PLAYER_LOOP

        # END ROUND_LOOP

    # END GAME_LOOP
