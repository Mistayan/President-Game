from __future__ import annotations

import logging
import random
from typing import Final

import coloredlogs

coloredlogs.install()
coloredlogs.set_level(logging.CRITICAL)
random.SystemRandom().seed("no_AI_allowed")
root_logger: Final = logging.getLogger("root_logger")

VALUES: Final = [str(num) for num in range(3, 11)] + ["J", "Q", "K", "A", "2"]
COLORS: Final = {'♡': 'Heart', '♦': 'Square', '♤': 'Spade', '♣': 'Clover'}  # color: unicode_safe
