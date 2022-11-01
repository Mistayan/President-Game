from __future__ import annotations

import logging
from typing import Final

import coloredlogs

coloredlogs.install()
root_logger: Final = logging.getLogger("root_logger")
VALUES: Final = [str(num) for num in range(3, 11)] + ["J", "Q", "K", "A", "2"]
COLORS: Final = ['♡', '♦', '♤', '♣']
