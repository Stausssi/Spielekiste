import pygame

from util import Game, Image


class Player:
    def __init__(self, xpos, ypos):
        # image

        self.player_image = Image(50,50, ())

        # positions
        self.xpos = xpos
        self.ypos = ypos

        # movement flags
        self.move_up = False
        self.move_down = False

    def getPosition(self):
        return self.xpos, self.ypos


class Ball:
    pass


class Pong(Game):
    def __init__(self):
        super().__init__()
        print("Bing Pong du hurnson")

        # Setup

        # 2 Players / 1 Player selection Menu

        # Player Setup
        self.player_one = Player(100, 100)

        self.run()

    def handleEvent(self, event):
        # event handling

        # Handle keydown events
        if event.type == pygame.KEYDOWN:
            # Move up with A Key
            if event.key == pygame.K_a:
                self.player_one.move_up = not self.player_one.move_up
            # Move down with D Key
            if event.key == pygame.K_d:
                self.player_one.move_down = not self.player_one.move_down

    def updateGameState(self):
        # borders, movement handling
        if self.player_one.move_up:
            self.player_one.ypos += 10
        if self.player_one.move_down:
            self.player_one.ypos -= 10

    def updateScreen(self):

        self.surface.blit(self.player_one.image, self.player_one.getPosition())

        # draw players and ball

        super().__init__().updateScreen()
