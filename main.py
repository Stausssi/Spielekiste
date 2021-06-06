"""
    file: main.py
    description: Contains the entry point the application.

    author: Niklas Drössler, Simon Stauss
    date: 17.03.2021
    licence: free
"""

import os
# Hide pygame support message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from util import GameContainer
from loguru import logger


# Catch uncaught errors by default
@logger.catch
def main():
    """
    This method is starting the GameContainer and therefore the application.


    Tests:
        - Logger legt Datei korrekt an
        - Spiel startet korrekt
    """

    # Create logging file, rotate if filesize exceeds 1MB
    logger.add("logs/{time}.log", rotation="1 MB")
    logger.info("Started the game launcher. Make sure to support pygame!")

    GameContainer()


if __name__ == "__main__":
    main()
