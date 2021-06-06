"""
    file: Pong.py
    description: Contains everything needed to play Pong.
    This File contains the classes Player, Ball, and the main class Pong, which is used to start the pong game

    author: Niklas Drössler
    date: 29.05.2021
    licence: free
"""


import pygame

from util import Game, Image
from config import Configuration
from random import randint
import numpy as np
from time import time
from time import sleep
from config import Colors
from loguru import logger


class Pong(Game):
    """
    This class is a child class of the Game class. Apart from the parent functions it handles the general gameloop
    of the pong game, instantiates the players and the ball, handles key events and the scoring system. Furthermore it
    creates the score counters and handles the general screen updates.

    Sounds: Official Atari Pong Sounds, taken from the following Youtube Video:
            - https://www.youtube.com/watch?v=qhaS2uMNTjI
            All Credits go to Atari.

    Images:
        AandD.png: selfmade
        ArrowLeftRight.png: selfmade
        ballbyte.png: selfmade
        plane.png: from https://www.bienenfisch-design.de/produkt/bits-and-bytes/ and edited
        PongLogo.png: created with: https://de.flamingtext.com/Free-Logo-Designs/
        spacer.png: selfmade
        PongEndscreen: selfmade with Ponglogo.png

    Tests:
        - game initialzes all textures and sounds
        - game initializes with/ without a computer player based on "hasComputerPlayer"
    """

    def __init__(self, hasComputerPlayer):
        super().__init__(game=Configuration.GAME_PONG)

        self.hasComputerPlayer = hasComputerPlayer  # determines, if player two should be a computer player

        # deactivate the internal scoring system of the gaming to use an own scoring system
        self.hasScore = False
        self.showGameOver = True

        self.font = pygame.font.SysFont("arial", 78)  # initialize the game font

        # Player Setup
        self.player_one = Player(100, 50)
        self.player_two = Player(Configuration.windowWidth - 100, 50)

        # Ball Setup
        self.ball = Ball(Configuration.windowWidth / 2, Configuration.windowHeight / 2)

        # counter
        self._score = [0, 0]
        self.startTime = time()  # time of the game start --> is used to calculate a score

        # calculate the number of spacers by windowheight
        number_of_spacers = Configuration.windowHeight // 40
        # create an Array of Image objects to be displayed on the screen
        self.spacers = list()
        for i in range(number_of_spacers):
            # image was edited on my own
            self.spacers.append(
                Image(Configuration.windowWidth / 2, 40 * i, (10, 30), "spacer.png", pathToImage="images/Pong/"))

        # load sounds
        try:
            self.sounds = {
                "wall_collision": pygame.mixer.Sound("sounds/Pong/wall_collision.wav"),
                "player_collision": pygame.mixer.Sound("sounds/Pong/player_collision.wav"),
                "fail": pygame.mixer.Sound("sounds/Pong/fail.wav")
            }
        except():
            logger.critical("Pong Sounds could not be loaded")

        # set gameover screen settings
        # load endscreen image
        self.nameBackground = Image(
            x=0,
            y=0,
            size=Configuration.windowSize,
            pathToImage="images/Pong/",
            image="PongEndscreen.png",
            hasColorkey=False
        )

        # render the pregame animation screen
        self.preGameScreen()

        # start the gameloop
        self.run()

    def preGameScreen(self) -> None:
        """
        This function loads the pregame animation and renders it on the screen.

        Return:
            None

        Tests:
            - The pregame screen is displayed correctly
            - all textures are on their correct positions
        """

        # load all images
        # created with: https://de.flamingtext.com/Free-Logo-Designs/
        logo = Image(Configuration.windowWidth / 2 - 750 / 2, Configuration.windowHeight / 4 - 120 / 2, (750, 120),
                     "PongLogo.png", pathToImage="images/Pong/")
        keys_player_one = Image(Configuration.windowWidth / 4 - 150, Configuration.windowHeight * 3 / 4 - 50,
                                (300, 100),
                                "AandD.png", pathToImage="images/Pong/")
        keys_player_two = Image(Configuration.windowWidth * 3 / 4 - 150, Configuration.windowHeight * 3 / 4 - 50,
                                (300, 100),
                                "ArrowLeftRight.png", pathToImage="images/Pong/")

        # draw text and images
        self.surface.fill(Colors.Black)
        self.drawImageOnSurface(logo)
        self.drawImageOnSurface(keys_player_one)
        if not self.hasComputerPlayer:  # only draw the control of the second player, if he isn´t a computer player
            self.drawImageOnSurface(keys_player_two)
        self.drawTextOnSurface("First player that reaches 1000 points wins!",
                               (Configuration.windowWidth / 2, Configuration.windowHeight / 2), Colors.ByteGreen,
                               font=self.font)

        self.drawTextOnSurface("Controls",
                               (Configuration.windowWidth / 2, Configuration.windowHeight * 3 / 4), Colors.ByteGreen,
                               font=self.font)

        super().updateScreen()  # display images on screen

        logger.info("Displaying prescreen animation")

        sleep(4)  # wait for seconds

    def startGameOverScreen(self, player: int) -> None:
        """
        This function calculates the score of the winning player and starts the gameover screen. The screen contains
        a specific text and the players score, it is set by calling the method setGameOverText().

        Args:
            player(Int): the player, that has won the game: 1 --> Player_one, 2 --> Player_two

        Return:
            None

        Tests:
            - the score is calculated correctly
            - The gameOver Screen is started
        """

        # calculate the score of the player based on the time it took to win
        endTime = time()
        score = int(
            10000 // (endTime - self.startTime))  # the faster a player wins, the more points he gets

        # generate gameover text
        self.setGameOverText(f"Player {player} has won! Score: {score}")
        self.score = score
        self.isGameOver = True  # set isGameOver, so that the game over Screen is started
        self.isRunning = False  # stop the execution of the Game

    def updateScore(self, player: int) -> None:
        """
        This function updates the score counter and increase the points of one player.

        Args:
            player (Integer): The player whose score will be increased by one (1 --> Player one, 2 --> Player two)

        Return:
            None

        Tests:
            - The score of either player one is increased
            - The score of either player two is increased
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

        Tests:
            - The A and D keys set move_up and move down for player one
            - The Arrow_left and Arrow_right keys set move_up and move down for player two
            - The Arrow_left and Arrow_right keys do not work if player two is a computer player
        """

        # event handling
        # Handle keydown events and sets movements flags accordingly
        if event.type == pygame.KEYDOWN:

            # player_one
            # Move up with A Key
            if event.key == pygame.K_a:
                self.player_one.move_up = True
            # Move down with D Key
            if event.key == pygame.K_d:
                self.player_one.move_down = True

            # player_two, allow movements only, if player two is no computer player
            if not self.hasComputerPlayer:
                # move up with left arrow key
                if event.key == pygame.K_LEFT:
                    self.player_two.move_up = True
                # Move down with right arrow key
                if event.key == pygame.K_RIGHT:
                    self.player_two.move_down = True

        # Handle keyup events
        elif event.type == pygame.KEYUP:
            # player one movement
            # Stop moving up
            if event.key == pygame.K_a:
                self.player_one.move_up = False
            # Stop moving down
            if event.key == pygame.K_d:
                self.player_one.move_down = False

            # player_two, allow movements only, if player two is no computer player
            if not self.hasComputerPlayer:
                # Stop moving up
                if event.key == pygame.K_LEFT:
                    self.player_two.move_up = False
                    # Stop moving down
                if event.key == pygame.K_RIGHT:
                    self.player_two.move_down = False

    def updateGameState(self) -> None:
        """
        This method handles all game-specific state changes. Furthermore it moves the players and the ball, handles
        their collision, determines if a player has scored a point and increases their score.

        Return:
            None

        Tests:
            - the ball collides when it hits a wall
            - the game is ended when one player reaches 5 points
            - scoring a goal resets the balls velocity
        """

        # movement updates of players and ball
        self.ball.move()
        self.player_one.move()
        if self.hasComputerPlayer:
            self.player_two.computer_move(self.ball)
        else:
            self.player_two.move()

        # collision handling of the ball
        if self.ball.didCollideWithPlayer(self.player_one) or self.ball.didCollideWithPlayer(self.player_two):
            if self.ball.flip_velocity(mode="x"):  # flip velocity vector on x-axis
                self.playSound("player_collision", 0.6)

            # change the sensitivity and speed of the computer player every bounce to make the game more interesting
            if self.hasComputerPlayer:
                self.player_two.setRandomSensitivitySpeed()

        if self.ball.did_collide_top_bottom():
            self.ball.flip_velocity(mode="y")  # flip velocity vector on y-axis
            self.playSound("wall_collision")

        # determine winner of the round
        round_winner = self.ball.determine_round_winner()
        if round_winner:

            self.playSound("fail", 0.3)

            # logging
            logger.info("Player {winner} has scored a goal. Score: {score}", winner=round_winner,
                        score=str(self._score))

            if round_winner == 1:
                # increase player one score
                self.updateScore(1)
                # determine, if the player has won 5 rounds
                if self._score[0] == 5:
                    self.startGameOverScreen(1)
            elif round_winner == 2:
                # increase player two score
                self.updateScore(2)
                # determine, if the player has won 5 rounds
                if self._score[1] == 5:
                    self.startGameOverScreen(2)

            self.ball.reset()  # reset the velocity and position of the ball

    def updateScreen(self) -> None:
        """
        This method updates the pygame window by drawing object. Here it draws the ball and the player,
        as well as the spacers in the middle of the game and the score counters

        Return:
            None

        Tests:
            - The Players and the Ball are drawn on the screen
            - The score counter is updating after each goal
        """

        # fill game display black
        self.surface.fill(Colors.Black)

        # draw players and ball
        self.drawImageOnSurface(self.player_one)
        self.drawImageOnSurface(self.player_two)
        self.drawImageOnSurface(self.ball)

        # draw all the spacer images
        for image in self.spacers:
            self.drawImageOnSurface(image)

        # draw scores and format the scores in byte representation
        self.drawTextOnSurface(format(self._score[0], "04b"),
                               (Configuration.windowWidth / 4, Configuration.windowHeight / 2), Colors.ByteGreen,
                               font=self.font)
        self.drawTextOnSurface(format(self._score[1], "04b"),
                               (3 * Configuration.windowWidth / 4, Configuration.windowHeight / 2), Colors.ByteGreen,
                               font=self.font)

        super().updateScreen()  # call the parent method to update the screen


class Player(Image):
    """
    Child class of the Image class. Represents the player in a pong game.
    Apart from handling the image of the players, it also handles his movement.
    The flags move_up or move_down can be set and by calling the
    move()- function, the player position is updated.

    Tests:
        - The player is initialized correctly, all variables are set
        - The image of the player is loaded
    """

    def __init__(self, x, y):
        self.player_size = (20, 150)

        # image from: https://www.bienenfisch-design.de/produkt/bits-and-bytes/
        # and edited
        super().__init__(x, y, self.player_size, "plane.png", pathToImage="images/Pong/")

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

        Tests:
            - The player does not move up, if he is already on the top
            - The player is moved by the correct amount of pixels
        """

        if self.getY() > 20:
            self.setY(self.getY() - self.speed)

    def __moveDownIfPossible(self):
        """
        This function moves the player down, if move_down is set and he doesn´t leave the window

        Returns:
            None

        Tests:
            - The player does not move down, if he is already on the bottom
            - The player is moved by the correct amount of pixels
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

        Tests:
            - The player moves up, when the flag: move_up is set
            - The player moves down, when the flag: move_down is set
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
        errors, or by reducing it´s speed randomly.

        Args:
            ball (Ball): the ball that the player should move to

        Returns:
            None

        Tests:
            - The computer player doesn´t move, if the ball is on the other players side of the window
            - The computer player doesn´t move, if the ball is moving away from him

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
        This method is intended to be used after a collision of the ball, so that the computer player
        has a different sensitivity and speed after each bounce

        Returns:
            None

        Tests:
            - a random sensitivity is set and updated
            - a random speed is set and updated
        """

        self.sensitivity = randint(20, 70)
        self.speed = randint(7, 12)


class Ball(Image):
    """
    This class is a child class of the Image class. It represents the pong ball.
    Apart from handling the image of the ball, it also handles his movement, collision,
    and the check, if a player has scored a point.

    Tests:
        - the ball is initialized correctly --> all variables are set
        - the image of the ball is loaded
    """

    def __init__(self, x, y):
        self.ball_size = (30, 30)
        # image was edited on my own
        super().__init__(x, y, self.ball_size, "ballbyte.png", pathToImage="images/Pong/")

        # speed
        self.speed = self.getRandomVelocity()

        # time since last velocity flip, this is needed to prevent a bug,
        # where the ball would glitch into the player
        self.lastFlip = time()

    def didCollideWithPlayer(self, player: Player):
        """
        This function checks if the ball collides with a given player.

        Args:
            player (Player): the player used to check for collision

        Return:
            Boolean

        Tests:
            - When colliding with a player, return "True"
            - When not colliding with a player, return "False"
        """

        ball_rect = self.getRect()
        return ball_rect.colliderect(player.getRect())

    def did_collide_top_bottom(self):
        """
        This function checks if the ball collides with the top or the bottom of the window.
        It returns a Boolean if a collision happens. This is used for the wall collision.

        Return:
            Boolean

        Tests:
            - When colliding with a top/bottom wall, return "True"
            - When not colliding with a top/bottom wall, return "False"
        """

        y_coord = self.getY()
        return y_coord < 0 or (y_coord + self.ball_size[1]) > Configuration.windowHeight

    def flip_velocity(self, mode="x") -> bool:
        """
        This function flips the velocity vector of the ball.

        Args:
            mode (String): The axis, on which the velocity vector is flipped. When mode is x, it flips the velocity
            on the x- axis (1,1) -> ( 1,-1). When mode is y, it flips the velocity on the y- axis (1,1) -> (-1, 1).

        Return:
            Boolean: True, when the velocity has been flipped, if not, false

        Tests:
            - The x velocity is not flipped, when lastFlip was less than 0.2 seconds ago
            - When flipping the y velocity, (1,1) should be flipped to (-1, 1)
        """

        if mode == "x":
            currentTime = time()
            # The ball can only flip it´s velocity, when the last flip is more than 0.2 seconds ago

            if (currentTime - self.lastFlip) > 0.2:
                self.speed = (-self.speed[0], self.speed[1])
                self.lastFlip = currentTime  # set the last flip to the current time
            else:
                return False  # indicates, that the ball has not been flipped
        elif mode == "y":
            self.speed = (self.speed[0], -self.speed[1])

        return True

    def move(self) -> None:
        """
        This function moves the ball in the direction of it's speed vector.

        Return:
            None

        Tests:
            - The speed vector is applied in the correct direction
            - The x and y coordinates are set after the change
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

        Tests:
            - When the ball moves out of the left side of the window, player two scores a goal
            - When the ball moves out of the right side of the window, player one scores a goal
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

        Tests:
            - check, if ball speed is reset
            - check, if ball is in the middle of the screen
        """

        self.speed = self.getRandomVelocity()
        self.setX(Configuration.windowWidth / 2)
        self.setY(Configuration.windowHeight / 2)

    def getRandomVelocity(self) -> (int, int):
        """
        Generates a random velocity tuple, that has random x/y values and signs.

        Return:
            (Integer, Integer): random velocity

        Tests:
            - check, if the velocity is within the correct boundaries
            - check, if multiple function calls return different signs of the speed
        """

        v_x, v_y = randint(9, 15), randint(5, 8)
        pos_or_negativ = np.random.randint(2, size=2)  # 1 --> negative sign, 0 --> positive sign

        if pos_or_negativ[0]:
            v_x *= -1

        if pos_or_negativ[1]:
            v_y *= -1

        return v_x, v_y
