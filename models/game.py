import logging
import random
import string
from abc import ABC, abstractmethod
from typing import Final

import names

from rules import GameRules
from models import AI
from models.Errors import CheaterDetected
from models.db import Database
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
    _rounds_winners: list  # For AI training sets
    _looser_queue: list  # For AI training sets
    _round: int = 0
    VALUES = VALUES

    @abstractmethod
    def __init__(self, number_of_players=3, number_of_ai=0, *players_names, skip_inputs: int = 0):
        """
        Game Instance.
        Players (includes IA) : 3-6 players
        :param number_of_players: int 1-6
        :param number_of_ai: int 1-5
        :param players_names: "p1", "p2", ..., "p6"
        """
        if 3 < number_of_players + number_of_ai > 6:
            raise ValueError(f"Invalid Total Number of Players. 3-6")
        self.skip_inputs = skip_inputs if skip_inputs >= 1 else False
        self.__logger: Final = logging.getLogger(__class__.__name__)
        self.__logger.debug(self.__super_private)
        self.players = []
        self.pile = []
        self._init_db()
        if number_of_players:
            for name in players_names:  # Named players
                self.players += [Human(name=str(name), game=self)]
                number_of_players -= 1
            for _ in range(number_of_players):  # Anonymous Players, random generation
                self.players += [Human(game=self)]
        self.players += [AI(name="AI - " + names.get_full_name(gender="female"), game=self)
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
        self._round = 1
        self._run = True

        for player in self.players:
            player.set_win(False)
            player.hand = []

    @abstractmethod
    def _distribute(self):
        """ Implement your distribution policy here """
        pass

    @property
    def still_alive(self):
        still_alive = [player.won for player in self.players].count(False)
        self.__logger.debug(f"Active players : {still_alive}")
        return still_alive

    @property
    def count_active_players(self):
        return self._active_players.count(True)

    @property
    def _active_players(self):
        return [player.is_active for player in self.players]

    @property
    def strongest_card(self):
        return self.VALUES[-1]

    def add_to_pile(self, card: Card) -> None:
        self.pile.append(card)

    def get_pile(self) -> list:
        return self.pile

    def _free_pile(self):
        self.__logger.info("########## reseting pile ##########")
        self.last_rounds_piles.append(self.pile)
        self.pile = []

    def show_players(self):
        for player in self.players:
            print(f"{player} : {len(player.hand)} Cards")

    def winners(self) -> list[dict]:
        rank_gen = ()
        self.__logger.debug(f"\nwinners : {self._rounds_winners}\nLoosers : {self._looser_queue}")
        if self._rounds_winners and not self._run:
            if self._looser_queue:
                for player_infos in self._looser_queue[::-1]:
                    # Losers are to be added from the end.
                    # First looser is last 'winner'
                    self._rounds_winners.append(player_infos)
                self._looser_queue = []  # Once over, erase looser queue for next calls

            rank_gen = [{"player": player_infos[0].name,
                         "rank": i + 1,
                         "round": player_infos[1],
                         "last_played_card": player_infos[2]
                         } for i, player_infos in enumerate(self._rounds_winners)]
        return rank_gen

    def _reset_winner(self):
        self._rounds_winners = []

    def print_winners(self):
        print("".join(["#" * 15, "WINNERS", "#" * 15]))
        for winner in self.winners():
            print(winner)

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
                self.__logger.critical(type(player), type(give), type(to))
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
            player.set_fold(False)
            player.__buffer = []

    def set_win(self, player, win=True) -> None:
        """
        Set player status to winner or looser and append :
        [Player, Round, Last_Card] to _rounds_winners
        """
        for test in self._rounds_winners:
            if test[0] == player:
                raise CheaterDetected(
                    f"{player} already in the ladder. Correct issue before continue")
        if win:
            self.__logger.info(f"{player} won the place N°{len(self._rounds_winners) + 1}")
        else:
            self.__logger.info(f"{player} lost the game.")
        player.set_win()
        winner_data = [player, self._round,
                       self.pile[-1] if self.pile and win
                       else player.last_played[0] if player.last_played else None]
        self.__logger.debug(winner_data)
        self._rounds_winners.append(winner_data)

    def set_lost(self, player) -> None:
        """ Set player status to winner and append [Player, Rank] to _rounds_winners"""
        if len(player.hand):
            return
        self.__logger.info(f"{player} Lost the game.")
        self._looser_queue.append([player, self._round, player.hand[-1] if player.hand else None])
        player.set_win()
        # if not [player.won for player in self.players].count(False):
        #     for player_infos in self._looser_queue:
        #         player_infos[0].set_win()

    def increment_round(self) -> None:
        self.__logger.info(f"#### INCREMENTING ROUND : {self._round} ####")
        self._round += 1
        self._reset_players_status()
        self._free_pile()

    @abstractmethod
    def start(self, override_test=False) -> None:
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
        print(flush=True)
        input("press Enter to start the game") if not override_test else None

    @abstractmethod
    def game_loop(self):
        """ A classic game loop """
        self.__logger.info('game loop')
        while self.still_alive > 1:
            self.round_loop()
            # Whenever a new round starts, must reset pile
            self.increment_round()  # And do more stuff to set new round...
            ...
        # END GAME_LOOP

    @abstractmethod
    def round_loop(self):
        """Implement your game logic here"""
        while ...:
            for player in self.players:
                ...

    @abstractmethod
    def player_loop(self, player: Player) -> list[Card]:
        """ Implement how a player should play your game"""
        while ...:
            ...
        return []

    def queen_of_heart_starts(self):
        """Only triggers if rule in True
        set the player with queen of heart as the first player"""
        if GameRules.QUEEN_OF_HEART_STARTS:
            for i, player in enumerate(self.players):
                for card in player.hand:
                    if card.number == "Q" and card.color == "♡":
                        print(f"{player} got Q♡ : starting the game, ")
                        self.last_playing_player_index = i
                        return

    def ask_yesno(self, question):
        """ Ask a question that requires  yes/no answer """
        answer = -1
        while answer == -1:
            if not self.skip_inputs:
                _in = input(f"{question} ? (y/n)")
                if _in and _in[0] == 'y':
                    answer = True
                if _in and _in[0] == 'n':
                    answer = False
            else:
                answer = self.skip_inputs
                self.skip_inputs -= 1
        return answer

    def __pile_to_unicode_safe(self):
        json_piles = []
        for pile in self.last_rounds_piles:
            json_pile = []
            for card in pile:
                json_pile.append(card.unicode_safe())
            json_piles.append(json_pile)
        return json_piles

    def __winners_unicode_safe(self, winners):
        json_winners = []
        for winner in winners:
            ww = winner.copy()
            if winner['last_played_card']:
                ww["last_played_card"] = winner["last_played_card"].unicode_safe() or None
            json_winners.append(ww)
        return json_winners

    def save_results(self, name, winners):
        to_save = {
            "game": name,
            "players": [player.name for player in self.players],
            "winners": self.__winners_unicode_safe(winners),
            "cards_played": self.__pile_to_unicode_safe(),
        }
        self.__db.update(to_save)

    @abstractmethod
    def _init_db(self, name=None):
        self.__db = Database(name or __class__.__name__)


class PresidentGame(CardGame):
    required_cards = 0

    def __init__(self, number_of_players=3, number_of_ai=0, *players_names, skip_inputs: int = 0):
        """ Instantiate a CardGame with President rules and functionalities """
        self._logger: Final = logging.getLogger(__class__.__name__)
        self.pile = []  # Pre-instantiating pile to avoid null/abstract pointer
        super().__init__(number_of_players, number_of_ai, *players_names, skip_inputs=skip_inputs)
        self._revolution = False
        self.queen_of_heart_starts()  # Only triggers if rule is True. First game only !

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

    def _initialize_game(self):
        super(PresidentGame, self)._initialize_game()
        self.required_cards = 0
        for player in self.players:
            player.reset()  # do not reset ranks

    def start(self, override=None, override_test=False) -> None:
        super(PresidentGame, self).start(override_test=override_test)
        while self._run:
            self.game_loop()
            # Reset players hands
            print("".join(["#" * 15, "GAME DONE", "#" * 15]))
            self._run = False
            self.print_winners()
            self.save_results("President Game", self.winners())
            self._run = override_test and self.skip_inputs > 0\
                or not override_test and self.ask_yesno("Another Game")

            if self._run:  # reset most values
                self._initialize_game()
                self._distribute()
                self.do_exchanges()  # Do exchanges
                super(PresidentGame, self)._reset_winner()  # then reset winners for new game
                if override_test:
                    self.skip_inputs -= 1

    def do_exchanges(self) -> None:
        """ On start of a new game, after the previous one,
        Players exchange their cards with others according to their ranks"""

        # starting with lowest_rank_player
        self._logger.debug(self._rounds_winners)
        for i, player_info in enumerate(self._rounds_winners[::-1]):
            player = player_info[0]
            adv = player.rank.advantage
            give_to = self._rounds_winners[i][0]
            sentence = f"{player} gives {'his best ' if adv < 0 else ''}" \
                       f"{'no' if not adv else abs(adv)}" \
                       f" cards {'to ' + str(give_to) if adv else ''}"
            print(sentence)
            for _ in range(abs(adv)):  # give cards according to adv.
                # If neutral, do not trigger
                card = None
                while not card:
                    if adv < 0:  # Give best card if negative advantage
                        card = player.hand[-1]
                    if adv > 0:  # Otherwise choose card to give
                        result = player.play_cli(1)
                        if result:
                            card = result[0]
                            player.add_to_hand(card)
                self.player_give_card_to(player, card, give_to)

    def game_loop(self):
        """ Keep CardGame logic,
        but we require required_cards to be set since it is vital to this game"""
        self._logger.info('game loop')
        while self.still_alive > 1:
            self.required_cards = 0  # The only change we require compared to CardGame.
            self.round_loop()
            self.increment_round()  # set new round...
            # Check if players still playing game:
            if self.still_alive == 1:  # If not,
                for player in self.players:
                    self.set_win(player, False) if not player.won else None
            # Whenever a new round starts, must reset pile
        # END GAME_LOOP

    def round_loop(self):
        """
        A round is defined as follows :
        - Each player play cards or fold, until no one can play.
        - When every player is folded, end round.
        - Reset 'played' status but not 'folded' status on each turn (for player in self. players)

        If first round, first player registered starts the game (or Queen of heart if rule ON)
        If not first round, first playing player is last round's winner
        If last round's winner have won the game, next player will take the lead.
        If this is not the first game, last game's looser start
        If a player is left alone on the table, the game ends.
        """

        print(' '.join(["#" * 15, "New Round", "#" * 15]))
        # If not first round, skip until current player is last round's winner.
        skip = True if self.last_rounds_piles else False
        while self.count_active_players > 1:
            for index, player in enumerate(self.players):
                # Skip players until last round's winner is current_player (or the one after him)
                if skip and index == self.last_playing_player_index:  # Player found
                    skip = False  # Stop skipping
                    if not player.is_active:  # If player already won, Next player starts
                        self._logger.debug("Last playing player cannot play this round. Skipping")
                        continue
                elif skip:
                    continue

                if player.is_active:
                    cards = self.player_loop(player)
                    print(f"{player} played {cards}" if cards
                          else f"{player} Folded.")

                    if cards:  # If player played
                        player.set_played()
                        self._logger.debug(f"{player} tries to play {cards}")
                        [self.add_to_pile(card) for card in cards]
                        self.last_playing_player_index = index
                        self.set_revolution() if len(cards) == 4 else None  # REVOLUTION ?
                        if self.best_card_played:
                            self.player_lost(player)
                            if GameRules.PLAYING_BEST_CARD_END_ROUND:
                                break
                    self.set_win(player) or player.set_played()  # If player has no more cards, WIN

                    # Check if last played cards match the strongest value
                    if GameRules.PLAYING_BEST_CARD_END_ROUND and self.best_card_played:
                        print(' '.join([
                            "#" * 15,
                            "TERMINATING Round, Best Card Value Played !",
                            "#" * 15]))
                        break
            # Everyone played
            for player in self.players:
                player.set_played(False)
                # player.set_fold(False) if not GameRules.WAIT_NEXT_ROUND_IF_FOLD else None
            self._logger.warning("EXITING ROUND_LOOP")

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
        if player.is_human:
            print("\n" * 10)
        cards = []
        while player.is_active:
            print(' '.join(["#" * 15, f" {player}'s TURN ", "#" * 15]), flush=True)
            print(f"Last played card : (most recent on the right)\n{self.pile}" if self.pile
                  else "You are the first to play.")
            cards = [card for card in player.play_cli(self.required_cards)]
            # ^^ Reworked to accept yields ^^
            if not self.required_cards:
                # First-player -> his card count become required card for other to play.
                self.required_cards = len(cards)

            if cards and len(cards) == self.required_cards:
                if self.card_can_be_played(cards[0]):
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
        if not GameRules.USE_REVOLUTION:
            return
        self._revolution = not self._revolution
        self.VALUES = self.VALUES[::-1]
        print("#" * 50)
        print(" ".join(["#" * 15, f"!!! REVOLUTION !!!", "#" * 15]))
        print("#" * 50)

    def winners(self) -> list[dict]:
        """ get super ranking then append PresidentGame rankings
        :returns: a list of dict containing multiple information on the winners"""

        winners = super().winners()
        for i, winner in enumerate(winners):
            self._logger.info(f"winner {i + 1}: {winner}")
            for player in self.players:
                if player.name == winner['player']:
                    winner.setdefault("grade",
                                      PresidentRank(i + 1, player, self.players).rank_name)
        return winners

    def card_can_be_played(self, card):
        """ Returns True if the card can be played according to pile and rules """
        return not self.pile or \
            (self.get_pile()[-1] <= card and not self._revolution
             or self.get_pile()[-1] >= card and self._revolution)

    def _init_db(self, name=None):
        super()._init_db(__class__.__name__)

    def player_lost(self, player):
        """ If player has no cards in hand, and the rule is set to True,
        Game sets current player to looser"""
        if GameRules.FINISH_WITH_BEST_CARD__LOOSE and not len(player.hand):
            self.set_lost(player)

    @property
    def best_card_played(self):
        """ Returns True if the last card played is the best card"""
        return self.pile[-1] == self.VALUES[-1]
