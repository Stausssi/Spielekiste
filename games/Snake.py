import os
import random

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
        self.width = Configuration.SNAKE_TILES_X * Configuration.SNAKE_TILE_SIZE
        self.height = Configuration.SNAKE_TILES_Y * Configuration.SNAKE_TILE_SIZE

        halfWidth = self.width // 2
        halfHeight = self.height // 2
        self.startX = Configuration.windowWidth // 2 - halfWidth
        self.startY = Configuration.windowHeight // 2 - halfHeight
        self.borderRect = pygame.rect.Rect(self.startX, self.startY, self.width, self.height)

        snakeX = self.startX + halfWidth
        if Configuration.SNAKE_TILES_X % 2 == 1:
            snakeX += Configuration.SNAKE_TILE_SIZE // 2

        snakeY = self.startY + halfHeight
        if Configuration.SNAKE_TILES_Y % 2 == 0:
            snakeY -= Configuration.SNAKE_TILE_SIZE // 2

        self.snakeTiles = [
            SnakeTile(snakeX, snakeY - Configuration.SNAKE_TILE_SIZE, "head"),
            SnakeTile(snakeX, snakeY, "body"),
            SnakeTile(snakeX, snakeY + Configuration.SNAKE_TILE_SIZE, "body"),
            SnakeTile(snakeX, snakeY + 2 * Configuration.SNAKE_TILE_SIZE, "tail")
        ]

        self.head = self.snakeTiles[0]
        self.currentDirection = Direction.UP
        self.tickCounter = 0
        self.score = 0
        self.speed = 5
        self.allowMove = True

        self.food = None
        self.updateFood()

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
        # Fill Background
        self.surface.fill((0, 255, 0))

        # Draw border
        pygame.draw.rect(self.surface, (255, 0, 0), self.borderRect, 5)

        # Draw Snake
        for tile in self.snakeTiles:
            self.drawImageOnSurface(tile)

        # Draw food
        self.drawImageOnSurface(self.food)

        super().updateScreen()

    def updateGameState(self):
        # Update the position of the head if enough ticks passed (2 times a second)
        if self.tickCounter % (Configuration.FRAMERATE // self.speed) == 0:
            self.updateSnakeTiles()
            self.eatFood()

        # Increase the tick counter
        self.tickCounter += 1

    def updateSnakeTiles(self):
        # Check whether the next field is valid
        if self.currentDirection == Direction.UP:
            nextX = self.head.getX()
            nextY = self.head.getY() - Configuration.SNAKE_TILE_SIZE
        elif self.currentDirection == Direction.RIGHT:
            nextX = self.head.getX() + Configuration.SNAKE_TILE_SIZE
            nextY = self.head.getY()
        elif self.currentDirection == Direction.DOWN:
            nextX = self.head.getX()
            nextY = self.head.getY() + Configuration.SNAKE_TILE_SIZE
        else:  # LEFT
            nextX = self.head.getX() - Configuration.SNAKE_TILE_SIZE
            nextY = self.head.getY()

        if self.isValidField(nextX, nextY):
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

            # Move the head to the new position
            self.head.setX(nextX)
            self.head.setY(nextY)

            # Check whether a snake tile is at a corner and change the picture if so
            for index in range(1, len(self.snakeTiles)):
                prevDirection = self.snakeTiles[index - 1].getDirection()

                tile = self.snakeTiles[index]
                rotate = tile.getRotateTile(prevDirection)
                if rotate != 0:
                    """
                    The angle depends on the direction switch
                    U -> R: 0       -1  -1
                    R -> D: 90      -1  -1
                    D -> L: 180     -1  -1
                    L -> U: 270      3  -1
                    
                    U -> L: Mirror          -3  1
                    L -> D: Mirror - 90      1  1
                    D -> R: Mirror - 180     1  1
                    R -> U: Mirror - 270     1  1
                    """
                    if tile.isBendable:
                        tile.bendImage(-1 * rotate * tile.getDirection() * -90, rotate == 1)
                    else:
                        tile.rotateTile(rotate)

        # Allow movement again
        self.allowMove = True

    def isValidField(self, x, y):
        inBounds = \
            self.startX <= x < self.startX + self.width and \
            self.startY <= y < self.startY + self.height

        # Check for intersection with a body tile.
        # Intersection with the tail is not possible since the tail will move away
        noIntersect = True
        for bodyIndex in range(1, len(self.snakeTiles) - 1):
            tile = self.snakeTiles[bodyIndex]
            if tile.getRect() == self.head.getRect():
                noIntersect = False
                break

        return noIntersect and inBounds

    def eatFood(self):
        # print(f"Food: {self.food.getRect()}, Head: {self.head.getRect()}")
        if self.food.getRect() == self.head.getRect():
            self.score += 100
            self.speed += 0.5

            self.updateFood()

    def updateFood(self):
        newX = self.head.getX()
        newY = self.head.getY()
        while newX in [tile.getX() for tile in self.snakeTiles] and newY in [tile.getY() for tile in self.snakeTiles]:
            newX = random.randrange(self.startX, self.startX + self.width, Configuration.SNAKE_TILE_SIZE)
            newY = random.randrange(self.startY, self.startY + self.height, Configuration.SNAKE_TILE_SIZE)

        self.food = Image(
            x=newX,
            y=newY,
            size=(Configuration.SNAKE_TILE_SIZE, Configuration.SNAKE_TILE_SIZE),
            image=f"food_{Configuration.SNAKE_FOOD[random.randint(1, 2)]}.png",
            pathToImage="images/Snake"
        )


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
            x=x,
            y=y + Configuration.SNAKE_TILE_SIZE // 2,
            size=size,
            image=image,
            pathToImage=path
        )

        self.direction = Direction.UP
        self.isBendable = tileType == "body"
        self.isTail = tileType == "tail"

        self.defaultImage = self.image

        if self.isBendable:
            self.cornerImage = pygame.transform.smoothscale(
                pygame.image.load(os.path.join(path, image.replace(tileType, "corner"))).convert(), size
            )

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

        if not self.isTail:
            rotate = self.getRotateTile(direction)
            self.rotateTile(rotate)

        self.direction = direction

    def getRotateTile(self, newDirection) -> int:
        diff = self.getDirectionDiff(newDirection)

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
            return -1
        elif diff == 1 or diff == -3:
            return 1
        else:
            return 0

    def rotateTile(self, rotation):
        self.image = pygame.transform.rotate(self.defaultImage, rotation * 90)
        self.defaultImage = self.image

    def getDirectionDiff(self, newDirection):
        return self.direction - newDirection

    def bendImage(self, angle, flip):
        self.image = pygame.transform.flip(pygame.transform.rotate(self.cornerImage, angle), flip, False)
