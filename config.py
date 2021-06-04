class Configuration:
    """
    A static configuration class containing the most important values, such as windows size, etc.
    """

    windowWidth, windowHeight = 1920, 1080
    windowSize = (windowWidth, windowHeight)
    windowTitle = "Niklas und Simons Spielekiste"
    MUSIC_VOLUME = 0.3
    FRAMERATE = 60

    # Snake specific constants
    SNAKE_TILE_SIZE = 50
    SNAKE_TILES_X = 15
    SNAKE_TILES_Y = 15
    SNAKE_SPEED = 15
    SNAKE_FOOD = ["apple", "cherry", "pear", "strawberry"]


class Colors:
    White = (255, 255, 255)
    Black = (0, 0, 0)
    VeryLightGreen = (0, 255, 0)
    LightGreen = (0, 200, 0)
    Green = (0, 150, 0)
    Red = (255, 0, 0)
    DarkRed = (150, 0, 0)
