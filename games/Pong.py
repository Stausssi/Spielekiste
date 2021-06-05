"""
This File contains the classes Player, Ball, and the main class Pong, which is used to start the pong game
"""

import pygame

from util import Game, Image
from config import Configuration
from random import randint
import numpy as np
from time import time
from time import sleep


class Player(Image):
    """
    Child class of the Image class. Represents the player in a pong game.
    Apart from handling the image of the players, it also handles his movement.
    The flags move_up or move_down can be set and by calling the
    move()- function, the player position is updated.
    """

    def __init__(self, x, y):
        self.player_size = (20, 150)

        # image from: https://www.bienenfisch-design.de/produkt/bits-and-bytes/
        # and edited
        super().__init__(x, y, self.player_size, "plane.png")

        # movement flags --> These determine in which direction the player is moved,
        # when move() is called

        self.move_up = False
        self.move_down = False

        # the speed in which the player is moved with
        self.speed = 10

        # determines, how accurate the computer player tracks the ball
        self.sensitivity = 20

    def __moveUpIfPossible(self) -> None:
        """
        This function moves the player up, if move_up is set and he doesn´t leave the window

        Returns:
            None
        """

        if self.getY() > 20:
            self.setY(self.getY() - self.speed)

    def __moveDownIfPossible(self):
        """
        This function moves the player down, if move_down is set and he doesn´t leave the window

        Returns:
            None
        """

        if self.getY() < (Configuration.windowHeight - 20 - self.player_size[1]):
            self.setY(self.getY() + self.speed)

    def move(self) -> None:
        """
        This function handles the movement of the player.
        When move_up or move_down is set, the Y- coordinate of the player is adjusted in either direction.
        The movement is not updated, if the player comes close to the boundaries of the window to prevent
        him from exiting the window, this is handles by the functions __moveUpIfPossible() and __moveDownIfPossible()

        Returns:
            None
        """

        if self.move_up:
            self.__moveUpIfPossible()
        if self.move_down:
            self.__moveDownIfPossible()

    def computer_move(self, ball) -> None:
        """
        This function handles the movement of a computer player.
        It moves the computer player in the direction of the ball, if certain criteria are met.
        Furthermore, it makes the computer player easier to win against by introducing a some
        errors, or by reducing it´s speed.

        Args:
            ball (Ball): the ball that the player should move to

        Returns:
            None
        """

        # only move the computer player, when the ball is moving in it´s direction,
        # it´s y coordinate is more than "sensitivity" - pixels away from the ball
        # and when the ball is the right half of the window

        if ball.speed[0] > 0 and not abs(
                ball.getY() - self.getY()) < self.sensitivity and ball.getX() > Configuration.windowWidth / 2:
            if ball.getY() < self.getY() + self.SIZE[1] / 2:
                self.__moveUpIfPossible()
            elif ball.getY() > self.getY() + self.SIZE[1] / 2:
                self.__moveDownIfPossible()

    def setRandomSensitivitySpeed(self) -> None:
        """
        This function sets a random speed and sensitivity for the player.
        This is used, so that the computer player can have some inaccuracies and lose the game easier.

        Returns:
            None
        """

        self.sensitivity = randint(30, 90)
        self.speed = randint(6, 12)


class Ball(Image):
    """
    This class is a child class of the Image class. It represents the pong ball.
    Apart from handling the image of the ball, it also handles his movement, collision,
    and the the check, if a player has scored a point.
    """

    def __init__(self, x, y):
        self.ball_size = (30, 30)
        # image was edited on my own
        super().__init__(x, y, self.ball_size, "ballbyte.png")

        # speed
        self.speed = self.getRandomVelocity()

    def didCollideWithPlayer(self, player: Player):
        """
        This function checks if the ball collides with a given player.

        Args:
            player (Player): the player used to check for collision

        Return:
            None
        """

        ball_rect = self.getRect()
        return ball_rect.colliderect(player.getRect())

    def did_collide_top_bottom(self):
        """
        This function checks if the ball collides with the top or the bottom of the window.
        It returns a Boolean if a collision happens. This is used for the wall collision.

        Return:
            Boolean
        """

        y_coord = self.getY()
        return y_coord < 0 or (y_coord + self.ball_size[1]) > Configuration.windowHeight

    def flip_velocity(self, mode="x"):
        """
        This function flips the velocity vector of the ball.

        Args:
            mode (String): The axis, on which the velocity vector is flipped. When mode is x, it flips the velocity
            on the x- axis (1,1) -> ( 1,-1). When mode is y, it flips the velocity on the y- axis (1,1) -> (-1, 1).

        Return:
            None
        """

        if mode == "x":
            self.speed = (-self.speed[0], self.speed[1])
        elif mode == "y":
            self.speed = (self.speed[0], -self.speed[1])

    def move(self):
        """
        This function moves the ball in the direction of it's speed vector.

        Return:
            None
        """

        new_x = self.getX() + self.speed[0]
        new_y = self.getY() + self.speed[1]
        self.setX(new_x)
        self.setY(new_y)

    def determine_round_winner(self):
        """
        Determines, if a player has won a round. If the ball moves out of the vertical boundary of the window,
        the player on the opposite side scores a goal.

        Return:
            Integer (1 if p1 scores, 2 if player 2 scores)
        """

        if self.getX() + self.SIZE[0] < 0:
            # point for player two
            return 2
        elif self.getX() > Configuration.windowWidth:
            # point for player one
            return 1

    def reset(self):
        """
        Resets the the balls speed to a random velocity and places it in the middle of the screen.

        Return:
            None
        """

        self.speed = self.getRandomVelocity()
        self.setX(Configuration.windowWidth / 2)
        self.setY(Configuration.windowHeight / 2)

    def getRandomVelocity(self) -> (int, int):
        """
        Generates a random velocity tuple, that has random x/y values and signs.

        Return:
            (Integer, Integer)
        """

        v_x, v_y = randint(5, 15), randint(5, 7)
        pos_or_negativ = np.random.randint(2, size=2)  # 1 --> negative sign, 0 --> positive sign

        if pos_or_negativ[0]:
            v_x *= -1

        if pos_or_negativ[1]:
            v_y *= -1

        return v_x, v_y


class Pong(Game):
    """
    This class is a child class of the Game class. Apart from the parent functions it handles the general gameloop
    of the pong game, instantiates the players and the ball, handles key events and the scoring system. Furthermore it
    creates the score counters and handles the general screen updates.
    """

    def __init__(self, hasComputerPlayer):
        super().__init__()

        self.hasComputerPlayer = hasComputerPlayer  # determines, if player two should be a computer player

        self.font = pygame.font.SysFont(None, 78)  # initialize the font

        # Player Setup
        self.player_one = Player(100, 50)
        self.player_two = Player(Configuration.windowWidth - 100, 50)

        self.ball = Ball(Configuration.windowWidth / 2, Configuration.windowHeight / 2)

        # counter
        self._score = [0, 0]
        self._font = pygame.font.Font('freesansbold.ttf', 32)
        self.startTime = time()  # time of the game start --> is used to calculate a score

        # calculate the number of spacers by windowheight
        number_of_spacers = Configuration.windowHeight // 40
        # create an Array of Image objects to be displayed on the screen
        self.spacers = list()
        for i in range(number_of_spacers):
            # image was edited on my own
            self.spacers.append(Image(Configuration.windowWidth / 2, 40 * i, (10, 30), "spacer.png"))

        # render the pregame animation screen

        self.preGameScreen()

        # start the gameloop
        self.run()

    def preGameScreen(self) -> None:
        """
        This function loads the pregame animation and renders it on the screen.

        Return:
            None
        """

        # load all images
        # created with: https://de.flamingtext.com/Free-Logo-Designs/
        logo = Image(Configuration.windowWidth / 2 - 750 / 2, Configuration.windowHeight / 4 - 120 / 2, (750, 120),
                     "PongLogo.png")
        keys_player_one = Image(Configuration.windowWidth / 4 - 150, Configuration.windowHeight * 3 / 4 - 50,
                                (300, 100),
                                "AandD.png")
        keys_player_two = Image(Configuration.windowWidth * 3 / 4 - 150, Configuration.windowHeight * 3 / 4 - 50,
                                (300, 100),
                                "ArrowLeftRight.png")

        # draw text and images
        self.surface.fill((0, 0, 0))
        self.drawImageOnSurface(logo)
        self.drawImageOnSurface(keys_player_one)
        if not self.hasComputerPlayer:
            self.drawImageOnSurface(keys_player_two)
        self.drawTextOnSurface(self.font, (11, 162, 12), "First player that reaches 1000 points wins!",
                               (Configuration.windowWidth / 2, Configuration.windowHeight / 2))

        self.drawTextOnSurface(self.font, (11, 162, 12), "Controls",
                               (Configuration.windowWidth / 2, Configuration.windowHeight * 3 / 4))

        super().updateScreen()  # display images on screen
        sleep(4)  # wait for seconds

    def updateScore(self, player: int) -> None:
        """
        This function updates the score counter and increase the points of one player.

        Args:
            player (Integer): The player whose score will be increased by one (1 --> Player one, 2 --> Player two)

        Return:
            None
        """

        if player == 1:
            self._score[0] += 1
        elif player == 2:
            self._score[1] += 1

    def handleEvent(self, event) -> None:
        """
        This function overrides the handleEvent function of it´s parent class. It handles all keyboard events
        that are necessary for updating the players movement and sets their movement flags accordingly.

        Args:
            event (pygame.event.Event): The to be handled event

        Return:
            None
        """

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
            if not self.hasComputerPlayer:
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
            if not self.hasComputerPlayer:
                if event.key == pygame.K_LEFT:
                    self.player_two.move_up = False
                    # Move down with D Key
                if event.key == pygame.K_RIGHT:
                    self.player_two.move_down = False

    def updateGameState(self) -> None:
        """
        This method handles all game-specific state changes. Furthermore it moves the players and the ball, handles
        their collision, determines if a player has scored a point and increases their score.

        Return:
            None
        """

        # movement updates of players and ball
        self.ball.move()
        self.player_one.move()
        if self.hasComputerPlayer:
            self.player_two.computer_move(self.ball)
        else:
            self.player_two.move()

        # collision handling
        if self.ball.didCollideWithPlayer(self.player_one) or self.ball.didCollideWithPlayer(self.player_two):
            self.ball.flip_velocity(mode="x")  # flip velocity vector on x-axis

            # change the sensitivity and speed of the computer player every bounce to make the game more interesting
            if self.hasComputerPlayer:
                self.player_two.setRandomSensitivitySpeed()

        if self.ball.did_collide_top_bottom():
            self.ball.flip_velocity(mode="y")  # flip velocity vector on y-axis

        # determine winner of the round
        winner = self.ball.determine_round_winner()
        if winner:

            # calculate the score of the player based on the time it took to win
            endTime = time()
            score = int(10000 // (endTime - self.startTime))  # the faster a player wins, the more points he gets

            if winner == 1:
                # increase player one score
                self.updateScore(1)
                # determine, if the player has won 5 rounds
                if self._score[0] == 5:
                    # TODO -->  exchange for log
                    print("Player one has won!")
                    # generate gameover text
                    self.setGameOverText(f"Player 1 has won! Score: {score}")
                    self.isGameOver = True  # set isGameOver, so that the game over Screen is started
                    self.isRunning = False

            elif winner == 2:
                # increase player two score
                self.updateScore(2)
                # determine, if the player has won 5 rounds
                if self._score[1] == 5:
                    # TODO -->  exchange for log
                    print("Player two has won!")
                    # generate gameover text
                    self.setGameOverText(f"Player 2 has won! Score: {score}")
                    self.isGameOver = True  # set isGameOver, so that the game over Screen is started
                    self.isRunning = False

            self.ball.reset()  # reset the velocity and position of the ball

    def updateScreen(self):
        """
        This method updates the pygame window by drawing object. Here it draws the ball and the player,
        as well as the spacers in the middle of the game and the score counters

        Return:
            None
        """

        # fill game display black
        self.surface.fill((0, 0, 0))

        # draw players and ball
        self.drawImageOnSurface(self.player_one)
        self.drawImageOnSurface(self.player_two)
        self.drawImageOnSurface(self.ball)
        for image in self.spacers:
            self.drawImageOnSurface(image)

        # draw scores
        self.drawTextOnSurface(self.font, (11, 162, 12), format(self._score[0], "04b"),
                               (Configuration.windowWidth / 4, Configuration.windowHeight / 2))
        self.drawTextOnSurface(self.font, (11, 162, 12), format(self._score[1], "04b"),
                               (3 * Configuration.windowWidth / 4, Configuration.windowHeight / 2))

        super().updateScreen()  # call the parent method to update the screen
