import logging
import os
import sys


def setup_logger():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger("chatbot")
    logger.setLevel(log_level)
    return logger

logger = setup_logger()