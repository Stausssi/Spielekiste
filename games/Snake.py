import os
import pygame
from enum import IntEnum

from config import Configuration
from util import Game, Image


class Snake(Game):
    def __init__(self):
        """
        Snake is a game where the player moves around a given map controlling a snake.
        The objective is to survive as long as possible while eating as much food as possible

        This version of snake is inspired by this tutorial: https://www.edureka.co/blog/snake-game-with-pygame/
        """

        super().__init__()

        self.snakeTiles = [
            SnakeTile(25, 25, "head"),
            SnakeTile(25, 26, "body"),
            SnakeTile(25, 27, "body"),
            SnakeTile(25, 28, "tail")
        ]

        self.head = self.snakeTiles[0]
        self.currentDirection = Direction.UP
        self.tickCounter = 0
        self.allowMove = True

        self.run()

    def handleEvent(self, event):
        # Only react to keydown if snake is allows to move
        if event.type == pygame.KEYDOWN and self.allowMove:
            self.allowMove = False

            if event.key == pygame.K_UP and self.currentDirection is not Direction.DOWN:
                self.currentDirection = Direction.UP
            elif event.key == pygame.K_RIGHT and self.currentDirection is not Direction.LEFT:
                self.currentDirection = Direction.RIGHT
            elif event.key == pygame.K_DOWN and self.currentDirection is not Direction.UP:
                self.currentDirection = Direction.DOWN
            elif event.key == pygame.K_LEFT and self.currentDirection is not Direction.RIGHT:
                self.currentDirection = Direction.LEFT
            else:
                self.allowMove = True

    def updateScreen(self):
        self.surface.fill((0, 0, 0))

        for tile in self.snakeTiles:
            self.drawImageOnSurface(tile)

        super().updateScreen()

    def updateGameState(self):
        # Update the position of the head if enough ticks passed (2 times a second)
        if self.tickCounter % 30 == 0:
            self.updateSnakeTiles()

        # Increase the tick counter
        self.tickCounter += 1

    def updateSnakeTiles(self):
        # Allow movement again
        self.allowMove = True

        # Update the direction and position of every other element
        for index in range(len(self.snakeTiles) - 1, 0, -1):
            # Retrieve direction and position of the previous element
            prevTile = self.snakeTiles[index - 1]
            prevDirection = prevTile.getDirection()
            prevPos = prevTile.getRect()

            # Set direction and position to the values of the previous Element
            tile = self.snakeTiles[index]
            tile.setDirection(prevDirection)
            tile.setRect(prevPos)

        # Update the direction of the head
        self.head.setDirection(self.currentDirection)

        # Move the head depending on the direction
        if self.currentDirection == Direction.UP:
            self.head.setY(self.head.getY() - Configuration.SNAKE_TILE_SIZE)
        elif self.currentDirection == Direction.RIGHT:
            self.head.setX(self.head.getX() + Configuration.SNAKE_TILE_SIZE)
        elif self.currentDirection == Direction.DOWN:
            self.head.setY(self.head.getY() + Configuration.SNAKE_TILE_SIZE)
        elif self.currentDirection == Direction.LEFT:
            self.head.setX(self.head.getX() - Configuration.SNAKE_TILE_SIZE)


class Direction(IntEnum):
    """
    Enum class representing the direction of a tile in Snake.
    The value of each of the entries is the angle by how much the image has to be rotated.
    """

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class SnakeTile(Image):
    def __init__(self, x, y, tileType):
        image = "snake_" + tileType + ".png"
        path = "images/snake"
        size = (Configuration.SNAKE_TILE_SIZE, Configuration.SNAKE_TILE_SIZE)

        super().__init__(
            x=x * Configuration.SNAKE_TILE_SIZE,
            y=y * Configuration.SNAKE_TILE_SIZE,
            size=size,
            image=image,
            pathToImage=path
        )

        self.direction = Direction.UP
        self.isBendable = tileType == "body"

        if self.isBendable:
            self.bendImage = pygame.transform.smoothscale(
                pygame.image.load(os.path.join(path, image.replace(tileType, "corner"))).convert(), size
            )
            self.defaultImage = self.image

    def getDirection(self) -> Direction:
        """
        Get the direction the tile is facing.

        Returns: The direction of the snake tile
        """

        return self.direction

    def setDirection(self, direction):
        """
        Update the direction of a tile. Also rotates the image to fit the direction.

        Args:
            direction (Direction): The new direction

        Returns: None
        """

        diff = self.direction - direction
        """
        rotate right if:
            U -> R, R -> D, D -> L, L -> U
            0 < 1 , 1 < 2 , 2 < 3 , 3 > 0
              -1  ,  -1   ,  -1   ,   3 

        rotate left if:
            U -> L, R -> U, D -> R, L -> D
            0 < 4 , 1 > 0 , 2 > 1 , 3 > 2
               -3  ,   1   ,   1   ,   1
        """
        if diff == -1 or diff == 3:
            self.image = pygame.transform.rotate(self.image, -90)
        elif diff == 1 or diff == -3:
            self.image = pygame.transform.rotate(self.image, 90)

        self.direction = direction
