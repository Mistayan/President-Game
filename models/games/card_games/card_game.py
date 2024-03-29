# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
import json
import logging
import random
from abc import abstractmethod
from typing import Final, Generator, Tuple, Union

from flask import request, make_response

from models.games.Errors import CheaterDetected, PlayerNotFound
from models.networking.responses import Play, Give, Fold
from models.players import Player, Human
from rules import GameRules, CardGameRules
from .card import Card
from .deck import Deck
from ..game_template import Game


class CardGame(Game):
    """ A Playable Card Game, Depending on GameRules

    game = CardGame(humans, ais, humans_names)
    game.start()
    """

    def __init__(self, nb_players=0, nb_ai=3, *players_names, nb_games: int = 0, save=True):
        """
        Game Instance.
        :param nb_players: int
        :param nb_ai: int
        :param players_names: "p1", "p2", ..., "p6" (humans only)
        :question nb_games: force game to only play the amount oof games specified
        :question save: whenever you would not like to save game results, set False
        """
        self.__logger: Final = logging.getLogger(__class__.__name__)
        super().__init__(nb_players, nb_ai, *players_names, save=save)
        self.game_rules = CardGameRules(nb_players) if not self.game_rules else self.game_rules
        if self.game_rules.min_players < nb_players + nb_ai > self.game_rules.max_players:
            raise ValueError("Invalid Total Number of Players to create PresidentGame.")

        self.__logger.debug("instantiating CardGame")
        self.players_limit = 12  # Arbitrary Value
        super().set_game_name(__class__.__name__)
        self.__best_card_played_last_round = False
        self.__logger.debug(self._SUPER_PRIVATE)
        self.skip_inputs = nb_games if nb_games >= 1 else False
        self.next_player_index: int = 0
        self.plays: list[list[Card]]  # For AI training sets
        self.__pile: list[Card] = []  # Cards on top of the pile
        self.deck = Deck(self.game_rules)
        self._skip_players = False  # Required for _next_player behavior
        self.required_cards = 0

    def _initialize_game(self):
        """ Reset most values to default, to be able to start a game
        reset players status and hands,
        distribute cards to players
        show players and their card count
        """
        super()._initialize_game()
        self._free_pile()
        self.plays = []
        self.next_player_index = 0
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
        self.__logger.info("distributing cards")
        for i, card in enumerate(self.deck.cards):
            player_index = i % len(self.players)
            self.players[player_index].add_to_hand(card)  # 'Give' card to player
            # NEVER GIVE UP THE CARD FROM DECK, to ensure cards given by players are from this game
            self.__logger.debug("Gave %s to player %s", card.unicode_safe(), self.players[player_index])

    @property
    def _run_condition(self):
        """
        Define the game's running condition as a property
        :return bool: True is Game should run.
        """
        return self.game_rules.loser_can_play_his_hand and self._count_still_alive >= 1 \
            or self._count_still_alive > 1

    @property
    def _count_still_alive(self) -> int:
        """ returns a counter or players that hasn't won the game """
        still_alive = [player.won for player in self.players].count(False)
        self.__logger.debug("Active players : %s", still_alive)
        return still_alive

    @property
    def _count_active_players(self) -> int:
        """ returns the number of players able to play during current round """
        return self._active_players.count(True)

    @property
    def _active_players(self) -> list[bool]:
        """ returns a list [True/False if player able to play] for each player in game """
        return [player.is_active for player in self.players]

    @property
    def strongest_card(self):
        """ returns the actual best card in the game (take into considerations values changes)"""
        return self.game_rules.VALUES[-1]

    @property
    def pile(self) -> list[Card]:
        """ returns game's pile"""
        return self.__pile

    @property
    def best_card_played(self) -> bool:
        """ Returns True if the last card played is the best card"""
        return self.__pile and self.__pile[-1] == self.game_rules.VALUES[-1]

    @property
    def everyone_folded(self):
        """ return true if everyone folded or won in game"""
        return [p.folded or p.won for p in self.players].count(True) == len(self.players)

    @property
    def _everyone_played(self):
        """ return true if everyone played in game"""
        return [p.played for p in self.players].count(True) == len(self.players)

    @property
    def count_humans(self):
        """ returns Humans count in game """
        return [p.is_human for p in self.players].count(True)

    def __get_next_player(self) -> Generator[Tuple[int, Player], None, None]:
        for index, player in enumerate(
                self.players[self.next_player_index:] + self.players[:self.next_player_index]):
            if player.is_active:
                self._skip_players = False
                yield index, player
            if self._everyone_played or self.everyone_folded:
                self.__logger.debug(
                    "########## EVERYONE %s ##########" % "FOLDED" if self.everyone_folded else "PLAYED")
                break
        yield -1, None

    @property
    def _next_player(self) -> Tuple[int, Union[Player, None]]:
        """ Get the next player who can play, according to current game rules """
        self.__logger.debug("########## NEXT INIT ##########")
        if not self.everyone_folded:
            self._skip_players = True
        return next(self.__get_next_player())

    def __add_to_pile(self, card: Card) -> None:
        """ add a given card to the current pile, therefore visible to everyone """
        if not self.valid_card(card):
            raise CheaterDetected("Card is not from this game")
        self.__pile.append(card)

    def valid_card(self, card) -> bool:
        """
        :returns: True if Card is from Game
        """
        valid = False
        if isinstance(card, Card):
            for test in self.deck.cards:
                if test.same_as(card):
                    valid = True
                    break
        return valid

    def _free_pile(self):
        """ Save current pile to memory, and reset it for next round """
        self.__logger.info("########## resetting pile ##########")
        if not self.__pile:
            return
        self.plays.append(self.__pile)
        self.__pile = []

    def show_players(self):
        """ On the beginning of a game, and when every round starts,
         players should see others and their number of cards in hand"""
        for player in self.players:
            self.send_all(f"{player} : {len(player.hand)} Cards")

    def player_give_to(self, player: Player, give: Card or list[Card], to):
        """
        What it does is in the name
        :param player: the player that will give a card
        :param give: the card(s) to give (will be removed from player's hand)
        :param to: Player, CardGame or a buffer_list to give to (anything else will fail)
        """
        if isinstance(give, list):
            for card in give:
                self.player_give_to(player, card, to)
        card = player.remove_from_hand(give)
        if isinstance(to, Player):
            to.add_to_hand(card)
        elif isinstance(to, CardGame):
            to.__add_to_pile(card)
        elif isinstance(to, list):
            to.append(card)
        else:
            self.__logger.critical(type(player), type(give), type(to))
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

    def _next_turn(self) -> None:
        """ Increment round, reset required values """
        self._turn += 1
        self.send_all(' '.join(["#" * 15, f"Round {self._turn}", "#" * 15]))
        self._reset_players_status()
        self.required_cards = 0  # reset required cards, so the first player chooses
        self._turn > 1 and self.show_players()  # display players on new round if round > 1

    def check_if_played_last(self, player):
        """
        Another way to ensure player is the one that has put cards on top of pile
        next_player_index does not behave exactly the same in some circumstances
        """
        if self.__pile and player.last_played and len(self.__pile) >= len(player.last_played):
            self.__logger.debug("%s VS %s", self.__pile, player.last_played)
            return [self.__pile[-(i + 1)] == card
                    for i, card in enumerate(player.last_played[::-1])
                    ].count(True) == len(player.last_played)
        return False

    def start(self, override_test=False) -> None:
        """
        On start of the game,
        players sort their hands for clearer display, and easier strategy planning
        Display current players and their number of cards in hand


        """
        if not self._run:
            self._initialize_game()
            self.__queen_of_heart_starts()  # ONLY FIRST GAME If Rule is True, set _next_player
            super()._reset_winner()  # then reset winners for new game

        while self._run:
            self._run_loop()
            for player in self.players:
                if player.is_human:
                    self._run = self._ask_yesno(player, "Another Game") if \
                        not (override_test and self.skip_inputs) else None
            if self._run:
                self._initialize_game()
                super()._reset_winner()  # then reset winners for new game

    def _run_loop(self) -> None:
        """
        This is the run loop (embedded in While self._run: ...)
        plays 1 game and show winners.
        save results if required
        disable players win status.
        """
        self._play_game()
        self.send_all("".join(["#" * 15, "GAME DONE", "#" * 15]))
        self.show_winners()
        self.save_results(self.game_name)
        for player in self.players:
            player.set_win(False)  # reset win status

    def _play_game(self):
        """
        A classic game loop
        increment turn
        play while everyone is not folded or some rule stops the round
        whenever _run_condition become False, every player remaining LOSE the game.
        """
        while self._run_condition:
            self._next_turn()  # set new round... (many things happens here)
            # If pile is empty, find player that open round, else find next player
            self._skip_players = not self.__pile or self._skip_players
            while not self.everyone_folded:
                self.__play_round()
                # Check if players still playing game:
                if not self._run_condition:
                    for player in self.players:
                        self.set_win(player, False)  # set remaining player to loser
                    self._run = False
                if self.game_rules.playing_best_card_end_round and self.best_card_played:
                    break
            self._free_pile()  # make sure the pile is empty. (if not, appends to play and free)

    def __play_round(self):
        """
        a classic round loop:
        After everyone played, players can play again, if not folded (unless a rule says otherwise)
        Next player choose N cards to play. if N == 0, N = player's choice
        If no player able to play or someone played a closing rule, round is over
        """

        self.__reset_played_status()  # Everyone played, reset this status
        index, player = self._next_player  # Get player that should start the round
        while player:
            player.is_action_required = True
            self.send_all(' '.join(["#" * 15, f" {player}'s TURN ", "#" * 15]))
            cards = self.__player_turn_loop(player)
            if cards:
                player.plays = []
            # If player played cards, confirm play
            player_played = self._do_play(index, player, cards)
            if cards and not player_played:
                self.send_all("%s are miss-played."
                              " %s keep his cards and play again" % ([_.unicode_safe() for _ in cards], player))
            # if player folded, when everyone else folded, next player is current player
            if self.everyone_folded:
                self._skip_players = False
                self.next_player_index = index
            # player played, next player should not be current player
            elif self._count_active_players:
                self._skip_players = False
                self.next_player_index = (index + 1) % len(self.players)
            # if player played best card and rule active, set next player to current player
            if self.game_rules.playing_best_card_end_round and self.best_card_played:
                self._skip_players = False
                self.next_player_index = index
                self.send_all(' '.join(["#" * 15,
                                        "TERMINATING Round, Best Card Value Played !",
                                        "#" * 15]))
                break
            index, player = self._next_player  # Get next player that should play in the round

    def __player_turn_loop(self, player: Player) -> list[Card]:
        """
        If the player is active (not folded, not won, hasn't played):
            - If required_cards == 0, the amount of cards a player plays
             become the number of required_cards for other players to play
            - Select N required_cards to play from his hand, and checks that he can play those.
            - The game double-checks with its own rules if the given card(s) are stronger or weaker
                - If cards ok, set player's status to 'played'
                - If cards not ok, give player his cards back
            - (miss-click failsafe) If player did not play, ask_yes_no to fold or play again
        :param player: current_player to play
        :return: cards the player played ; [] otherwise
        """
        if self.status == self.OFFLINE:
            # Playing local,
            if player.is_human and self.count_humans > 1:
                # with multiple players in the same console.
                self._send_player(player, "\n" * 10)
                self._send_player(player,
                                  "Press Enter to play (this is to avoid"
                                  "other players to see your hand)",
                                  input)

        cards = []
        while player.is_active:
            self._send_player(player, f"Last played card : (most recent on the right)\n{self.__pile}"
            if self.__pile else "You are the first to play.")
            if self.status == self.OFFLINE or not player.is_human:
                cards = player.play(self.required_cards)
            else:
                cards = self._wait_player_action(player)
                player.plays = []  # Once synced with game, reset player's play
            if not self.required_cards:
                # First-player -> his card count become required card for other to play.
                self.required_cards = len(cards)
            if not player.is_action_required or player.folded or \
                    cards and len(cards) == self.required_cards and self.card_can_be_played(cards[0]):
                player.set_played()
                break  # Player played required_cards cards, and can play them

            # Player did not play required_cards cards, or cards are not powerful enough, send message
            if not player.folded:
                self._send_player(player, f"Card{'s' if len(cards) > 1 else ''}"
                                          " not powerful enough. Pick again")
            else:  # Fail-safe for unexpected behaviour...
                self._send_player(player, f"Not enough {cards[0].number} in hand" if cards
                else f"No card{'s' if len(cards) > 1 else ''} played")

            # AND Give cards back to player
            for card in cards:  # Give cards back...
                player.add_to_hand(card)

        self.send_all(f"{player} played {[_.unicode_safe() for _ in cards]}" if cards else f"{player} Folded.")
        return cards

    def card_can_be_played(self, card):
        """
         A simple card game usually allows a player to play a card if the pile is empty,
         OR if card >= card_on_top_of_pile
        """
        return not self.__pile or card >= self.__pile[-1]

    def __queen_of_heart_starts(self) -> int:
        """
        Only triggers if rule in True
        Search for the queen of heart in players' hands
        set the player with queen of heart as the first player
        """
        if self.game_rules.queen_of_heart_start_first_game and not self._winners:
            for i, player in enumerate(self.players):
                # Since we are playing with a deck of 52 cards, the queen of heart is the 4th card
                # and the first color is the first color in the list
                if any(card.number == self.game_rules.VALUES[-4] and card.color == list(self.game_rules.COLORS)[0]
                       for card in player.hand):
                    self.send_all(f"{player} : got the Queen of Heart !")
                    self.next_player_index = i  # Set first player of 1st game to the one with queen of heart
                    return self.next_player_index
        return random.randint(0, len(self.players) - 1)  # else, random player starts

    def player_lost(self, player):
        """ If player has no cards in hand, and the rule is set to True,
        Game sets current player to losers
        :returns: True if player lost, False otherwise"""
        status = False
        if self.game_rules.finish_with_best_card_loose and player.hand and \
                not len(player.hand) and self.best_card_played:
            self.set_win(player, False)
            status = True
        return status

    def _ask_yesno(self, player, question):
        """ Ask a question that requires  yes/no answer
        if self.skip_input is active, will return True"""
        answer = -1
        while answer == -1:
            if not self.skip_inputs:
                _in = self._send_player(player, f"{question} ? (y/n)", input).lower()
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
            :return: True if player has been able to play, False otherwise
        """
        self.__logger.info("%s tries to play %s", player, [card.unicode_safe() for card in cards])
        # Check that every card given by the player can be played
        if [self.card_can_be_played(card) for card in cards].count(True) != len(cards):
            return False

        # Cards can be played, add them to pile
        [self.__add_to_pile(card) for card in cards]
        player.last_played = cards
        player.set_played(True)

        return self.set_win(player)  # if player has no more cards, he wins (or lose depending on rules)

    def __reset_fold_status(self) -> None:
        """ Reset players fold status for next round """
        self.__logger.debug("Resetting players 'fold' status")
        [p.set_fold(False) for p in self.players]

    def __reset_played_status(self) -> None:
        """
        Reset played status for each player in game
        Also reset fold status if rule apply """
        self.__logger.debug("Resetting players 'played' status")
        [p.set_played(False) for p in self.players]  # reset
        if not self.game_rules.wait_next_round_if_folded and not self.everyone_folded:
            self.__reset_fold_status()

    def _get_player_index(self, pname):
        """ return the player's index (in case you need it) """
        for i, player in enumerate(self.players):
            if player == pname:
                return i
        raise PlayerNotFound(pname)  # Should only be reached when server is running...

    def to_json(self) -> dict:
        """ Serialize CardGameame for communications"""
        sup: dict = super().to_json()
        update = {
            "pile": [(card.number, self.game_rules.COLORS[card.color]) for card in self.__pile],
            "required_cards": self.required_cards,
        }
        if not self._run:
            update.setdefault("game_rules", self.game_rules.__dict__())
        sup.update(update)
        return sup

    def _update_game_rules(self, param: GameRules | dict):
        super()._update_game_rules(param)
        self._logger.debug(f"afterwards : {self.game_rules.__dict__()}")

    @abstractmethod
    def _check_card(self, card, num, color):
        return card.number == num and card.color == color

    def _init_server(self, name):
        super()._init_server(name)

        @self.route(f"/{Play.request['message']}/{Play.REQUIRED}", methods=Play.methods)
        def play(player):
            """
            implement Game logic for this method
            :param player: player we received message from
            :return:  200 | 401
            """

            player: Human = self.get_player(player)
            assert player and player.is_human and player.is_action_required
            assert player.token == request.headers.get('token')
            plays = json.loads(request.data).get("request").get("plays")
            self._logger.info(plays)
            if not plays:
                player.set_fold()
            else:
                for _play in plays:
                    num, color = _play.split(',')
                    color = Card.from_unicode(color)
                    self.__logger.debug("player's hand %s" % player.hand)
                    self._logger.debug("Searching %s / %s in player's hand" % (num, color))
                    card_found = False
                    for card in player.hand:
                        if self._check_card(card, num, color):
                            card_found = True
                            self.player_give_to(player, card, player.plays)
                            break
                    if not card_found:
                        self._logger.critical("Card not found in player's hand")

            if player.folded or player.plays:
                player.is_action_required = False  # Game's async-loops self-synchronise with this
            return make_response('OK', 200)

        @self.route(f"/{Fold.request['message']}/{Fold.REQUIRED}", methods=Fold.methods)
        def fold(player):
            """
            implement Game logic for this method
            :param player: player we received message from
            :return:  200 | 401
            """

            player: Human = self.get_player(player)
            assert player and player.is_human and player.is_action_required
            assert player.token == request.headers.get('token')
            plays = json.loads(request.data).get("request").get("plays")
            if not plays:
                player.set_fold()
            if player.folded or player.plays:
                player.is_action_required = False  # Game's async-loops self-synchronise with this
            return make_response('OK', 200)

        @self.route(f"/{Give.request['message']}/{Give.REQUIRED}", methods=Give.methods)
        def give(player):
            """
            implement Game logic for this method
            :param player: player we received message from
            :return: what player gives
            """
            player: Human = self.get_player(player)
            assert player and player.is_human and player.is_action_required
            plays = request.data
            player.plays = plays
            player.is_action_required = False  # Game's async-loops self-synchronise with this
            return plays
