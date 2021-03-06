"""
    file: Snake.py
    description: Contains everything needed to play snake.

    author: Simon Stauss
    date: 15.05.2021
    licence: free
"""

import random
import pygame
from enum import IntEnum
from threading import Timer

from config import Configuration, Colors
from util import Game, Image
from loguru import logger


class Snake(Game):
    def __init__(self):
        """
        Snake is a game where the player moves around a given map controlling a snake.
        The objective is to survive as long as possible while eating as much food as possible

        This textures of the snake are copied from:
        https://rembound.com/articles/creating-a-snake-game-tutorial-with-html5

        Fruits (food) are from Victor Stambert:
        https://veo_the_artist.artstation.com/projects/oOYoDq

        Tests:
            - Variablen korrekt angelegt und ├╝berschrieben
            - Berechnung alle fehlerfrei
        """

        super().__init__(game=Configuration.GAME_SNAKE)

        # Calc width and height of the field
        self.width = Configuration.SNAKE_TILES_X * Configuration.SNAKE_TILE_SIZE
        self.height = Configuration.SNAKE_TILES_Y * Configuration.SNAKE_TILE_SIZE

        halfWidth = self.width // 2
        halfHeight = self.height // 2

        # Calculate the upper left corner of the game field
        self.startX = Configuration.windowWidth // 2 - halfWidth
        self.startY = Configuration.windowHeight // 2 - halfHeight

        # Create the border around the field
        self.borderThickness = 6
        halfThickness = self.borderThickness // 2
        self.borderRect = pygame.rect.Rect(
            self.startX - halfThickness,
            self.startY - halfThickness,
            self.width + self.borderThickness,
            self.height + self.borderThickness
        )

        # Initialize the background image
        # Image modified after: https://www.slynyrd.com/blog/2019/8/27/pixelblog-20-top-down-tiles
        self.backgroundImage = Image(
            x=0,
            y=0,
            size=Configuration.windowSize,
            image="snake_background.png",
            pathToImage="images/snake",
            hasColorkey=False
        )

        # load Endscreen image
        self.nameBackground = Image(
            x=0,
            y=0,
            size=Configuration.windowSize,
            pathToImage="images/snake/",
            image="SnakeEndscreen.png",
            hasColorkey=False
        )

        # Initialize background music and sounds
        # https://patrickdearteaga.com/royalty-free-music/childs-nightmare/
        self.backgroundMusic = "sounds/snake/background.ogg"
        try:
            self.sounds = {
                # https://mixkit.co/free-sound-effects/eat/ "Chewing something crunchy":
                "food": pygame.mixer.Sound("sounds/snake/food.wav"),
                # https://mixkit.co/free-sound-effects/arcade/ "Arcade retro game over"
                "death": pygame.mixer.Sound("sounds/snake/death.wav")
            }
        except:
            logger.critical("Snake Sounds could not be loaded")

        # Position the snake in the middle of the field
        # If width or height is odd add half of a snake tile to stay centered
        snakeX = self.startX + halfWidth + (Configuration.SNAKE_TILES_X % 2) * Configuration.SNAKE_TILE_SIZE // 2
        snakeY = self.startY + halfHeight + (Configuration.SNAKE_TILES_Y % 2) * Configuration.SNAKE_TILE_SIZE // 2

        # Create the snake tiles: 1 Head, 2 Bodies, 1 Tail
        self.snakeTiles = [
            SnakeTile(snakeX, snakeY - Configuration.SNAKE_TILE_SIZE, "head"),
            SnakeTile(snakeX, snakeY, "body"),
            SnakeTile(snakeX, snakeY + Configuration.SNAKE_TILE_SIZE, "body"),
            SnakeTile(snakeX, snakeY + 2 * Configuration.SNAKE_TILE_SIZE, "tail")
        ]

        self.head = self.snakeTiles[0]

        # Snake is moving upwards by default
        self.currentDirection = Direction.UP

        self.tickCounter = 0
        self.allowMove = True
        self.hasDied = False
        self.isGameOver = False

        # Position food randomly on the field
        self.food = None
        self.updateFood()
        self.foodEaten = False

        # Start the game
        self.run()

    def handleEvent(self, event) -> None:
        """
        This method handles the snake specific events, such as controlling the snake by key presses.

        Tests:
            - Nur bestimmte Events werden beachtet
            - Korrekte Reaktion auf die jeweiligen Events

        Args:
            event (pygame.event.Event): The to be handled event

        Returns: None
        """

        # Only react to keydown if snake is allowed to move
        if event.type == pygame.KEYDOWN and self.allowMove:
            self.allowMove = False

            # Prevent the snake going in the opposite direction
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

    def updateScreen(self) -> None:
        """
        This methods handles the drawing of elements on the screen.

        Tests:
            - Alle Elemente sind vorhanden und werden an die richtigen Stellen gezeichnet
            - Reihenfolge beim Zeichnen der Elemente wird eingehalten -> Keine ├ťberlappungen

        Returns: None
        """

        # Draw checkers background
        size = Configuration.SNAKE_TILE_SIZE
        for x in range(self.startX, self.startX + self.width, size):
            for y in range(self.startY, self.startY + self.height, size):
                if (x // 50 + y // 50) % 2 == 1:
                    color = Colors.LightGreen
                else:
                    color = Colors.VeryLightGreen
                pygame.draw.rect(self.surface, color, (x, y, size, size))

        # Draw border
        pygame.draw.rect(self.surface, Colors.Red, self.borderRect, self.borderThickness)

        # Draw Snake
        # Use the reversed list to make sure the head is always on top
        for tile in reversed(self.snakeTiles):
            self.drawImageOnSurface(tile)

        # Draw food
        self.drawImageOnSurface(self.food)

        if self.hasDied and not self.isGameOver:
            self.animateDeath()

        super().updateScreen()

    def updateGameState(self) -> None:
        """
        This method updates the snake at a configured speed.

        Tests:
            - ├ťberpr├╝fen auf Logikfehler
            - Werte aus Konfiguration korrekt gelesen

        Returns: None
        """

        if not self.isGameOver:
            # Update the position of the tiles if enough ticks passed, specified in the Configuration class
            # Also check for food and eat if there is any
            if self.tickCounter % Configuration.SNAKE_SPEED == 0 and not self.hasDied:
                self.updateSnakeTiles()
                self.eatFood()

            # Increase the tick counter
            self.tickCounter += 1

    def updateSnakeTiles(self) -> None:
        """
        This method updates every tile of the snake while also checking for collisions and rotating the tiles
        correspondingly.

        Tests:
            - Schlange bewegt sich immer in die richtige Richtung
            - Bilder werden korrekt rotiert und ausgetauscht
            - Korrektes Aktualisieren des SnakeTiles-Arrays

        Returns: None
        """

        # Calculate the coordinates of the new field the head is moving on
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

        # Check if head is allowed to move on the new field
        if self.isValidField(nextX, nextY):
            # Save the state of the tiles
            for tile in self.snakeTiles:
                tile.saveState()

            # Update the direction and position of every tile except the head
            # Dont update the new tile and tail if food was eaten
            startIndex = len(self.snakeTiles) - 1
            if self.foodEaten:
                self.foodEaten = False
                startIndex -= 1

            for index in range(startIndex, 0, -1):
                # Retrieve direction and position of the previous element
                prevTile = self.snakeTiles[index - 1]
                prevDirection = prevTile.getDirection()
                prevPos = prevTile.getRect()

                # Set direction and position to the values of the previous Element
                self.snakeTiles[index].move(prevPos, prevDirection)

            # Move the head
            self.head.move(
                pygame.rect.Rect(nextX, nextY, Configuration.SNAKE_TILE_SIZE, Configuration.SNAKE_TILE_SIZE),
                self.currentDirection
            )

            # Update body tiles to represent corners
            # Check whether a snake body-tile is at a corner and change the picture if so
            for index in range(1, startIndex + 1):
                prevDirection = self.snakeTiles[index - 1].getDirection()

                tile = self.snakeTiles[index]
                rotate = tile.getRotateTile(prevDirection)
                if rotate != 0:
                    """
                    The angle depends on the direction switch
                    U -> R: 0       -1
                    R -> D: 90      -1
                    D -> L: 180     -1
                    L -> U: 270     -1

                    U -> L: Mirror          1
                    L -> D: Mirror - 90     1
                    D -> R: Mirror - 180    1
                    R -> U: Mirror - 270    1
                    """
                    if tile.isBendable:
                        tile.bendImage(-1 * rotate * tile.getDirection() * -90, rotate == 1)
                    else:  # rotate tail
                        tile.rotateTile(rotate)

            # Allow movement again
            self.allowMove = True
        else:
            self.hasDied = True

    def isValidField(self, x, y) -> bool:
        """
        This method checks whether the head of the snake is allowed to move on to the new field.

        Tests:
            - ├ťbergebene Parameter sind im korrekten Wertebereich
            - Keine Logikfehler
            - Edge-Cases

        Args:
            x (int): The x coordinate of the new field
            y (int): The y coordinate of the new field

        Returns: true, if the head is allowed to move on the new field
        """

        # Check whether the snake remains inside the given field
        inBounds = \
            self.startX <= x < self.startX + self.width and \
            self.startY <= y < self.startY + self.height

        # Check for intersection with a tile
        noIntersect = True
        for bodyIndex in range(1, len(self.snakeTiles)):
            tile = self.snakeTiles[bodyIndex]
            # Check whether the tile intersects with the head -> collision
            if tile.getRect() == self.head.getRect():
                noIntersect = False
                break

        return noIntersect and inBounds

    def eatFood(self) -> None:
        """
        This method checks whether the head of the snake is on top of a food item. If that's the case, the food will be
        consumed by the snake and thus increasing the score and speed. A new food item will be spawned randomly.

        Tests:
            - ├ťberpr├╝fung auf ├ťberlappung der Felder immer richtig
            - Einf├╝gen eines neuen SnakeTiles an der richtigen Stelle

        Returns: None
        """

        # Check whether the head is on top of a food
        if self.food.getRect() == self.head.getRect():
            self.score += 100

            # logging

            logger.info("Snake has eaten food, new score: {}", self.score)

            self.playSound("food")

            # Reposition the food item
            self.updateFood()

            # Insert a deepcopy of the existing body AFTER the existing tile
            pos = len(self.snakeTiles) - 2

            self.snakeTiles.insert(
                pos + 1,
                self.snakeTiles[pos].__copy__()
            )

            self.foodEaten = True

    def updateFood(self) -> None:
        """
        This method moves a food item to a random location and randomly changes the type of the food.

        Tests:
            - Neue Position des Essens hat keine ├ťberschneidungen mit der Snake
            - Variablen werden korrekt gespeichert und gesetzt
            - Bild wird ohne Fehler aktualisiert

        Returns: None
        """

        # Create a new pair of coordinates
        newRect = self.head.getRect()

        # Choose new random positions if the random coordinate is inside the snake
        while newRect in [tile.getRect() for tile in self.snakeTiles]:
            newX = random.randrange(self.startX, self.startX + self.width, Configuration.SNAKE_TILE_SIZE)
            newY = random.randrange(self.startY, self.startY + self.height, Configuration.SNAKE_TILE_SIZE)

            newRect = pygame.rect.Rect(newX, newY, Configuration.SNAKE_TILE_SIZE, Configuration.SNAKE_TILE_SIZE)

        # Create the food item at the created position
        # Choose a random image
        self.food = Image(
            x=newRect.x,
            y=newRect.y,
            size=(Configuration.SNAKE_TILE_SIZE, Configuration.SNAKE_TILE_SIZE),
            image=f"food_{Configuration.SNAKE_FOOD[random.randint(0, len(Configuration.SNAKE_FOOD) - 1)]}.png",
            pathToImage="images/Snake"
        )

    def animateDeath(self) -> None:
        """
        This method animates the death of the snake by moving the entire body backwards and replacing the head image

        Tests:
            - Bewegen der Schlange ohne Probleme und Fehler
            - Edge-Cases: Gerade erst gegessen? Alle Ecken zur├╝ckgesetzt?

        Returns: None
        """

        # Play death sound
        self.playSound("death")

        # Reset the tiles to their previous state
        self.snakeTiles = [tile.getPreviousState() for tile in self.snakeTiles]

        self.isGameOver = True

        # Quit the game and ask for the users name
        Timer(1, self.quit).start()


class Direction(IntEnum):
    """
    IntEnum class representing the direction (UP, RIGHT, DOWN, LEFT) of a tile in Snake. Merely for cosmetic purposes.

    Tests:
        - Variablen werden korrekt angelegt
        - Variablen werden korrekt zur├╝ckgegeben
    """

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class SnakeTile(Image):
    def __init__(self, x, y, tileType):
        """
        A SnakeTile represents a tile-fragment of the snake. There is always a head tile, at least two body tiles and a
        tail tile.

        Tests:
            - tileType nur einer der g├╝ltigen M├Âglichkeiten
            - Bild wird richtig angelegt

        Args:
            x (int): The x position where the tile is to be placed on the screen
            y (int): The y position where the tile is to be placed on the screen
            tileType (str): The type of the tile. "head", "body" or "tail"
        """

        # Choose the image depending on the tileType
        image = "snake_" + tileType + ".png"
        path = "images/snake"
        size = (Configuration.SNAKE_TILE_SIZE, Configuration.SNAKE_TILE_SIZE)

        super().__init__(
            x=x,
            y=y,
            size=size,
            image=image,
            pathToImage=path
        )

        # Save the type of the tile
        self.tileType = tileType

        # Texture is facing upwards by default
        self.direction = Direction.UP

        # Body tiles can be bend by default
        self.isBendable = tileType == "body"

        # Save whether the tile is the tail of the snake for later use
        self.isTail = tileType == "tail"

        # Save a copy of the image to switch back to after using the cornerImage
        self.defaultImage = self.image

        # Load the corner image if the tile is a body tile
        if self.isBendable:
            self.cornerImage = Image(
                x=x,
                y=y,
                size=size,
                image="snake_corner.png",
                pathToImage=path
            )

        # Save a the previous state to animate the death of the snake
        self.prevState = None

    def __copy__(self):
        """
        This method deepcopies a snake tile and is used for increasing the length of the snake after eating food and
        saving the previous state of the tile

        Tests:
            - Alle Variablen werden korrekt gesetzt
            - Zur├╝ckgegebener Wert ist eine Kopie der SnakeTile

        Returns (SnakeTile): A new SnakeTile object exactly the same as the current object
        """

        cloneTile = SnakeTile(self.getX(), self.getY(), self.tileType)
        cloneTile.direction = self.direction
        cloneTile.image = self.image.copy()
        if cloneTile.isBendable:
            cloneTile.cornerImage.image = self.cornerImage.getImage().copy()

        cloneTile.defaultImage = self.defaultImage.copy()
        cloneTile.rect = pygame.rect.Rect(self.rect)
        cloneTile.prevState = self.getPreviousState()

        return cloneTile

    def move(self, rect, direction) -> None:
        """
        Moves the tile to a given position and facing in a specific direction.

        Tests:
            - Bewegung wird an die korrekte Stelle durchgef├╝hrt
            - ├ťbergabeparameter g├╝ltig? (auf dem Spielfeld und Richtung aus dem Enum)

        Args:
            rect (pygame.rect.Rect): The position to move the tile to
            direction (Direction): The direction the tile will be facing

        Returns: None
        """

        self.setRect(rect)
        self.setDirection(direction)

    def getPreviousState(self):
        """
        Get the previous state of the tile

        Tests:
            - Zur├╝ckgegebener Wert ist eine SnakeTiles Instanz
            - prevState spiegelt tats├Ąchlich den vorherigen Stand wieder

        Returns (SnakeTile): A SnakeTile representing the previous state
        """

        return self.prevState

    def saveState(self) -> None:
        """
        This method saves a copy of the element to the prevState variable.

        Tests:
            - Kopie wird ohne Fehler erzeugt
            - Variable wird korrekt gesetzt

        Returns: None
        """

        self.prevState = self.__copy__()

    def getDirection(self) -> Direction:
        """
        Get the direction the tile is facing.

        Tests:
            - Wert wird korrekt zur├╝ckgegeben
            - Variable spiegelt wirklich Richtung des SnakeTile wieder

        Returns: The direction of the snake tile
        """

        return self.direction

    def setDirection(self, direction) -> None:
        """
        Update the direction of a tile. Also rotates the image to fit the direction.

        Tests:
            - Variable wird korrekt gesetzt
            - ├ťbergebene Richtung ist valide

        Args:
            direction (Direction): The new direction

        Returns: None
        """

        # Dont rotate the tile since it's rotating is handled separately due to corner images
        if not self.isTail:
            # Get the direction of the rotation and rotate the image
            rotate = self.getRotateTile(direction)
            self.rotateTile(rotate)

        # Update the direction of the tile
        self.direction = direction

    def getRotateTile(self, newDirection) -> int:
        """
        Returns the direction of the the rotate depending on the new direction.

        Tests:
            - Wert wird korrekt zur├╝ckgegeben
            - Berechnung ergibt immer das selbe

        Args:
            newDirection (Direction): The direction the tile will be facing next

        Returns: 1, if image has to be rotated left, -1, if the image has to be rotated right and 0 if something went
        wrong
        """

        # Get the difference of the current and new direction
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

    def rotateTile(self, rotation) -> None:
        """
        Rotate the image of a tile.

        Tests:
            - Rotation wird korrekt durchgef├╝hrt
            - Variablen werden ├╝berschrieben

        Args:
            rotation (int): The direction of the rotation: 1 -> rotate left, -1 -> rotate right

        Returns: None
        """

        self.image = pygame.transform.rotate(self.defaultImage, rotation * 90)
        self.defaultImage = self.image

    def getDirectionDiff(self, newDirection) -> int:
        """
        Get the numerical difference of the current and a new direction.

        Tests:
            - ├ťbergebener Parameter ist g├╝ltig
            - Berechnung ergibt f├╝r die gleichen Parameter immer das selbe Ergebnis

        Args:
            newDirection (Direction): The direction to be subtracted with

        Returns: The numerical difference of two directions
        """

        return self.direction - newDirection

    def bendImage(self, angle, flip) -> None:
        """
        Replace the image of a body tile with the corner image. Also handle rotation and horizontal mirroring of the
        image.

        Tests:
            - Bild wird richtig rotiert und gespiegelt
            - ├ťbergebene Parameter sind g├╝ltig

        Args:
            angle (int): The angle to rotate the image by
            flip (bool): Specifies whether the image has to be mirrored horizontally

        Returns: None
        """

        self.image = pygame.transform.flip(pygame.transform.rotate(self.cornerImage.getImage(), angle), flip, False)
