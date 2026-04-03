"""Debug logging for the Anima SDK, activated by ANIMA_LOG=debug."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("anima")

if os.environ.get("ANIMA_LOG") == "debug":
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[anima %(asctime)s] %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
