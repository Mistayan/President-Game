# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import logging
from typing import Final

from models import Card, Deck
from models.Errors import CheaterDetected, PlayerNotFound
from models.games import Game
from models.players.player import Player
from rules import GameRules


class CardGame(Game):
    def __init__(self, nb_players=3, nb_ai=0, *players_names, nb_games: int = 0, save=True):
        """
        Game Instance.
        Players (includes IA) : 3-6 players
        :param nb_players: int 1-6
        :param nb_ai: int 1-5
        :param players_names: "p1", "p2", ..., "p6"
        """
        super().__init__(nb_players, nb_ai, *players_names, save=save)
        super().set_game_name(__class__.__name__)
        self.__logger: Final = logging.getLogger(__class__.__name__)
        self.__logger.debug(self._super_shared_private)
        self.skip_inputs = nb_games if nb_games >= 1 else False
        self.next_player_index: int = 0
        self.plays: list[list[Card]]  # For AI training sets
        self.VALUES = GameRules.VALUES
        self._pile: list[Card] = []
        self.deck = Deck()
        self._run = False
        self._skip_players = False  # Required for next_player behavior
        self.required_cards = 0

    def _initialize_game(self):
        """ Reset most values to default, to be able to start a game
        reset players status and hands,
        distribute cards to players
        show players and their card count
        """
        super(CardGame, self)._initialize_game()
        self._free_pile()
        self.plays = []
        self.next_player_index = 0
        self.VALUES = GameRules.VALUES
        self.deck.shuffle()
        self._turn = 0
        self._run = True
        for player in self.players:
            player.reset()
        self.required_cards = 0
        self._distribute()
        [player.sort_hand() for player in self.players]
        self.show_players()

    def _distribute(self):
        """ Usual method of distribution : distribute all cards amongst players """
        self.__logger.info(f"distributing cards")
        for i, card in enumerate(self.deck.cards):
            player_index = i % len(self.players)
            self.players[player_index].add_to_hand(card)  # 'Give' card to player
            # NEVER GIVE UP THE CARD FROM DECK, to ensure cards given by players are from this game
            self.__logger.debug(f"Gave {card} to player {self.players[player_index]}")

    @property
    def run_condition(self):
        return GameRules.LOSER_CAN_PLAY and self.count_still_alive >= 1 \
            or self.count_still_alive > 1

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
        return [p.played or p.won for p in self.players].count(True) == len(self.players)

    @property
    def pile(self) -> list[Card]:
        """ returns game's pile"""
        return self._pile

    @property
    def best_card_played(self) -> bool:
        """ Returns True if the last card played is the best card"""
        return self.pile and self.pile[-1] == self.VALUES[-1]

    @property
    def everyone_folded(self):
        return [p.folded or p.won for p in self.players].count(True) == len(self.players)

    @property
    def _everyone_played(self):
        return [p.played for p in self.players].count(True) == len(self.players)

    @property
    def count_humans(self):
        return [p.is_human for p in self.players].count(True)

    @property
    def next_player(self):
        self.__logger.debug("########## NEXT INIT ##########")
        while not self.everyone_folded:
            self._skip_players = True
            while not self.everyone_played:
                self.__logger.debug("########## CONDITION LOOP ##########")
                for index, player in enumerate(self.players):
                    if index == self.next_player_index:
                        self._skip_players = False
                    # Skip until player can play or is the last standing
                    if not self._skip_players:
                        if player.is_active:
                            yield index, player
                        player.set_played()  # set_played, no matter what player did (patch)
            self.__logger.debug("########## EVERYONE PLAYED ##########")
            yield -1, None  # Do not reset generator, wait for game to change players status
        self.__logger.debug("########## EVERYONE FOLDED ##########")
        return -1, None  # Reset generator since everyone folded.

    def add_to_pile(self, card: Card) -> None:
        """ add a given card to the current pile, therefore visible to everyone """
        if not self.valid_card(card):
            raise CheaterDetected("Card is not from this game")
        self._pile.append(card)

    def valid_card(self, card) -> bool:
        valid = False
        for test in self.deck.cards:
            if test.same_as(card):
                valid = True
                break
        return valid

    def _free_pile(self):
        """ Save current pile to memory, and reset it for next round """
        self.__logger.info("########## resetting pile ##########")
        if not self.pile:
            return
        self.plays.append(self.pile)
        self._pile = []

    def show_players(self):
        """ On the beginning of a game, and when every round starts,
         players should see others and their number of cards in hand"""
        for player in self.players:
            print(f"{player} : {len(player.hand)} Cards")

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

    def next_turn(self) -> None:
        """ Increment round, reset required values """
        self._turn += 1
        print(' '.join(["#" * 15, f"Round {self._turn}", "#" * 15]))
        self._reset_players_status()
        self.required_cards = 0  # reset required cards, so the first player chooses
        self._turn > 1 and self.show_players()  # display players on new round if round > 1

    def check_if_played_last(self, player):
        """
        Another way to ensure player is the one that has put cards on top of pile
        next_player_index does not behave exactly the same in some circumstances
        """
        result = False
        if self.pile and player.last_played and len(self.pile) >= len(player.last_played):
            result = [not self.pile[-i] != card
                      for i, card in enumerate(player.last_played[::-1])
                      ].count(True) == len(player.last_played)
        return result

    def start(self, override_test=False) -> None:
        """
        On start of the game,
        players sort their hands for clearer display, and easier strategy planning
        Display current players and their number of cards in hand


        """
        if not self._run:
            self._initialize_game()
            self.queen_of_heart_starts()  # ONLY FIRST GAME If Rule is True, set next_player
            print(flush=True)
            not override_test and input("press Enter to start the game")
        while self._run:
            self._run_loop()
            super(CardGame, self)._reset_winner()  # then reset winners for new game
            self._run = self.ask_yesno("Another Game") if \
                not (override_test and self.skip_inputs) else None
            if self._run:
                self._initialize_game()

    def _run_loop(self) -> None:
        """
        This is the run loop (embedded in While self._run: ...)
        plays 1 game and show winners.
        save results if required
        disable players win status.
        """
        self._play_game()
        print("".join(["#" * 15, "GAME DONE", "#" * 15]))
        self.show_winners()
        self.save_results(self.game_name)
        for player in self.players:
            player.set_win(False)

    def _play_game(self):
        """
        A classic game loop
        increment turn
        play while everyone is not folded or some rule stops the round
        whenever run_condition become False, every player remaining LOSE the game.
        """
        while self.run_condition:
            self.next_turn()  # set new round... (many things happens here)
            # If pile is empty, find player that open round, else find next player
            self._skip_players = self.pile == [] or self._skip_players
            while not self.everyone_folded:
                self._play_round()
                # Check if players still playing game:
                if not self.run_condition:
                    for player in self.players:
                        self.set_win(player, False)  # set remaining player to loser
                    self._run = False
                if GameRules.PLAYING_BEST_CARD_END_ROUND and self.best_card_played:
                    break
            self._free_pile()  # make sure the pile is empty. (if not, appends to play and free)

    def _play_round(self):
        """
        a classic round loop:
        After everyone played, players can play again, if not folded (unless a rule says otherwise)
        Next player choose N cards to play. if N == 0, N = player's choice
        If no player able to play or someone played a closing rule, round is over
        """

        self._reset_played_status()  # Everyone played, reset this status
        for index, player in self.next_player:
            if not player:  # No one left standing
                break
            cards = self.player_loop(player)
            cards and self._do_play(index, player, cards)  # If player returned cards, confirm play
            # If player has no more cards, WIN (or lose, depending on rules)
            if not cards:
                self.next_player_index = index  # Last player to fold should always start next
            if GameRules.PLAYING_BEST_CARD_END_ROUND and self.best_card_played:
                print("#" * 15, "TERMINATING Round, Best Card Value Played !", "#" * 15)
                break

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
        cards = []
        while player.is_active:
            cards = [card for card in player.play(self.required_cards) if card]
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

    def card_can_be_played(self, card):
        """
         A simple card game usually allows a player to play a card if the pile is empty,
         OR if card >= card_on_top_of_pile
        """
        return not self.pile or card >= self.pile[-1]

    def queen_of_heart_starts(self) -> int:
        """Only triggers if rule in True
        set the player with queen of heart as the first player"""
        if GameRules.QUEEN_OF_HEART_STARTS:
            for i, player in enumerate(self.players):
                for card in player.hand:
                    if card.number == "Q" and card.color == "♡":
                        print(f"{player} got Q♡ : starting the game, ")
                        self.next_player_index = i
                        return i

    def player_lost(self, player):
        """ If player has no cards in hand, and the rule is set to True,
        Game sets current player to losers
        :returns: True if player lost, False otherwise"""
        status = False
        if GameRules.FINISH_WITH_BEST_CARD__LOOSE and not len(player.hand) \
                and self.best_card_played:
            self.set_win(player, False)
            status = True
        return status

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

    def _do_play(self, index, player, cards) -> bool:
        """ Log the play attempt,
            add player's cards to pile
            sets current player to next round's starting player (if no one plays after)
            If the player has no more cards after he played, he wins (or lose depending on rules)
            :return: True if player won/lost; False otherwise
        """
        self.__logger.info(f"{player} tries to play {cards}")
        [self.add_to_pile(card) for card in cards]
        player.set_played()
        if self.best_card_played and GameRules.PLAYING_BEST_CARD_END_ROUND:
            self.next_player_index = index
        else:
            # player played, next player should not be current player
            self.next_player_index = (index + 1) % len(self.players)
        return self.set_win(player)

    def _reset_fold_status(self) -> None:
        self.__logger.debug("Resetting players 'fold' status")
        [p.set_fold(False) for p in self.players]

    def _reset_played_status(self) -> None:
        self.__logger.debug("Resetting players 'played' status")
        [p.set_played(False) for p in self.players]
        if not GameRules.WAIT_NEXT_ROUND_IF_FOLD and not self.everyone_folded:
            self._reset_fold_status()

    def get_player_index(self, player):
        for i, p in enumerate(self.players):
            if p == player:
                return i
        raise PlayerNotFound(player)
