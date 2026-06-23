
# app/core/logger.py

import logging
import sys
from pathlib import Path

from logging.handlers import RotatingFileHandler

LOG_PATH = "logs/mrbot.log"

Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
    handlers=[
        RotatingFileHandler(
            LOG_PATH,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MrBot")


def exception_handler(exc_type, exc_value, exc_traceback):
    logger.error(
        "UNCAUGHT EXCEPTION",
        exc_info=(
            exc_type,
            exc_value,
            exc_traceback
        )
    )


sys.excepthook = exception_handler
