# logger.py

import logging

def vadafi_logger():
    logging.basicConfig(
        filename="vadafi.log",
        encoding="utf-8",
        filemode="a",
        level=logging.DEBUG,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    # Logger object
    logger = logging.getLogger(__name__)
    
    return logger
