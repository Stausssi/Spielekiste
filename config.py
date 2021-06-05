class Configuration:
    """
    A static configuration class containing the most important values, such as windows size, etc.
    """

    windowWidth, windowHeight = 1920, 1080
    windowSize = (windowWidth, windowHeight)
    windowTitle = "Niklas und Simons Spielekiste"
    MUSIC_VOLUME = 0.3
    FRAMERATE = 60

    # Scores
    SCORES_HEADER = {
        "Snake": ["Score"],
        "TicTacToe": ["Wins"],
        "Pong": ["Wins", "Score"],
        "Space Invaders": ["Score"]
    }


class Colors:
    White = (255, 255, 255)
    Black = (0, 0, 0)
    VeryLightGreen = (0, 255, 0)
    LightGreen = (0, 200, 0)
    Green = (0, 150, 0)
    Red = (255, 0, 0)
    DarkRed = (150, 0, 0)
