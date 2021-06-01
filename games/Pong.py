import pygame

from util import Game, Image
from config import Configuration


class Player:
    def __init__(self, xpos, ypos):
        # image
        self.SIZE = (20, 100)
        self.image = Image(xpos, ypos, self.SIZE, "plane.png")

        # movement flags
        self.move_up = False
        self.move_down = False


class Ball:
    def __init__(self, xpos, ypos):
        # image
        self.SIZE = (20, 20)
        self.image = Image(xpos, ypos, self.SIZE, "ball.png")
        self.speed = (5, 2)

    def didCollideWithPlayer(self, player: Player):
        ball_rect = self.image.getRect()
        return ball_rect.colliderect(player.image.getRect())

    def did_collide_top_bottom(self):
        y_coord = self.image.getY()
        return y_coord < 0 or (y_coord + self.SIZE[1]) > Configuration.windowHeight

    def flipVelocity(self, mode="x"):
        # can only flip velocity again after it travelled for 20 pixels
        if mode is "x":
            self.speed = (-self.speed[0], self.speed[1])
        elif mode is "y":
            self.speed = (self.speed[0], -self.speed[1])

    def move(self):
        new_x = self.image.getX() + self.speed[0]
        new_y = self.image.getY() + self.speed[1]
        self.image.setX(new_x)
        self.image.setY(new_y)


class Pong(Game):
    def __init__(self):
        super().__init__()
        print("Bing Pong du hurnson")

        # 2 Players / 1 Player selection Menu

        # Player Setup
        self.player_one = Player(100, 50)
        self.player_two = Player(Configuration.windowWidth - 100, 50)
        self.ball = Ball(Configuration.windowWidth / 2, Configuration.windowHeight / 2)

        self.run()

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

        player_one_y = self.player_one.image.getY()
        player_two_y = self.player_two.image.getY()
        speed1 = 0
        speed2 = 0

        if self.player_one.move_up:
            if player_one_y > 20:
                speed1 = -10
        if self.player_one.move_down:
            if player_one_y < (Configuration.windowHeight - 20 - self.player_one.SIZE[1]):
                speed1 = 10
        if self.player_two.move_up:
            if player_two_y > 20:
                speed2 = -10
        if self.player_two.move_down:
            if player_two_y < (Configuration.windowHeight - 20 - self.player_two.SIZE[1]):
                speed2 = 10

        # movement update
        self.ball.move()
        self.player_one.image.setY(player_one_y + speed1)
        self.player_two.image.setY(player_two_y + speed2)

        # collision
        if self.ball.didCollideWithPlayer(self.player_one) or self.ball.didCollideWithPlayer(self.player_two):
            self.ball.flipVelocity(mode="x")

        if self.ball.did_collide_top_bottom():
            self.ball.flipVelocity(mode="y")  # flip velocity vector on y-axis

    def updateScreen(self):
        # fill game display black
        self.surface.fill((0, 0, 0))

        # draw players and ball
        self.drawImageOnSurface(self.player_one.image)
        self.drawImageOnSurface(self.player_two.image)
        self.drawImageOnSurface(self.ball.image)

        # draw players and ball

        super().updateScreen()
