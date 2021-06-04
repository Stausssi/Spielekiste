import random

import pygame

from config import Colors, Configuration
from util import Game, Image


class TicTacToe(Game):
    def __init__(self):
        super().__init__()

        # Disable score
        self.hasScore = False

        # Center the field
        self.startX = Configuration.windowWidth // 2 - Configuration.TTT_TILE_SIZE * 1.5
        self.startY = Configuration.windowHeight // 2 - Configuration.TTT_TILE_SIZE * 1.5

        # Background image
        # From: https://www.vecteezy.com/vector-art/434094-wood-texture
        self.backgroundImage = Image(
            x=0,
            y=0,
            size=Configuration.windowSize,
            image="background.jpg",
            pathToImage="images/ttt",
            hasColorkey=False
        )

        # Background music
        self.backgroundMusic = None

        # Sounds
        self.sounds = {
            "click": None,
            "win": None
        }

        self.players = ["X", "O"]
        self.turns = random.randint(0, 1)
        self.currentPlayer = self.players[self.turns]

        # Save the state of the field
        self.field = [
            "", "", "",
            "", "", "",
            "", "", ""
        ]

        # Save all possibilities a player can win with
        self.winPossibilities = [
            [0, 1, 2],
            [0, 3, 6],
            [0, 4, 8],
            [1, 4, 7],
            [2, 4, 6],
            [2, 5, 8],
            [3, 4, 5],
            [6, 7, 8]
        ]

        # Run the game
        self.run()

    def updateScreen(self):
        # Draw fields
        for x in range(3):
            for y in range(3):
                size = Configuration.TTT_TILE_SIZE
                xPos = self.startX + x * size
                yPos = self.startY + y * size

                # Draw white field
                pygame.draw.rect(
                    self.surface,
                    Colors.White,
                    (xPos, yPos, size, size)
                )

                # Draw black field border
                pygame.draw.rect(
                    self.surface,
                    Colors.Black,
                    (xPos, yPos, size, size),
                    4
                )

        # Draw X and Os
        # print(self.field)
        x = self.startX + Configuration.TTT_TILE_SIZE // 2
        y = self.startY + Configuration.TTT_TILE_SIZE // 2

        for field in self.field:
            print(x, y)
            self.drawTextOnSurface(field, (x, y), Colors.Black)

            x += Configuration.TTT_TILE_SIZE
            x %= self.startX + 3 * Configuration.TTT_TILE_SIZE
            y += Configuration.TTT_TILE_SIZE
            y %= self.startY + 3 * Configuration.TTT_TILE_SIZE

        super().updateScreen()

    def updateGameState(self):
        # Snippet from: https://stackoverflow.com/questions/6294179/how-to-find-all-occurrences-of-an-element-in-a-list
        indices = [i for i, x in enumerate(self.field) if x == self.currentPlayer]
        if indices in self.winPossibilities:
            # TODO: Inform players of the winner
            self.isRunning = False
            self.isGameOver = True

        # Update the player
        self.currentPlayer = self.players[self.turns % 2]

    def handleEvent(self, event):
        # Mouse left click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Get the field the player clicked on
            posX = event.pos[0]
            posY = event.pos[1]
            fieldX = int((posX - self.startX) // Configuration.TTT_TILE_SIZE)
            fieldY = int((posY - self.startY) // Configuration.TTT_TILE_SIZE)

            # Check if field is valid
            if self.isValid(fieldX, fieldY):
                fieldPos = fieldX + 3 * fieldY

                # Update the field and turn count
                self.field[fieldPos] = self.currentPlayer
                self.turns += 1

    def isValid(self, x, y):
        """
        This method returns whether the player can place their symbol on a field.

        Args:
            x: The x-coordinate of the field
            y: The y-coordinate of the field

        Returns: True, if the field is valid
        """

        inRange = x in [0, 1, 2] and y in [0, 1, 2]
        pos = x + 3 * y
        return inRange and self.field[pos] == ""
