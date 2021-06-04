import os
import pygame
import pygame_menu
from pygame_textinput import TextInput

from config import Configuration, Colors


class Game:
    def __init__(self, title=Configuration.windowTitle, windowSize=Configuration.windowSize):
        """
        Superclass for every component in this application.

        Implements predefined behaviour and supplies the children with method-prototypes, which will be slightly
        modified by the children.

        Args:
            title (str): The title of the pygame window
            windowSize (tuple[int, int]): The size of the pygame window
        """

        self.isRunning = True
        self.isGameOver = False
        self.isPaused = False
        self.hasScore = True
        self.score = 0
        self.scoreX, self.scoreY = (windowSize[0] // 2, 100)

        self.windowSize = windowSize
        self.events = None

        self.clock = pygame.time.Clock()

        # Pygame specific stuff
        pygame.init()

        # Display
        pygame.display.set_caption(title)
        self.surface = pygame.display.set_mode(size=self.windowSize)
        self.backgroundImage = None

        # Music
        pygame.mixer.init()
        self.backgroundMusic = None
        self.sounds = {}

        # Font
        pygame.font.init()
        self.defaultFont = pygame.font.SysFont("arial", 25)

        # Create the pause menu
        self.pauseMenu = pygame_menu.Menu(
            title="Spiel pausiert",
            width=self.windowSize[0] / 2,
            height=self.windowSize[1] / 2,
            theme=pygame_menu.themes.THEME_DARK  # title_close_button=False
        )
        self.pauseMenu.add.button("Resume Playing", self.togglePause)
        self.pauseMenu.add.button("Quit", self.quit)

        # Draw the pause menu by default on pause (ESC)
        self.pauseBehaviour = self.drawMenu

        # Create variables needed for the game end screen
        self.nameSubmit = False
        self.nameInputX, self.nameInputY = (Configuration.windowWidth // 2, Configuration.windowHeight // 2)
        self.nameBackground = Image(
            x=0,
            y=0,
            size=Configuration.windowSize,
            image="nameInput.png",
            hasColorkey=False
        )

    def run(self):
        """
        Main loop of the application.
        Calls methods self.updateEvents(), self.updateGameState() and self.updateScreen() while self.isRunning is True.
        If self.isRunning is False, self.gameOver() will be called to ask the user for their name.
        
        !DO NOT OVERWRITE THIS METHOD!

        Returns: None
        """

        # Play background music
        if self.backgroundMusic is not None:
            pygame.mixer.music.load(self.backgroundMusic)
            pygame.mixer.music.set_volume(Configuration.MUSIC_VOLUME)
            pygame.mixer.music.play(-1)

        # Main loop
        while self.isRunning:
            self.updateEvents()

            if not self.isPaused:
                self.updateGameState()

            if self.backgroundImage is not None:
                self.drawImageOnSurface(self.backgroundImage)

            self.updateScreen()

            # Target 60 FPS
            self.clock.tick(Configuration.FRAMERATE)

        if self.isGameOver and self.hasScore:
            self.gameOver()

    def updateEvents(self, nameInput=False):
        """
        This functions gets every pygame event and handles quit and pause.
        Unhandled Events are passed down to self.handleEvent() to be handled by children classes.

        !DO NOT OVERWRITE THIS METHOD!

        Args:
            nameInput (bool): Specifies whether the game is currently waiting for the user to input their name

        Returns: None
        """

        self.events = pygame.event.get()

        # Loop through every event
        for event in self.events:
            eventHandled = False
            
            if event.type == pygame.QUIT:
                self.quit()
                eventHandled = True
            if event.type == pygame.KEYDOWN:
                # Toggle pause on ESC
                if event.key == pygame.K_ESCAPE:
                    self.togglePause()
                    eventHandled = True

                if nameInput and event.key == pygame.K_RETURN:
                    self.nameSubmit = True
                    eventHandled = True

            if not eventHandled:
                # further event handling
                self.handleEvent(event)

    def handleEvent(self, event):
        """
        This method specifies game-specific behavior on pygame events.
        Overwrite this method in your class!

        Args:
            event (pygame.event.Event): The to be handled event

        Returns: None
        """

        # print("Unhandled event:", event)
        pass

    def updateGameState(self):
        """
        This method handles all game-specific state changes. It is to be implemented by the children classes.

        Returns: None
        """

        pass

    def updateScreen(self):
        """
        This method updates the pygame window.
        It also handles pause behaviour.
        """

        if self.isPaused:
            self.pauseBehaviour()

        if self.hasScore:
            # Print score at a given position
            self.drawTextOnSurface(f"Score: {self.score}", (self.scoreX, self.scoreY))

        pygame.display.update()

    def drawTextOnSurface(self, text, position, color=Colors.White, font=None, surface=None, center=True):
        """
        This method draws a given text on a surface.

        Args:
            color (tuple[int, int, int]): The color of the drawn text
            text (String): The text to draw
            position ((int, int)): The position of the top left corner of the text
            font (pygame.font.Font): The font of the text. Defaults to self.defaultFont
            surface (pygame.surface.Surface): The surface to draw the text on. Defaults to the default surface of the
                class
            center (Boolean): When True, center of the text is moved to position, defaults to True

        Returns: None
        """

        if surface is None:
            surface = self.surface

        if font is None:
            font = self.defaultFont

        textSurface = font.render(text, True, color)

        if center:
            textRect = textSurface.get_rect()
            position = (position[0] - textRect.width / 2, position[1] - textRect.height / 2)

        surface.blit(textSurface, position)

    def drawImageOnSurface(self, image, position=None, surface=None):
        """
        This method draws a given image on a surface.

        Args:
            image (Image): The image to draw
            position (pygame.rect.Rect): The position to draw the image at. Defaults to the position saved in the image
             class
            surface (pygame.surface.Surface): The surface to draw the image on. Defaults to the default surface of the
             game

        Returns: None
        """

        if position is None:
            position = image.getRect()

        if surface is None:
            surface = self.surface

        surface.blit(image.getImage(), position)

    def drawMenu(self, menu=None):
        """
        This method draws a given menu to the screen. Default menu is the pause menu

        Args:
            menu (pygame_menu.Menu): The menu to draw
        """

        if not menu:
            menu = self.pauseMenu

        # Pass events to the menu und draw it onto the surface if enabled
        if menu.is_enabled():
            menu.update(self.events)
            menu.draw(self.surface)

    def togglePause(self):
        """
        This method toggles self.isPaused and is called once the user pressed the ESC-key.

        Returns: None
        """

        self.isPaused = not self.isPaused

    def playSound(self, sound, volume=1.0):
        """
        This method plays a sound.

        Args:
            sound (str): The name of the sound
            volume (float): The volume of the sound. Ranges from 0.0 to 1.0, where 1.0 is the loudest

        Returns: None
        """
        sound = self.sounds[sound]

        if sound:
            sound.set_volume(volume)
            sound.play()

    def gameOver(self):
        """
        This method is called once the game finished.
        It asks the user to input a name and saves their score afterwards.

        Returns: None
        """

        # Ask the user for their name to save the score
        name = self.getUserName()
        self.saveScore(name)

    def getUserName(self) -> str:
        """
        This method shows an input dialog for the user to write their name.
        The name will be used in the scoreboard.

        Returns: The name of the user as a string
        """

        nameInput = TextInput()

        while not self.nameSubmit:
            self.updateEvents(True)

            nameInput.update(self.events)

            self.drawImageOnSurface(self.nameBackground)
            self.surface.blit(nameInput.get_surface(), (self.nameInputX, self.nameInputY))

            pygame.display.update()

            self.clock.tick(Configuration.FRAMERATE)

        return nameInput.get_text()

    def saveScore(self, name):
        """
        This method saves the score of the user in a game

        Args:
            name (str): The name of the user

        Returns: None
        """

        # print(self.score, name)
        pass

    def quit(self):
        """
        This method is called once the player quits the game.
        It also stops the background music
        """

        pygame.mixer.music.stop()

        self.isRunning = False


class GameContainer(Game):
    def __init__(self):
        """
        Children of class Game.

        This class displays the main menu adding the ability to start games and adjust settings.
        """
        super().__init__()

        # Disable the score display
        self.hasScore = False
        
        # Create menus
        # https://pygame-menu.readthedocs.io/en/4.0.1/index.html
        self.mainMenu = pygame_menu.Menu(
            title="Herzlich Willkommen in der Spielekiste!",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK  # title_close_button=False
        )
        self.playMenu = pygame_menu.Menu(
            title="Spiel wählen",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK
        )
        self.optionsMenu = pygame_menu.Menu(
            title="Optionen",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK
        )
        self.highscoreMenu = pygame_menu.Menu(
            title="Highscores",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK
        )

        # Add buttons to main menu
        self.mainMenu.add.button("Play", self.playMenu)
        self.mainMenu.add.button("Options", self.optionsMenu)
        self.mainMenu.add.button("Highscores", self.highscoreMenu)
        self.mainMenu.add.button("Quit", self.quit)

        # Add games to play menu
        self.playMenu.add.button("Play Snake", self.startSnake)
        self.playMenu.add.button("Play Tic Tac Toe", self.startTTT)
        self.playMenu.add.button("Play Pong", self.startPong)
        self.playMenu.add.button("Play Space-Invader", self.startSpaceInvader)
        self.playMenu.add.button("Back", pygame_menu.events.BACK)

        # Add buttons to options menu
        self.optionsMenu.add.button("Back", pygame_menu.events.BACK)

        # Add buttons to highscore menu
        self.highscoreMenu.add.button("Back", pygame_menu.events.BACK)

        # Quit the game on esc
        self.pauseBehaviour = self.quit

        # Run the container
        self.run()

    def updateScreen(self):
        # Draw the main menu
        self.drawMenu(self.mainMenu)

        super().updateScreen()

    @staticmethod
    def startSnake():
        """
        This function starts the Snake-Game
        """

        from games.Snake import Snake
        Snake()

    @staticmethod
    def startTTT():
        """
        This function starts the TicTacToe-Game
        """

        from games.TicTacToe import TicTacToe
        TicTacToe()

    @staticmethod
    def startPong():
        """
        This functions starts the Pong-Game
        """

        from games.Pong import Pong
        Pong()

    @staticmethod
    def startSpaceInvader():
        """
        This functions starts the Pong-Game
        """

        from games.SpaceInvader import SpaceInvader
        SpaceInvader()

    def quit(self):
        """
        This method quits the application.
        """

        pygame.quit()
        exit(0)


class Image(pygame.sprite.Sprite):
    def __init__(self, x, y, size, image, pathToImage="images/", colorkey=(0, 0, 0), hasColorkey=True):
        """
        This class represents a image in a game. This can be a texture, character, etc.
        It's parent is pygame.sprite.Sprite

        Args:
            x (int): The position on the screen on the x-axis
            y (int): The position on the screen on the y-axis
            size (tuple[int, int]): The size of the image
            image (str): The name of the image file to open
            pathToImage (str): The name of the folder of the image
            colorkey (tuple[int, int, int]): The color to be replaced with transparent pixels
            hasColorkey (bool): Specifies whether the color given in colorkey will be replaced
        """
        super().__init__()

        # Load the given image
        self.image = pygame.transform.smoothscale(pygame.image.load(os.path.join(pathToImage, image)).convert(), size)

        # Apply colorkey
        if hasColorkey:
            self.image.set_colorkey(colorkey)

        # Create size variable and position the image on the screen
        self.SIZE = pygame.Rect(0, 0, size[0], size[1])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def getX(self) -> int:
        """
        This method returns the most left x value of the image

        Returns: x-coordinate of the image
        """

        return self.rect.x

    def setX(self, x) -> None:
        """
        This method moves the image to the given value on the x-axis

        Args:
            x (int): The x-coordinate to move the image to

        Returns: None
        """

        self.rect.x = x

    def getY(self) -> int:
        """
        This method returns the y-axis value of the image

        Returns: y-coordinate of the image
        """

        return self.rect.y

    def setY(self, y) -> None:
        """
        This method moves the image to the given value on the y-axis

        Args:
            y (int): The y-coordinate to move the image to

        Returns: None
        """

        self.rect.y = y

    def getRect(self) -> pygame.rect.Rect:
        """
        This method returns the rect of the image.

        Returns: The rect of the image
        """

        return self.rect

    def setRect(self, rect):
        """
        This method updates the rect of the image.

        Args:
            rect (pygame.rect.Rect): The new rect object

        Returns: None
        """

        self.rect = pygame.rect.Rect(rect)

    def getImage(self) -> pygame.surface.Surface:
        """
        This method returns the image surface of the image.

        Returns: The image surface of the image
        """

        return self.image

    def setImage(self, image):
        """
        This method updates the image of the image.

        Args:
            image (pygame.surface.Surface): The new image surface

        Returns: None
        """

        self.image = image
