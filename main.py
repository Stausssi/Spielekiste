"""
    file: main.py
    description: Contains the entry point the application.

    author: Niklas Drössler, Simon Stauss
    date: 17.03.2021
    licence: free
"""

# import os
# # Remove pygame support message
# os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
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

    GameContainer()


if __name__ == "__main__":
    main()
