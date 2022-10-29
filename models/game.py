import logging
from typing import Final
import names

import models.conf
from models import Player, AI, Deck, Card, VALUES


class PresidentGame:
    players: list
    last_playing_player_index = 0
    pile: list[Card]
    last_rounds_piles: list[list[Card]]  # For AI training sets
    rounds_winners: list[Player]  # For AI training sets
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

        self.logger: Final = logging.getLogger(__name__)
        self.players = []
        for name in players_names:  # Named players
            self.players += [Player(str(name))]
            number_of_players -= 1
        for _ in range(number_of_players):  # Anonymous Players
            self.players += [Player()]
        self.players += [AI("AI - " + names.get_full_name(gender="female"))
                         for _ in range(number_of_ai)]  # AI Players
        self.deck = Deck().shuffle()
        self._distribute()
        self.pile = []
        self.last_rounds_piles = []
        self._revolution = False
        self.rounds_winners = []

    def _distribute(self):
        self.logger.info(f"distributing cards")
        for i, card in enumerate(self.deck.cards):
            player_index = i % len(self.players)
            self.players[player_index].add_to_hand(card)  # Give card to player
            self.logger.debug(f"Gave {card} to player {self.players[player_index]}")

    @property
    def revolution(self):
        return self._revolution

    @property
    def still_playing(self):
        still_alive = [not player.won for player in self.players].count(True)
        self.logger.info(f"Still playing players : {still_alive}")
        return still_alive

    @property
    def count_active_players(self):
        active_players = self.active_players.count(True)
        return active_players

    @property
    def active_players(self):
        return [player.is_active for player in self.players]

    @property
    def strongest_card(self):
        return VALUES[-1] if not self.revolution else VALUES[0]

    def add_to_pile(self, card: Card) -> None:
        self.pile.append(card)

    def get_pile(self) -> list:
        return self.pile

    def free_pile(self):
        self.last_rounds_piles.append(self.pile)
        self.pile = []

    def start(self):
        # On start of the game, players sort their hands for clearer display, and easier strategy planning
        [player.sort_hand() for player in self.players]
        self.game_loop()

    def game_loop(self):
        self.logger.info('game loop')
        while self.count_active_players > 1:
            self.round_loop()
            # Whenever a new round starts, must reset pile and required_cards number
            self.free_pile()
            self.required_cards = 0
            # As well as players fold status
            [player.set_fold(False) for player in self.players]

        print("".join(["#" * 15, "GAME DONE", "#" * 15]))
        rank_gen = (" : ".join([str(i), player.name, "\n"]) for i, player in enumerate(self.rounds_winners))
        print("Players Ranks :\n"
              f"{''.join(rank_gen)}")
        # END GAME_LOOP

    def round_loop(self):
        print(' '.join(["#" * 15, "New Round", "#" * 15]))
        # If not first round (nothing on pile), skip until current player is last round's winner.
        skip = True if self.last_rounds_piles else False
        while self.count_active_players > 1:
            for index, player in enumerate(self.players):
                if skip and index != self.last_playing_player_index:
                    continue
                if skip and index == self.last_playing_player_index:
                    skip = False
                    break
                if player.is_active:
                    cards = self.player_loop(player)
                    print(f"{player} played {cards}" if cards else f"{player} folded")
                    if cards:  # If player played
                        [self.add_to_pile(card) for card in cards]
                        self.last_playing_player_index = index
                        # REVOLUTION ?
                        self.set_revolution() if len(cards) == 4 else None
                        if cards and cards[0].number == self.strongest_card:  # BEST_CARDS_PLAYED ?
                            print(f" {VALUES[-1]} played. Forcefully stopping current turn.")
                            break
                # player played or folded
            # Everyone played / folded / won

            print(' '.join(["#" * 15, "PREPARING FOR NEW TURN", "#" * 15]))
            # reset played status
            for player in self.players:
                player.set_played(False)

            # Check if last played cards match the strongest value
            if self.pile and self.pile[-1].number == self.strongest_card:
                print(' '.join(["#" * 15, "TERMINATING Round, Best Card Value Played !", "#" * 15]))
                break
        # END ROUND_LOOP

    def strongest_on_pile(self):
        return max(self.pile) if self.revolution else min(self.pile)

    def player_loop(self, player):
        print(' '.join(["#" * 15, f"{player}'s TURN", "#" * 15]))
        player_cards = []
        while player.is_active:
            print(f"Last played card : (most recent on the right)\n{self.pile}" if self.pile
                  else "You are the first to play.")
            player_cards = player.play_cli(self.required_cards, self.revolution)
            if not self.required_cards:
                # First-player -> his card count become required card for other plays.
                self.required_cards = len(player_cards)
            if len(player_cards) > 0 and len(player_cards) == self.required_cards:
                # If first_play
                if not self.pile:
                    player.set_played()  # set to 'True'
                    break
                elif self.pile:
                    if self.revolution and player_cards[0] > self.pile[-1] or \
                     not self.revolution and player_cards[0] < self.pile[-1]:
                        print(f"Card{'s' if len(player_cards) > 1 else ''} not powerful enough. Pick again")
                        for card in player_cards:  # Give cards back...
                            player.add_to_hand(card)
                    else:
                        player.set_played()
            elif not player.is_folded:
                print(f"Not enough {player_cards[0].value} in hand" if player_cards else "No card played. Fold ?")
                if not player_cards:
                    _in = input("Fold ? (y/n)")
                    if _in.lower() == "y":
                        print(f"{player} folded")
                        player.set_fold()  # set to 'True'
            else:
                print(f"{player} folded")
        if len(player.hand) == 0:
            if player_cards and player_cards[0].number == self.strongest_card:
                player.set_loose()
            player.set_win()
            print("".join(["#"*15, f"{player} WINS SPOT {len(self.rounds_winners) + 1}"]))
            self.rounds_winners.append(player)

        return player_cards
        # END PLAYER_LOOP

    def _can_play(self, player):
        """ define if current player can play"""
        status = player.is_active

        return status

    def set_revolution(self):
        self._revolution = not self._revolution
        # Re-arranging players hands so cards are from weakest to strongest
        for player in self.players:
            player.hand = player.hand[::-1]
        print("#" * 50)
        print(" ".join(["#" * 15, f"!!! REVOLUTION !!!", "#" * 15]))
        print("#" * 50)
