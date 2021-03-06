"""
    file: TicTacToe.py
    description: Contains everything needed to play TicTacToe.

    author: Simon Stauss
    date: 30.05.2021
    licence: free
"""

import pygame
from threading import Timer

from typing import Tuple

from config import Colors, Configuration
from util import Game, Image


class TicTacToe(Game):
    def __init__(self):
        """
        TicTacToe is game where two players play against each other on a 3x3 field. The first player to reach 3 symbols
        in a row, column or diagonal wins.

        Tests:
            - Variablen korrekt angelegt
            - Berechnungen alle fehlerfrei
        """
        super().__init__(game=Configuration.GAME_TTT)

        # Disable score but still show name enter if someone won
        self.hasScore = False
        self.showGameOver = True
        self.gameOverTimer = Timer(1, self.quit)
        self.draw = False

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

        # load endscreen image
        self.nameBackground = Image(
            x=0,
            y=0,
            size=Configuration.windowSize,
            pathToImage="images/ttt/",
            image="TTTEndscreen.png",
            hasColorkey=False
        )

        # Background music
        # From: https://www.chosic.com/download-audio/?t=27247&tag=Games
        self.backgroundMusic = "sounds/ttt/background.mp3"

        # Sounds
        self.sounds = {
            # From: https://mixkit.co/free-sound-effects/click/ "Modern click box check"
            "click": pygame.mixer.Sound("sounds/ttt/click.wav"),
            # From: https://mixkit.co/free-sound-effects/win/ "Quick win video game notification"
            "win": pygame.mixer.Sound("sounds/ttt/win.wav")
        }

        # Fonts
        self.mouseFont = pygame.font.SysFont("arial", Configuration.TTT_TILE_SIZE // 3, True)
        self.symbolFont = pygame.font.SysFont("arial", Configuration.TTT_TILE_SIZE // 2, True)
        self.notifyFont = pygame.font.SysFont("arial", Configuration.TTT_TILE_SIZE, True)

        # Game specific variables
        self.players = ["X", "O"]
        self.turns = 0
        self.currentPlayer = self.players[self.turns]
        self.winner = None

        # Get the current position of the mouse and disable default pointer
        self.mousePos = pygame.mouse.get_pos()
        pygame.mouse.set_visible(False)

        # Create the default field
        self.fields = {}
        for x in range(3):
            for y in range(3):
                posX = self.startX + Configuration.TTT_TILE_SIZE // 2 + x * Configuration.TTT_TILE_SIZE
                posY = self.startY + Configuration.TTT_TILE_SIZE // 2 + y * Configuration.TTT_TILE_SIZE

                self.fields.update({
                    self.indexFromXY(x, y): TTTTile(posX, posY)
                })

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

    def updateScreen(self) -> None:
        """
        This method draws the field and placed symbols on the screen. It also draws the symbol of the current player at
        the position of the mouse.
        It also notifies the players of a winner or draw.

        Tests:
            - Darstellung korrekt und in richtiger Reihenfolge
            - Variablen alle korrekt gesetzt

        Returns: None
        """

        # Draw white background
        pygame.draw.rect(
            self.surface,
            Colors.White,
            (self.startX, self.startY, 3 * Configuration.TTT_TILE_SIZE, 3 * Configuration.TTT_TILE_SIZE)
        )

        # Draw symbols and borders
        for field in self.fields.values():
            fieldPos = field.getPos()

            # Draw the border around the field
            borderX, borderY = fieldPos
            borderX -= Configuration.TTT_TILE_SIZE // 2
            borderY -= Configuration.TTT_TILE_SIZE // 2
            pygame.draw.rect(
                self.surface,
                Colors.Black,
                (borderX, borderY, Configuration.TTT_TILE_SIZE, Configuration.TTT_TILE_SIZE),
                4
            )

            # Draw the symbol
            self.drawTextOnSurface(field.getPlayer(), fieldPos, Colors.Black, font=self.symbolFont)

        # Notify users of a draw or the winner
        if self.draw:
            self.gameStateNotification("It's a draw!", True)
        elif self.winner in self.players:
            self.isGameOver = True
            self.gameStateNotification(f"{self.winner} won!")
        else:
            # Draw the symbol of the current user at the position of the mouse
            self.drawTextOnSurface(self.currentPlayer, self.mousePos, Colors.Black, font=self.mouseFont)

        super().updateScreen()

    def updateGameState(self) -> None:
        """
        This method updates the state of the game. It checks whether a player has won or if the game is a draw.

        Tests:
            - ??berpr??fung auf Gewinner korrekt
            - Gleiche Kombination der Felder f??hrt immer zum selben Ergebnis

        Returns: None
        """

        # Check every possibility a player can with with
        for win in self.winPossibilities:
            # Check whether every field of the win possibility is occupied by the same player
            hasWon = True
            for index in win:
                hasWon = hasWon and self.fields[index].getPlayer() == self.currentPlayer

            # Notify the users and end the game if that's the case
            if hasWon:
                self.winner = self.currentPlayer
                break

        self.draw = self.turns == 9 and not self.winner

        # Update the player
        self.currentPlayer = self.players[self.turns % 2]

    def handleEvent(self, event) -> None:
        """
        This method handles the events needed for the game to work. It reacts to a mouse click with the primary button
        and mouse motion.

        Tests:
            - Gleiches Event f??r immer zum selben Ergebnis
            - Variablen werden korrekt gesetzt

        Args:
            event (pygame.event.Event):

        Returns: None
        """

        if not self.isGameOver:
            # Mouse left click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Get the field the player clicked on
                posX = event.pos[0]
                posY = event.pos[1]
                fieldX = int((posX - self.startX) // Configuration.TTT_TILE_SIZE)
                fieldY = int((posY - self.startY) // Configuration.TTT_TILE_SIZE)

                # Check if field is valid
                if fieldX in range(3) and fieldY in range(3):
                    # Update the field and turn count
                    if self.fields[self.indexFromXY(fieldX, fieldY)].setPlayer(self.currentPlayer):
                        self.playSound("click")
                        self.turns += 1
            # Display the current player at the position of the mouse
            elif event.type == pygame.MOUSEMOTION:
                self.mousePos = event.pos

    def gameStateNotification(self, text, isDraw=False) -> None:
        """
        Notifies the user of a change in the game state. This means that either someone won or the game is a draw.
        It also enables the regular mouse pointer again and plays a sound.

        Tests:
            - Parameter werden korrekt ??bergeben
            - Farbe des Texts wird korrekt ausgew??hlt

        Args:
            text (str): The text that will be displayed
            isDraw (bool): Specifies whether it's a draw. The text will change from green to red if that's the case

        Returns: None
        """

        pygame.mouse.set_visible(True)
        self.playSound("win", 0.5)

        # Choose a different color for the draw text
        color = Colors.LightGreen
        if isDraw:
            color = Colors.Red

        # Draw the text to notify the user
        self.drawTextOnSurface(
            text,
            (Configuration.windowWidth // 2, Configuration.windowHeight // 2),
            color,
            font=self.notifyFont
        )

        # Quit the game in a second if the timer isn't running
        if not self.gameOverTimer.is_alive():
            self.gameOverTimer.start()

    @staticmethod
    def indexFromXY(x, y) -> int:
        """
        This method converts x and y coordinates into an usable index.
        Used for the field array

        Tests:
            - Parameter werden korrekt ??bergeben
            - Die selbe Kombination (x, y) f??hrt immer zum selben Index

        Args:
            x (int): The x coordinate ranging between [0, 2]
            y (int): The y coordinate ranging between [0, 2]

        Returns: An index in the range of [0, 8]
        """

        return x + 3 * y


class TTTTile:
    def __init__(self, x, y):
        """
        This class represents a TicTacToeTile.
        It contains the position of the tile and the player occupying it.

        Tests:
            - Variablen werden korrekt ??bergeben
            - Variablen werden korrekt gesetzt

        Args:
            x (int): The x coordinate of the center of the tile
            y (int): The y coordinate of the center of the tile
        """

        self.x = x
        self.y = y
        self.player = ""

    def setPlayer(self, player) -> bool:
        """
        Updates the player of a field, if it's not already occupied by someone.

        Tests:
            - R??ckgabewert wird richtig zur??ckgegeben
            - Variable wird ver??ndert

        Args:
            player (str): The player that wants to occupy the field

        Returns: Whether the field was empty.
        """

        # Update only if the field was empty
        if self.player == "":
            self.player = player

            return True
        else:
            return False

    def getPlayer(self) -> str:
        """
        Returns the player of the field.

        Tests:
            - Wert wird korrekt zur??ckgegeben
            - Variable enth??lt ein einziges Zeichen aus ["X", "Y"] oder gar kein Zeichen

        Returns: The player occupying the field
        """

        return self.player

      
    def getPos(self):

        """
        Returns the position of the tile.
        It is needed to render the symbol of the player on the screen.

        Tests:
            - Wert wird korrekt zur??ckgegeben
            - Tupel wird korrekt erstellt und spiegelt die Position wieder

        Returns (tuple[int, int]: A tuple containing both the x and y coordinate.
        """

        return self.x, self.y
