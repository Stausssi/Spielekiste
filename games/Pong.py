import pygame

from util import Game, Image
from config import Configuration


class Player(Image):
    def __init__(self, x, y):
        player_size = (20, 100)
        super().__init__(x, y, player_size, "plane.png")

        # movement flags
        self.move_up = False
        self.move_down = False

    def move(self):
        speed = 0
        if self.move_up:
            if self.getY() > 20:
                speed = -10
        if self.move_down:
            if self.getY() < (Configuration.windowHeight - 20 - self.SIZE[1]):
                speed = 10
        self.setY(self.getY() + speed)


class Ball(Image):
    def __init__(self, x, y):
        ball_size = (20, 20)
        super().__init__(x, y, ball_size, "ball.png")

        # speed
        self.speed = (5, 2)

    def didCollideWithPlayer(self, player: Player):
        ball_rect = self.getRect()
        return ball_rect.colliderect(player.getRect())

    def did_collide_top_bottom(self):
        y_coord = self.getY()
        return y_coord < 0 or (y_coord + self.SIZE[1]) > Configuration.windowHeight

    def flipVelocity(self, mode="x"):
        # can only flip velocity again after it travelled for 20 pixels
        if mode == "x":
            self.speed = (-self.speed[0], self.speed[1])
        elif mode == "y":
            self.speed = (self.speed[0], -self.speed[1])

    def move(self):
        new_x = self.getX() + self.speed[0]
        new_y = self.getY() + self.speed[1]
        self.setX(new_x)
        self.setY(new_y)


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

        # movement update
        self.ball.move()
        self.player_one.move()
        self.player_two.move()

        # collision handling
        if self.ball.didCollideWithPlayer(self.player_one) or self.ball.didCollideWithPlayer(self.player_two):
            self.ball.flipVelocity(mode="x")

        if self.ball.did_collide_top_bottom():
            self.ball.flipVelocity(mode="y")  # flip velocity vector on y-axis

    def updateScreen(self):
        # fill game display black
        self.surface.fill((0, 0, 0))

        # draw players and ball
        self.drawImageOnSurface(self.player_one)
        self.drawImageOnSurface(self.player_two)
        self.drawImageOnSurface(self.ball)

        # draw players and ball

        super().updateScreen()
