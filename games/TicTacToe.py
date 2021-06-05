from config import Configuration
from pandas import DataFrame
from util import Game


class TicTacToe(Game):
    def __init__(self):
        super().__init__(game="TicTacToe")
        print("XXX - i won")

        self.isGameOver = True
        self.isRunning = False
        self.run()
