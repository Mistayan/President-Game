import logging
from typing import Final
import names

from models import Player, AI, Deck, Card, root_logger


class PresidentGame:
    logger: Final = logging.getLogger(__name__)
    players: list
    last_playing_player_index = 0
    pile: list[Card]
    last_rounds_piles: list[list[Card]]     # For AI training sets
    rounds_winners: list[Player]            # For AI training sets
    turn: int = 0
    required_cards = 0

    def __init__(self, number_of_players=3, number_of_ai=0, *players_names):
        """
        Game Instance.
        Players (includes IA) : 3-6 players
        :param number_of_players: int 1-6
        :param number_of_ai: int 1-5
        :param players_names: "p1", "p2", ..., "p6"
        """
        if players_names and len(players_names) > number_of_players:
            raise IndexError(f"Too many names for Human Player count (AI are randomly named)")
        if 3 < number_of_players + number_of_ai > 6:
            raise ValueError(f"Invalid Total Number of Players. 3-6")

        self.players = []
        for name in players_names:  # Named players
            self.players += [Player(str(name))]
            number_of_players -= 1
        for _ in range(number_of_players):  # Anonymous Players
            self.players += [Player()]
        self.players += [AI("AI - " + names.get_full_name(gender="female"))
                         for _ in range(number_of_ai)]  # AI Players
        self.deck = Deck().shuffle()
        self.distribute()
        self.pile = []

    def distribute(self):
        self.logger.info(f"distributing cards")
        for i, card in enumerate(self.deck.cards):
            player_index = i % len(self.players)
            self.players[player_index].add_to_hand(card)  # Give card to player
            self.logger.debug(f"Gave {card} to player {self.players[player_index]}")

    @property
    def remaining_players(self):
        active_players = [not player.is_folded for player in self.players].count(True)
        self.logger.info(f"players count : {active_players}")
        return active_players

    def add_to_pile(self, card: Card) -> None:
        self.pile.append(card)

    def get_pile(self) -> list:
        return self.pile

    def free_pile(self):
        self.pile = []

    def start(self):
        # On start of the game, players sort their hands for clearer display, and easier strategy planning
        [player.sort_hand() for player in self.players]
        self.game_loop()

    def game_loop(self):
        # Game_Loop
        while self.remaining_players > 1:
            self.logger.info('game loop')
            self.round_loop()
        print("".join(["#"*15, "GAME DONE", "#"*15]))
        print("Players Ranks :\n"
              "")
        # END GAME_LOOP

    def round_loop(self):
        # Round_loop
        for player in self.players:
            print('round loop')
            if player.is_folded:
                continue  # Skip current player
            self.player_loop(player)

        # END ROUND_LOOP

    def player_loop(self, player):
        player_game = []
        # Player_Loop
        while not player.is_folded or not player._played_turn:
            print('player loop')
            print(f"Last played card : (most recent on the left)\n{self.pile[::-1]}" if self.pile
                  else "You are the first to play.")
            player_game = player.play(self.required_cards)
            print(player_game, self.required_cards)
            if not self.required_cards:
                # First-player -> his card count become required card for other plays.
                self.required_cards = len(player_game)
            if len(player_game) != self.required_cards:
                print(f"Not Enough {player_game[0].value} Cards !")
        # END PLAYER_LOOP