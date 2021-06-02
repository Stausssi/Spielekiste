class Configuration:
    """
    A static configuration class containing the most important values, such as windows size, etc.
    """

    windowWidth, windowHeight = 1920, 1080
    windowSize = (windowWidth, windowHeight)
    FRAMERATE = 60

    SNAKE_TILE_SIZE = 50
    SNAKE_TILES_X = 15
    SNAKE_TILES_Y = 15
    SNAKE_MAX_SPEED = 7.5

    SNAKE_FOOD = {
        1: "apple",
        2: "cherry"
    }

