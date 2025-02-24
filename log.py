import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=logging.INFO):
    """Funkce pro nastavení loggeru."""
    formatter = logging.Formatter(
        "%(asctime)s -%(funcName)s - %(levelname)s - %(message)s"
    )
    handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=1, encoding='utf-8'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
