import logging
import random
import string
from abc import ABC, abstractmethod
from typing import Final
import names

from models import Player, AI, Deck, Card, VALUES


class CardGame(ABC):
    random.SystemRandom().seed(random.random())
    __super_private: Final = random.choices(string.hexdigits, k=100)
    players: list = []
    last_playing_player_index = 0
    pile: list[Card] = []
    last_rounds_piles: list[list[Card]] = []  # For AI training sets
    _rounds_winners: list[[Player, int]] = []  # For AI training sets
    _round: int = 0

    @abstractmethod
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

        self.__logger: Final = logging.getLogger(__class__.__name__)
        for name in players_names:  # Named players
            self.players += [Player(str(name))]
            number_of_players -= 1
        for _ in range(number_of_players):  # Anonymous Players, random generation
            self.players += [Player()]
        self.players += [AI("AI - " + names.get_full_name(gender="female"))
                         for _ in range(number_of_ai)]  # AI Players
        self._VALUES = VALUES
        self.deck = Deck().shuffle()

    @abstractmethod
    def _distribute(self):
        """ Implement your distribution policy here """
        pass

    @property
    def still_playing(self):
        still_alive = [not player.won for player in self.players].count(True)
        self.__logger.info(f"Active players : {still_alive}")
        return still_alive

    @property
    def count_active_players(self):
        return self.active_players.count(True)

    @property
    def active_players(self):
        return [player.is_active for player in self.players]

    @property
    def strongest_card(self):
        return self._VALUES[-1]

    def add_to_pile(self, card: Card) -> None:
        self.pile.append(card)

    def get_pile(self) -> list:
        return self.pile

    def free_pile(self):
        self.last_rounds_piles.append(self.pile)
        self.pile = []

    def _print_winner(self):
        rank_gen = (" : ".join([str(i), player_infos[0].name, player_infos[1]]) + "\n"
                    for i, player_infos in enumerate(self._rounds_winners))
        print("Players Ranks :\n"
              f"{''.join(rank_gen)}")

    def _reset_players_status(self):
        """
        Method to be called when round ends
        :return:
        """
        self.__logger.debug(' '.join(["#" * 15, "RESETTING PLAYERS STATUS", "#" * 15]))
        # reset played status
        for player in self.players:
            player.set_played(False)
            player.last_played = []

    def set_win(self, player):
        player.set_win()
        self._rounds_winners.append([player, self._round])

    def start(self):
        # On start of the game,
        # players sort their hands for clearer display, and easier strategy planning
        [player.sort_hand() for player in self.players]
        self.game_loop()

    @abstractmethod
    def game_loop(self):
        self.__logger.info('game loop')
        while self.still_playing > 1:
            self.round_loop()
            # Whenever a new round starts, must reset pile
            self.free_pile()
            # As well as players fold status
            [player.set_fold(False) for player in self.players]

        print("".join(["#" * 15, "GAME DONE", "#" * 15]))
        self._print_winner()
        # END GAME_LOOP

    @abstractmethod
    def round_loop(self):
        """Implement your game logic here"""
        while self.count_active_players >= 1:
            for player in self.players:
                ...

    @abstractmethod
    def player_loop(self, player: Player) -> list[Card]:
        """ Implement how a player should play your game"""
        ...
        while player.is_active:
            ...
        return []


class PresidentGame(CardGame):
    required_cards = 0

    def __init__(self, number_of_players=3, number_of_ai=0, *players_names):
        """ Instantiate a CardGame with President rules"""
        super().__init__(number_of_players, number_of_ai, *players_names)
        self._logger: Final = logging.getLogger(__class__.__name__)
        self._revolution = False
        self._distribute()

    def _distribute(self):
        """ PresidentGame logic for distributing cards:
        Give cards equally amongst players.
         Remaining cards are distributed as fairly as possible
        """
        self._logger.info(f"distributing cards")
        for i, card in enumerate(self.deck.cards):
            player_index = i % len(self.players)
            self.players[player_index].add_to_hand(card)  # Give card to player
            self._logger.debug(f"Gave {card} to player {self.players[player_index]}")

    def game_loop(self):
        """ Keep CardGame logic,
        but we require required_cards to be set since it is vital to this game"""
        self._logger.info('game loop')
        while self.still_playing > 1:
            self.round_loop()
            # Whenever a new round starts, must reset pile
            self.free_pile()
            self.required_cards = 0  # The only change we require compared to CardGame.
            # As well as players fold status
            [player.set_fold(False) for player in self.players]

        print("".join(["#" * 15, "GAME DONE", "#" * 15]))
        self._print_winner()
        # END GAME_LOOP

    def round_loop(self):
        """
        A round is defined as follows :
        - Each player play cards or fold, until no one can play.
        - When every player is folded, end round.
        - Reset 'played' status but not 'folded' status on each turn (for player in self. players)

        If first round, first player registered starts the game.
        If not first round, first playing player is last round's winner
        If last round's winner have won the game, next player will take the lead.
        If a player is left alone on the table, the game ends.
        """

        print(' '.join(["#" * 15, "New Round", "#" * 15]))
        # If not first round, skip until current player is last round's winner.
        skip = True if self.last_rounds_piles else False
        while self.count_active_players:
            for index, player in enumerate(self.players):
                if skip and index != self.last_playing_player_index:
                    continue
                if skip and index == self.last_playing_player_index:
                    skip = False
                if self._can_play(player):
                    cards = self.player_loop(player)
                    print(f"{player} played {cards}")
                    if cards:  # If player played
                        [self.add_to_pile(card) for card in cards]
                        self.last_playing_player_index = index
                        # REVOLUTION ?
                        self.set_revolution() if len(cards) == 4 else None
                        if cards and cards[0].number == self.strongest_card:  # BEST_CARDS_PLAYED ?
                            print(f" {VALUES[-1]} played. Forcefully stopping current round.")
                            break
                #
            # Everyone played / folded / won

            self._reset_players_status()
            self._round += 1
            # Check if last played cards match the strongest value
            if self.pile and self.pile[-1].number == self.strongest_card:
                print(' '.join(["#" * 15, "TERMINATING Round, Best Card Value Played !", "#" * 15]))
                break
        # END ROUND_LOOP


    def player_loop(self, player):
        print(' '.join(["#" * 15, f"{player}'s TURN", "#" * 15]))
        player_cards = []
        while player.is_active:
            print(f"Last played card : (most recent on the left)\n{self.pile[::-1]}" if self.pile
                  else "You are the first to play.")
            player_cards = player.play_cli(self.required_cards)
            if not self.required_cards:
                # First-player -> his card count become required card for other plays.
                self.required_cards = len(player_cards)
            if len(player_cards) > 0 and len(player_cards) == self.required_cards:
                if not self.pile or player_cards[0] >= self.get_pile()[-1]:
                    player.set_played()  # set to 'True'
                    break
                elif self.pile:
                    print(f"Card{'s' if len(player_cards) > 1 else ''} not powerful enough. Pick again")
                    for card in player_cards:  # Give cards back...
                        player.add_to_hand(card)
            elif not player.is_folded:
                print(f"Not enough {player_cards[0].value} in hand" if player_cards else "No card played. Fold ?")
                if not player_cards:
                    _in = input("Fold ? (y/n)")
                    if _in.lower() == "y":
                        print(f"{player} folded")
                        player.set_fold()  # set to 'True'
            else:
                print(f"{player} folded")

        return player_cards
        # END PLAYER_LOOP

    def _can_play(self, player):
        """ define if current player can play"""
        status = player.is_active

        return status

    def set_revolution(self):
        self._revolution = not self._revolution
        self._VALUES = self._VALUES[::-1]
        # Re-arranging players hands so cards are from weakest to strongest
        for player in self.players:
            player.hand = player.hand[::-1]
        print("#" * 30)
        print(" ".join(["#" * 15, f"!!! REVOLUTION !!!", "#" * 15]))
        print("#" * 30)
