import logging
import random
import string
from abc import ABC, abstractmethod
from typing import Final, Any

import names

from .ai import AI
from .player import Player, Human
from .db import Database
from models import Deck, Card
from models.rankings import PresidentRank
from rules import GameRules, PresidentRules
from models.Errors import CheaterDetected, PlayerNotFound


class CardGame(ABC):
    __super_private: Final = ''.join(random.choices(string.hexdigits, k=100))

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
        self.players: list[Player] = []
        self.last_playing_player_index: int = 0
        self.last_rounds_piles: list[list[Card]]  # For AI training sets
        self._round: int = 0
        self.VALUES = GameRules.VALUES
        self._pile: list[Card] = []
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
        self._looser_queue = []
        self._run = True
        self.__db: Database = None
        # Since this is the first game, we consider the player wants to play

    def _initialize_game(self):
        self.__logger.info(' '.join(["#" * 15, "PREPARING NEW GAME", "#" * 15]))
        self._pile = []
        self.last_rounds_piles = []
        self._looser_queue = []
        self.last_playing_player_index = 0
        self.VALUES = GameRules.VALUES
        self.deck.shuffle()
        self._round = 0
        self._run = True
        for player in self.players:
            player.reset()

    @abstractmethod
    def _distribute(self):
        """ Implement your distribution policy here """
        pass

    @property
    def count_still_alive(self) -> int:
        """ returns a counter or players that hasn't won the game """
        still_alive = [player.won for player in self.players].count(False)
        self.__logger.debug(f"Active players : {still_alive}")
        return still_alive

    @property
    def count_active_players(self) -> int:
        """ returns the number of players able to play during current round """
        return self._active_players.count(True)

    @property
    def _active_players(self) -> list[bool]:
        """ returns a list [True/False if player able to play] for each player in game """
        return [player.is_active for player in self.players]

    @property
    def strongest_card(self):
        """ returns the actual best card in the game (take into considerations values changes)"""
        return self.VALUES[-1]

    @property
    def everyone_played(self):
        """ returns True if everyone played his turn """
        return [p.played_turn or p.won for p in self.players].count(True) == len(self.players)

    def add_to_pile(self, card: Card) -> None:
        """ add a given card to the current pile, therefore visible to everyone """
        self._pile.append(card)

    @property
    def pile(self) -> list:
        """ returns game's pile"""
        return self._pile

    def _free_pile(self):
        """ Save current pile to memory, and reset it for next round """
        self.__logger.info("########## resetting pile ##########")
        self.last_rounds_piles.append(self.pile)
        self._pile = []

    def show_players(self):
        """ On the beginning of a game, and when every round starts,
         players should see others and their number of cards in hand"""
        for player in self.players:
            print(f"{player} : {len(player.hand)} Cards")

    def winners(self) -> list[dict[str, Any]]:
        """ Generate winners ladder, appends losers starting from the last one"""
        rank_gen = ()
        self.__logger.debug(f"\nwinners : {self._rounds_winners}\nLosers : {self._looser_queue}")
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
        """
        What it does is in the name
        :param player: the player that will give a card
        :param give: the card to give (it will be removed from player's hand, fail if he doesn't)
        :param to: Player, CardGame or a buffer_list to give to (anything else will fail) """
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
        except Exception:
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

    def set_win(self, player, win=True) -> bool:
        """
        Set player status to winner or looser and append :
        [Player, Round, Last_Card] to _rounds_winners
        """
        if (len(player.hand) and win) or player.won:
            return False
        for test in self._rounds_winners:
            if test[0] == player:
                raise CheaterDetected(f"{player} already in the ladder.")
        if win:
            if GameRules.FINISH_WITH_BEST_CARD__LOOSE and self.best_card_played:
                self.set_lost(player)
            self.__logger.info(f"{player} won the place N°{len(self._rounds_winners) + 1}")
            winner_data = [player, self._round, player.last_played[0]]
            self._rounds_winners.append(winner_data)
            player.set_win()
        else:
            self.set_lost(player, 'did not win')
        return True

    def set_lost(self, player, reason=None) -> None:
        """ Set player status to winner and append [Player, Rank] to _rounds_winners"""
        self.__logger.info(f"{player} Lost the game.")
        self._looser_queue.append([player,
                                   self._round,
                                   player.hand[-1] if player.hand and not reason
                                   else player.last_played[-1] if player.last_played else None])
        player.set_win()  # It just means that a player cannot play anymore for current game

    def increment_round(self) -> None:
        self._round += 1
        self.__logger.info(f"#### ROUND : {self._round} ####")
        self._reset_fold_status()

    def check_if_played_last(self, player):
        result = False
        if self.pile and player.last_played and len(self.pile) >= len(player.last_played):
            result = [not self.pile[-i] != card
                      for i, card in enumerate(player.last_played[::-1])
                      ].count(True) == len(player.last_played)
        return result

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
        override_test or input("press Enter to start the game")

    @abstractmethod
    def game_loop(self):
        """ A classic game loop
        implement conditions to stay in the game like so:
        While ... :
        <ul>super().game_loop()
        # do stuff
        """
        self.increment_round()  # set new round...
        self.round_loop()
        self._free_pile()
        # Check if players still playing game:
        if self.count_still_alive <= 1:  # If not,
            for player in self.players:
                self.set_win(player, False)

    @abstractmethod
    def round_loop(self):
        """
        a classic round loop
        implement conditions to stay in the loop like so:
        While ... :
        <ul>super().round_loop()
        # do stuff
        """
        if not GameRules.WAIT_NEXT_ROUND_IF_FOLD and not self.everyone_folded:
            self._reset_fold_status()
        self._reset_played_status()  # Everyone played, reset this status
        self._cycle_players()

    @abstractmethod
    def player_loop(self, player: Player) -> list[Card]:
        """ Implement how a player should play your game"""
        while ...:
            ...
        return []

    @abstractmethod
    def card_can_be_played(self, card):
        ...

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

    def player_lost(self, player):
        """ If player has no cards in hand, and the rule is set to True,
        Game sets current player to losers
        :returns: True if player lost, False otherwise"""
        status = False
        if GameRules.FINISH_WITH_BEST_CARD__LOOSE and not len(player.hand)\
                and self.best_card_played:
            self.set_lost(player, 'FINISH_WITH_BEST_CARD__LOOSE')
            status = True
        return status

    def _cycle_players(self):
        """ round_loop sub part
        cycle players turns until no one is able to play.

        if there is no pile (first to play / first round), skip until last round's winner found
        if player cannot play, select next
        """
        skip = self.pile == []
        while not self.everyone_played:
            for index, player in enumerate(self.players):
                if skip and index == self.last_playing_player_index:
                    skip = False
                # Skip until player can play or is the last standing
                if not skip:
                    if player.is_active:
                        cards = self.player_loop(player)
                        if cards and self._do_play(index, player, cards):  # If player played
                            skip = True  # Set True to be able to find next player on next loop
                    # If player has no more cards, WIN (or lose, depending on rules)
                    if len(player.hand) == 0 and not self.player_lost(player):
                        self.set_win(player)
                    player.set_played()  # No matter what player did, consider he played
            if self.best_card_played and GameRules.PLAYING_BEST_CARD_END_ROUND:
                break

    def ask_yesno(self, question):
        """ Ask a question that requires  yes/no answer
        if self.skip_input is active, will return True"""
        answer = -1
        while answer == -1:
            if not self.skip_inputs:
                _in = input(f"{question} ? (y/n)").lower()
                answer = True if _in and _in[0] == 'y' \
                    else False if _in and _in[0] == 'n' \
                    else -1
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

    def save_results(self, name) -> (dict | None):
        to_save = {
            "game": name,
            "players": [player.name for player in self.players],
            "winners": self.__winners_unicode_safe(self.winners()),
            "cards_played": self.__pile_to_unicode_safe(),
        }
        if not self.__db:
            self.__logger.info("Could not save. Game has been created with save = False")
            return to_save

        self.__db.update(to_save)

    def _init_db(self, name=None):
        self.__db = Database(name or __class__.__name__)

    def _do_play(self, index, player, cards) -> bool:
        """ Log the play attempt,
            add player's cards to pile
            sets current player to next round's starting player (if no one plays after) """
        self.__logger.debug(f"{player} tries to play {cards}")
        [self.add_to_pile(card) for card in cards]
        self.last_playing_player_index = index
        return True

    @property
    def best_card_played(self) -> bool:
        """ Returns True if the last card played is the best card"""
        return self.pile and self.pile[-1] == self.VALUES[-1]

    def _reset_fold_status(self) -> None:
        self.__logger.debug("Resetting players 'fold' status")
        [p.set_fold(False) for p in self.players]

    def _reset_played_status(self) -> None:
        self.__logger.debug("Resetting players 'played' status")
        [p.set_played(False) for p in self.players]

    @property
    def everyone_folded(self):
        return [p.folded or p.won for p in self.players].count(True) == len(self.players)

    @property
    def _everyone_played(self):
        return [p.played_turn for p in self.players].count(True) == len(self.players)

    def get_player_index(self, player):
        for i, p in enumerate(self.players):
            if p == player:
                return i
        raise PlayerNotFound(player)

    @property
    def count_humans(self):
        return [p.is_human for p in self.players].count(True)


class PresidentGame(CardGame):
    required_cards = 0

    def __init__(self, number_of_players=3, number_of_ai=0, *players_names, skip_inputs: int = 0, save=True):
        """ Instantiate a CardGame with President rules and functionalities """
        self._logger: Final = logging.getLogger(__class__.__name__)
        self._pile = []  # Pre-instantiating pile to avoid null/abstract pointer
        super().__init__(number_of_players, number_of_ai, *players_names, skip_inputs=skip_inputs)
        save and super()._init_db(__class__.__name__)
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
        self._distribute()

    def start(self, override=None, override_test=False) -> None:
        super(PresidentGame, self).start(override_test=override_test)
        while self._run:
            self.game_loop()
            # Reset players hands
            print("".join(["#" * 15, "GAME DONE", "#" * 15]))
            self._run = False
            self.print_winners()
            self.save_results("President Game")
            self._run = self.ask_yesno("Another Game") \
                if not (override_test and self.skip_inputs) else False  # Tests only

            if self._run:  # reset most values
                self._initialize_game()
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
                    card = self.player_choose_card_to_give(player)
                self.player_give_card_to(player, card, give_to)

    def player_choose_card_to_give(self, player) -> Card:
        """
        According to player's rank's advantage,
        :param player: player that have to choose a card to give to another player
        :return: the chosen Card
        """
        adv = player.rank.advantage
        card = None
        if adv < 0:  # Give best card if negative advantage
            card = player.hand[-1]
            if player.rank.rank_name == "Troufion":
                self.last_playing_player_index = self.get_player_index(player)
        if adv > 0:  # Otherwise choose card to give
            result = player.play_cli(1)
            if result:
                card = result[0]
                player.add_to_hand(card)
        return card

    def game_loop(self):
        """ Keep CardGame logic,
        but we require required_cards to be set since it is vital to this game"""
        self._logger.info('game loop')
        while self.count_still_alive > 1:
            self.required_cards = 0  # The only change we require compared to CardGame.
            super(PresidentGame, self).game_loop()

    def round_loop(self):
        """
        A round is defined as follows :
        - Each player play cards or fold, until no one can play.
        - When every player is folded, end round.
        - Reset 'played' status but not 'folded' status on each cycle, unless rules says otherwise

        """

        print(' '.join(["#" * 15, "New Round", "#" * 15]), flush=True)
        self._round > 1 and self.show_players()  # display players on new round if round > 1
        while not self.everyone_folded:
            super(PresidentGame, self).round_loop()

            # Check if rule apply and last played cards match the strongest value
            if GameRules.PLAYING_BEST_CARD_END_ROUND and self.best_card_played:
                print(' '.join(["#" * 15, "TERMINATING Round, Best Card Value Played !", "#" * 15]))
                break
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
        if player.is_human and self.count_humans > 1:
            print("\n" * 10)
        cards = []
        while player.is_active:
            print(' '.join(["#" * 15, f" {player}'s TURN ", "#" * 15]), flush=True)
            print(f"Last played card : (most recent on the right)\n{self.pile}" if self.pile
                  else "You are the first to play.")
            cards = [card for card in player.play_cli(self.required_cards) if card]
            # ^^ Reworked to accept yields ^^
            if not self.required_cards:
                # First-player -> his card count become required card for other to play.
                self.required_cards = len(cards)

            if cards and len(cards) == self.required_cards:
                if self.card_can_be_played(cards[0]):
                    break
                elif self.pile:
                    print(f"Card{'s' if len(cards) > 1 else ''} not powerful enough. Pick again")
                    for card in cards:  # Give cards back...
                        player.add_to_hand(card)
            elif not player.folded:  # Fail-safe for unexpected behaviour...
                print(f"Not enough {cards[0].number} in hand" if cards
                      else f"No card{'s' if len(cards) > 1 else ''} played")
                not cards and not player.folded and player.ask_fold(override=not player.is_human)
        print(f"{player} played {cards}" if cards
              else f"{player} Folded.")
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
        if not PresidentRules.USE_REVOLUTION:
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
        return not self.pile or (self.pile[-1] <= card and not self._revolution
                                 or self.pile[-1] >= card and self._revolution)

    def _do_play(self, index, player, cards):
        super()._do_play(index, player, cards)
        self.set_revolution() if len(cards) == 4 else None  # REVOLUTION ?
