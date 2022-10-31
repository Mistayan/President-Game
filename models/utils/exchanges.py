from __future__ import annotations
from models import root_logger


def player_give_card_to(player, give, to):
    try:
        receive = player.remove_from_hand(give)
        try:  # first, try as if player give to player
            to.add_to_hand(receive)
        except:  # If not a Player (method does not exist), try as if player put on game's pile
            try:
                to.add_to_pile(receive)
            except:
                to.append(receive)
    except Exception as e:
        root_logger.critical(e)
        raise