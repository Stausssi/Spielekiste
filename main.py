# import os
# # Remove pygame support message
# os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from util import GameContainer
from loguru import logger


# Catch uncaught errors by default
@logger.catch
def main():
    """
    Application entry point starting the GameContainer and therefore the application.

    :return: None
    """

    # Create logging file, rotate if filesize exceeds 1MB
    logger.add("logs/{time}.log", rotation="1 MB")

    GameContainer()


if __name__ == "__main__":
    main()
