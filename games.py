from util import Game


class Snake(Game):
    def __init__(self):
        super().__init__()
        print("Snake has been started you fooool")

        self.run()


class TicTacToe(Game):
    def __init__(self):
        super().__init__()
        print("XXX - i won")

        self.run()
