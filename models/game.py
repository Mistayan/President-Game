import logging
import random
import re
import string
from abc import ABC, abstractmethod
from typing import Final

import names

from models import AI
from models.Errors import CheaterDetected
from models.deck import Deck, Card, VALUES
from models.player import Player, Human
from models.rankings import PresidentRank


class CardGame(ABC):
    random.SystemRandom().seed("no_AI_allowed")
    __super_private: Final = ''.join(random.choices(string.hexdigits, k=100))
    players: list
    last_playing_player_index: int
    pile: list[Card]
    deck: Deck
    last_rounds_piles: list[list[Card]]  # For AI training sets
    _rounds_winners: list[[Player, int, Card]]  # For AI training sets
    _looser_queue: list[[Player, int, Card]]  # For AI training sets
    _round: int = 0
    VALUES = VALUES

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
        self.__logger.debug(self.__super_private)
        self.players = []
        self.pile = []
        for name in players_names:  # Named players
            self.players += [Human(str(name))]
            number_of_players -= 1
        for _ in range(number_of_players):  # Anonymous Players, random generation
            self.players += [Human()]
        self.players += [AI(self, "AI - " + names.get_full_name(gender="female"))
                         for _ in range(number_of_ai)]  # AI Players
        self.deck = Deck()
        self._initialize_game()
        self._rounds_winners = []
        self._run = True
        # Since this is the first game, we consider the player wants to play

    def _initialize_game(self):
        self.__logger.info(' '.join(["#" * 15, "PREPARING NEW GAME", "#" * 15]))
        self.pile = []
        self.last_rounds_piles = []
        self._looser_queue = []
        self.last_playing_player_index = 0
        self.VALUES = VALUES
        self.deck.shuffle()

        for player in self.players:
            player.set_win(False)
            player.hand = []

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
        return self.VALUES[-1]

    def add_to_pile(self, card: Card) -> None:
        self.pile.append(card)

    def get_pile(self) -> list:
        return self.pile

    def free_pile(self):
        self.last_rounds_piles.append(self.pile)
        self.pile = []

    def show_players(self):
        for player in self.players:
            print(f"{player} : {len(player.hand)} Cards")

    def winners(self):
        rank_gen = [""]
        if self._rounds_winners:
            rank_gen = (
                " : ".join([str(i), player_infos[0].name, "on round", str(player_infos[1])]) + "\n"
                for i, player_infos in enumerate(self._rounds_winners))
        return rank_gen

    def player_give_card_to(self, player: Player, give: Card, to):
        try:
            card = player.remove_from_hand(give)
            if isinstance(to, Player):
                to.add_to_hand(card)
            elif isinstance(to, CardGame):
                to.add_to_pile(card)
            elif isinstance(to, list):
                to.append(card)
            else:
                print(type(player), type(give), type(to))
                raise
        except Exception as e:
            raise CheaterDetected(f"{player} failed to give {give} to {to}")

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
            player.__buffer = []

    def set_win(self, player) -> None:
        """
        Set player status to winner or looser and append :
        [Player, Round, Last_Card] to _rounds_winners
        """
        if len(self.players) - 1 != len(self._rounds_winners):
            print(f"{player} won the place N°{len(self._rounds_winners) + 1}")
        else:
            self.set_lost(player)
        player.set_win()
        self._rounds_winners.append([player, self._round, self.pile[-1] if self.pile else None])

    def set_lost(self, player) -> None:
        """ Set player status to winner and append [Player, Rank] to _rounds_winners"""
        print(f"{player} Lost the game.")
        self._looser_queue.append([player, self._round, player.hand[-1] if player.hand else None])

    def increment_round(self) -> None:
        self._round += 1

    @abstractmethod
    def start(self) -> None:
        """
        # On start of the game,
        # players sort their hands for clearer display, and easier strategy planning
        # Display current players and their number of cards in hand
        call super().start then implement your logic

            while _run:
                game_loop()
        """
        [player.sort_hand() for player in self.players]
        self.show_players()
        input("press Enter to start the game")

    @abstractmethod
    def game_loop(self):
        """ A classic game loop """
        self.__logger.info('game loop')
        while self.still_playing > 1:
            self.round_loop()
            # Whenever a new round starts, must reset pile
            self.free_pile()
            # As well as players fold status
            [player.set_fold(False) for player in self.players]
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

    @staticmethod
    def ask_yesno(question):
        """ Ask a question that requires  yes/no answer """
        answer = -1
        while answer == -1:
            _in = input(f"{question} ? (y/n)")
            if _in and _in[0] == 'y':
                answer = True
            if _in and _in[0] == 'n':
                answer = False
        return answer

    def save_results(self):
        pass


class PresidentGame(CardGame):
    required_cards = 0

    def __init__(self, number_of_players=3, number_of_ai=0, *players_names):
        """ Instantiate a CardGame with President rules"""
        self._logger: Final = logging.getLogger(__class__.__name__)
        self.pile = []  # Pre-instantiating pile to avoid null/abstract pointer
        super().__init__(number_of_players, number_of_ai, *players_names)
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

    def start(self, override=None, override_test=False) -> None:
        super().start()
        while self._run:
            if not override_test:
                # Reset players hands
                self.game_loop()
                print("".join(["#" * 15, "GAME DONE", "#" * 15]))
                print("".join(["#" * 15, "WINNERS", "#" * 15]))
                for winner in self.winners():
                    print(winner)
                self.save_results()
                self._run = self.ask_yesno("Another Game ?") if not override else True

            if self._run:  # reset most values
                self._initialize_game()
                self._distribute()
                self.do_exchanges()  # Do exchanges
                self._rounds_winners = []  # Then, reset winners
                override_test = False

    def do_exchanges(self) -> None:
        """ On start of a new game, after the previous one,
        Players exchange their cards with others according to their ranks"""

        # starting with lowest_rank_player
        for i, player_infos in enumerate(self._rounds_winners[::-1]):
            # player_info = [Player, round, last_card_played]
            player: Player = player_infos[0]
            print(player)
            # if not isinstance(player.rank, PresidentRank):
            #     raise CheaterDetected("Not a rank...")

            player.sort_hand()  # Ensure hand is sorted before starting...

            # If neutral, do not trigger
            print(f"{player} gives {abs(player.rank.advantage)} cards")
            for _ in range(abs(player.rank.advantage)):  # give as many cards as the advantage
                if player.rank.advantage < 0:  # Give best card if negative advantage
                    card = player.hand[-1]
                if player.rank.advantage > 0:  # Otherwise choose card to give
                    result = player.play_cli(1)
                    if result:
                        card = result[0]
                        player.add_to_hand(card)
                self.player_give_card_to(player,
                                         card,
                                         self._rounds_winners[i][0]
                                         )

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
        while self.count_active_players >= 1:
            for index, player in enumerate(self.players):
                # Skip players until last round's winner is current_player (or the one after him)
                if skip and index == self.last_playing_player_index:  # Player found
                    skip = False  # Stop skipping
                    if not player.is_active:  # If player already won, Next player starts
                        self._logger.debug("Last playing player cannot play this round. Skipping")
                        continue
                elif skip:
                    continue

                if self.still_playing == 1:  # If Last active player
                    self.set_lost(player)  # add current user to the end of the ladder

                if player.is_active:
                    cards = self.player_loop(player)
                    print(f"{player} played {cards}" if cards
                          else f"{player} Folded.")

                    if cards:  # If player played
                        [self.add_to_pile(card) for card in cards]
                        if len(player.hand) == 0:  # Player got no Cards left
                            self.set_win(player)
                        self.last_playing_player_index = index

                        self.set_revolution() if len(cards) == 4 else None  # REVOLUTION ?
                        if cards and cards[0].number == self.strongest_card:  # BEST_CARDS_PLAYED ?
                            break
                #
            # Everyone played / folded / won

            self._reset_players_status()
            self.increment_round()
            # Check if last played cards match the strongest value
            if self.pile and self.pile[-1].number == self.strongest_card:
                print(' '.join([
                    "#" * 15,
                    "TERMINATING Round, Best Card Value Played !",
                    "#" * 15]))
                break  # Break round_loop

        # END ROUND_LOOP

    def player_loop(self, player: Player) -> list[Card]:
        """
        If the player is active (not folded, not won, hasn't played):
            - If required_cards == 0, the amount of cards a player plays
             become the number of required_cards for other players to play
            - Select N required_cards to play from his hand, and checks that he can play those.
            - The game double-checks with its own rules if the given card(s) are stronger or weaker
                - If cards ok, set player's status to 'played'
                - If cards not ok, give player his cards back
            - (miss-click failsafe) If player did not play, ask_fold to fold or play again
        :param player: current_player to play
        :return: cards the player played ; [] otherwise
        """
        print("\n" * 10)
        print(' '.join(["#" * 15, f" {player}'s TURN ", "#" * 15]))
        cards = []
        while player.is_active:
            print(f"Last played card : (most recent on the right)\n{self.pile}" if self.pile
                  else "You are the first to play.")
            cards = [card for card in player.play_cli(self.required_cards)]
            # ^^ Reworked to accept yields ^^
            if not self.required_cards:
                # First-player -> his card count become required card for other to play.
                self.required_cards = len(cards)

            if cards and len(cards) == self.required_cards:
                if not self.pile or cards[0] >= self.get_pile()[-1] and not self._revolution \
                        or cards[0] <= self.get_pile()[-1] and self._revolution:
                    player.set_played()  # Cards are valid for current game state.
                    break
                elif self.pile:
                    print(f"Card{'s' if len(cards) > 1 else ''} not powerful enough. Pick again")
                    for card in cards:  # Give cards back...
                        player.add_to_hand(card)
            elif not player.is_folded:  # Fail-safe for unexpected behaviour...
                print(f"Not enough {cards[0].number} in hand" if cards
                      else f"No card{'s' if len(cards) > 1 else ''} played")
                if not cards and player.ask_fold():
                    player.set_fold()

        return cards
        # END PLAYER_LOOP

    @property
    def revolution(self):
        return self._revolution

    def set_revolution(self):
        """ VARIANCE OF THE GAME RULES
        REVOLUTION is a rule that allows players to play 4 times the same card
        in order to reverse cards power.

        It can be cancelled if a player plays another 4 cards on top of the previous revolution,
        or either on his turn, later on.

        Inspired by the French revolution, yet to become True.
        """
        self._revolution = not self._revolution
        self._VALUES = self.VALUES[::-1]
        print("#" * 50)
        print(" ".join(["#" * 15, f"!!! REVOLUTION !!!", "#" * 15]))
        print("#" * 50)

    def winners(self):
        """ get super ranking then append PresidentGame rankings
        :returns: an iterable generator"""
        return (re.sub("\n", f" -> {PresidentRank(i + 1, self.players)}", winner)
                for i, winner in enumerate(super().winners()))  # Keep generators alive
