import pygame

from util import Game, Image
from config import Configuration
from random import randint
import numpy as np


class Player(Image):
    def __init__(self, x, y):
        self.player_size = (20, 150)
        super().__init__(x, y, self.player_size, "plane.png")

        # movement flags
        self.move_up = False
        self.move_down = False

    def move(self):
        speed = 0
        if self.move_up:
            if self.getY() > 20:
                speed = -10
        if self.move_down:
            if self.getY() < (Configuration.windowHeight - 20 - self.player_size[1]):
                speed = 10
        self.setY(self.getY() + speed)


class Ball(Image):
    def __init__(self, x, y):
        self.ball_size = (30, 30)
        super().__init__(x, y, self.ball_size, "ball.png")

        # speed
        self.speed = self.getRandomVelocity()

        # last velocity flip
        self.last_flip = (x, y)  # is in the middle of the screen when initializing

    def didCollideWithPlayer(self, player: Player):
        ball_rect = self.getRect()
        return ball_rect.colliderect(player.getRect())

    def did_collide_top_bottom(self):
        y_coord = self.getY()
        return y_coord < 0 or (y_coord + self.ball_size[1]) > Configuration.windowHeight

    def flip_velocity(self, mode="x"):
        if mode == "x":
            self.speed = (-self.speed[0], self.speed[1])
        elif mode == "y":
            self.speed = (self.speed[0], -self.speed[1])

    def move(self):
        new_x = self.getX() + self.speed[0]
        new_y = self.getY() + self.speed[1]
        self.setX(new_x)
        self.setY(new_y)

    def determine_winner(self):
        if self.getX() + self.SIZE[0] < 0:
            # point for player two
            return 2
        elif self.getX() > Configuration.windowWidth:
            # point for player one
            return 1

    def reset(self):
        self.speed = self.getRandomVelocity()
        self.setX(Configuration.windowWidth / 2)
        self.setY(Configuration.windowHeight / 2)

    def getRandomVelocity(self):
        v_x, v_y = randint(5, 15), randint(5, 7)
        pos_or_negativ = np.random.randint(2, size=2)

        if pos_or_negativ[0]:
            v_x *= -1

        if pos_or_negativ[1]:
            v_y *= -1

        return v_x, v_y


class Pong(Game):
    def __init__(self):
        super().__init__()

        self.font = pygame.font.SysFont(None, 78)

        # 2 Players / 1 Player selection Menu

        # Player Setup
        self.player_one = Player(100, 50)
        self.player_two = Player(Configuration.windowWidth - 100, 50)
        self.ball = Ball(Configuration.windowWidth / 2, Configuration.windowHeight / 2)

        # counter
        self._score = [0, 0]
        self._font = pygame.font.Font('freesansbold.ttf', 32)

        # calculate number of spacers
        number_of_spacers = Configuration.windowHeight // 40
        self.spacers = list()
        for i in range(number_of_spacers):
            self.spacers.append(Image(Configuration.windowWidth / 2, 40 * i, (10, 30), "spacer.png"))

        # start the gameloop
        self.run()

    def updateScore(self, player: int):
        if player == 1:
            self._score[0] += 1
        elif player == 2:
            self._score[1] += 1

    def handleEvent(self, event):
        # event handling

        # Handle keydown events
        if event.type == pygame.KEYDOWN:

            # player_one
            # Move up with A Key
            if event.key == pygame.K_a:
                self.player_one.move_up = True
            # Move down with D Key
            if event.key == pygame.K_d:
                self.player_one.move_down = True

            # player_two
            if event.key == pygame.K_LEFT:
                self.player_two.move_up = True
                # Move down with D Key
            if event.key == pygame.K_RIGHT:
                self.player_two.move_down = True

        # Handle keyup events
        if event.type == pygame.KEYUP:
            # Move up with A Key
            if event.key == pygame.K_a:
                self.player_one.move_up = False
            # Move down with D Key
            if event.key == pygame.K_d:
                self.player_one.move_down = False

            # player_two
            if event.key == pygame.K_LEFT:
                self.player_two.move_up = False
                # Move down with D Key
            if event.key == pygame.K_RIGHT:
                self.player_two.move_down = False

    def updateGameState(self):
        # borders, movement handling

        # movement updates
        self.ball.move()
        self.player_one.move()
        self.player_two.move()

        # collision handling
        if self.ball.didCollideWithPlayer(self.player_one) or self.ball.didCollideWithPlayer(self.player_two):
            self.ball.flip_velocity(mode="x")  # flip velocity vector on x-axis

        if self.ball.did_collide_top_bottom():
            self.ball.flip_velocity(mode="y")  # flip velocity vector on y-axis

        # determine winner
        winner = self.ball.determine_winner()
        if winner:
            if winner == 1:
                # increase player one score
                self.updateScore(1)
            elif winner == 2:
                self.updateScore(2)
                # increase player two score

            self.ball.reset()

    def updateScreen(self):
        # fill game display black
        self.surface.fill((0, 0, 0))

        # draw players and ball
        self.drawImageOnSurface(self.player_one)
        self.drawImageOnSurface(self.player_two)
        self.drawImageOnSurface(self.ball)
        for image in self.spacers:
            self.drawImageOnSurface(image)

        # draw scores
        self.drawTextOnSurface(self.font, (255, 255, 255), str(self._score[0]),
                               (Configuration.windowWidth / 4, Configuration.windowHeight / 2))
        self.drawTextOnSurface(self.font, (255, 255, 255), str(self._score[1]),
                               (3 * Configuration.windowWidth / 4, Configuration.windowHeight / 2))

        super().updateScreen()
