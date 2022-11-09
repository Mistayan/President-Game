from __future__ import annotations

import logging
import random
from typing import Final

import coloredlogs

coloredlogs.install()
coloredlogs.set_level(logging.CRITICAL)
random.SystemRandom().seed("no_AI_allowed")
root_logger: Final = logging.getLogger("root_logger")
