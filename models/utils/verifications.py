

def validate_human_input(player, _in: str):
    if _in and not isinstance(_in, str):
        return validate_human_input(player, str(_in))

    _card = None
    if _in == "FOLD":
        player.set_fold()
        _card = None
    for card in player.hand:
        if card.number == _in:
            _card = card
            break
    return _card


def human_choose_n_cards_to_play(_max: int) -> int:
    n = 0
    while not n > 0:
        try:
            n = int(input(f"[FIRST-PLAYER] - How many cards do you want to play (1-{_max})?\n>>> "))
            if n > _max or n < 1:
                n = 0
        except:
            n = 0
    return n


def human_choose_cards_to_play(player, n_cards_to_play):
    _in = input(f"{n_cards_to_play} cards to play :\n"
                f"(2-9 JQKA), or 'FOLD' to skip current round\n>>> ").upper()

    # Check fold status
    if _in == "FOLD" or _in and _in[0] == "F":
        player.set_fold()  # True by default

    cards_to_play = []
    if not player.is_folded:
        # Validate that player has n times this card in hand
        for i in range(n_cards_to_play):
            ok = validate_human_input(player, _in)
            if ok:
                cards_to_play.append(player.remove_from_hand(ok))

        if len(cards_to_play) != n_cards_to_play:  # Not enough of designated card in hand...
            [player.add_to_hand(card) for card in cards_to_play]  # Give player his cards back
            cards_to_play = []
    return cards_to_play
