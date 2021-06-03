class Configuration:
    """
    A static configuration class containing the most important values, such as windows size, etc.
    """

    windowWidth, windowHeight = 1920, 1080
    windowSize = (windowWidth, windowHeight)
    windowTitle = "Niklas und Simons Spielekiste"
    FRAMERATE = 60

    # Snake specific constants
    SNAKE_TILE_SIZE = 50
    SNAKE_TILES_X = 15
    SNAKE_TILES_Y = 16
    SNAKE_SPEED = 15
    SNAKE_FOOD = ["apple", "cherry", "pear", "strawberry"]
