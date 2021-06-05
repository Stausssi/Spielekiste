from pandas import DataFrame


class Configuration:
    """
    A static configuration class containing the most important values, such as windows size, etc.
    """

    windowWidth, windowHeight = 1920, 1080
    windowSize = (windowWidth, windowHeight)
    windowTitle = "Niklas und Simons Spielekiste"
    MUSIC_VOLUME = 0.3
    FRAMERATE = 60

    GAME_SNAKE = "Snake"
    GAME_TTT = "TicTacToe"
    GAME_PONG = "Pong"
    GAME_SPACE_INVADERS = "Space Invaders"

    # Scores
    PLAYER_HEADER = "Player"
    SCORE_HEADER = "Score"
    WIN_HEADER = "Wins"

    DATA_HEADERS = {
        GAME_SNAKE: [PLAYER_HEADER, SCORE_HEADER],
        GAME_TTT: [PLAYER_HEADER, WIN_HEADER],
        GAME_PONG: [PLAYER_HEADER, WIN_HEADER, SCORE_HEADER],
        GAME_SPACE_INVADERS: [PLAYER_HEADER, SCORE_HEADER]
    }

    # Create the score dict containing a dataframe for each game
    SCORE_DATA = {}
    for game in DATA_HEADERS.keys():
        data = {}
        for dataHeader in DATA_HEADERS[game]:
            data.update({
                dataHeader: []
            })

        SCORE_DATA.update({
            game: DataFrame(data=data)
        })

    # SCORES = {
    #     "Snake": DataFrame(
    #         data={
    #             SCORES_HEADER["Snake"][0]: None,
    #             SCORES_HEADER["Snake"][1]: None
    #         }
    #     ),
    #     "TicTacToe": DataFrame(
    #         data={
    #             SCORES_HEADER["TicTacToe"][0]: None,
    #             SCORES_HEADER["TicTacToe"][1]: None
    #         }
    #     ),
    #     "Pong": DataFrame(
    #         data={
    #             SCORES_HEADER["Pong"][0]: None,
    #             SCORES_HEADER["Pong"][1]: None,
    #             SCORES_HEADER["Pong"][2]: None
    #         }
    #     ),
    #     "Space Invaders": DataFrame(
    #         data={
    #             SCORES_HEADER["Space Invaders"][0]: None,
    #             SCORES_HEADER["Space Invaders"][1]: None
    #         }
    #     ),
    # }


class Colors:
    White = (255, 255, 255)
    Black = (0, 0, 0)
    VeryLightGreen = (0, 255, 0)
    LightGreen = (0, 200, 0)
    Green = (0, 150, 0)
    Red = (255, 0, 0)
    DarkRed = (150, 0, 0)
