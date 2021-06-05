"""
    file: config.py
    description: Contains constants (Configuration and Colors) for the application.

    author: Niklas Drössler, Simon Stauss
    date: 14.04.2021
    licence: free
"""

import pandas


class Configuration:
    """
    A static configuration class containing the most important values, such as window size, etc.

    Tests:
        - Variablen werden korrekt angelegt
        - DataFrame wird korrekt aus der CSV gelesen
    """

    windowWidth, windowHeight = 1920, 1080
    windowSize = (windowWidth, windowHeight)
    windowTitle = "Niklas und Simons Spielekiste"
    MUSIC_VOLUME = 0.3
    FRAMERATE = 60
    
    GAME_SNAKE = "Snake"
    GAME_TTT = "TicTacToe"
    GAME_PONG = "Pong"

    # Scores
    PLAYER_HEADER = "Player"
    SCORE_HEADER = "Score"
    WIN_HEADER = "Wins"

    DATA_HEADERS = {
        GAME_SNAKE: [PLAYER_HEADER, SCORE_HEADER],
        GAME_TTT: [PLAYER_HEADER, WIN_HEADER],
        GAME_PONG: [PLAYER_HEADER, SCORE_HEADER]
    }

    # Create the score dict containing a dataframe for each game
    SCORE_DATA = {}
    for game in DATA_HEADERS.keys():
        # Get the highest scores from the csv file
        SCORE_DATA.update({
            game: pandas.read_csv(f"scores/{game}.csv")
        })

    # Needed for dynamic table updates
    UPDATE_GAME_SCORE = ""

    # Snake specific constants
    SNAKE_TILE_SIZE = 50
    SNAKE_TILES_X = 15
    SNAKE_TILES_Y = 15
    SNAKE_SPEED = 15
    SNAKE_FOOD = ["apple", "cherry", "pear", "strawberry"]

    # TicTacToe
    TTT_TILE_SIZE = 250


class Colors:
    """
    A static class containing constants of tuples containing the RGB values of a color.

    Tests:
        - Farben alle korrekt definiert
        - Werte werden korrekt abgerufen
    """

    White = (255, 255, 255)
    Black = (0, 0, 0)
    VeryLightGreen = (0, 255, 0)
    LightGreen = (0, 200, 0)
    Green = (0, 150, 0)
    Red = (255, 0, 0)
    DarkRed = (150, 0, 0)
    ByteGreen = (11, 162, 12)
