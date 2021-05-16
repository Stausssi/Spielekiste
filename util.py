import pygame
import pygame_menu

from config import Configuration


class Game:
    def __init__(self, title="Niklas und Simons Spielekiste", windowSize=Configuration.windowSize):
        """
        Superclass for every component in this application.

        Implements predefined behaviour and supplies the children with method-prototypes, which will be slightly modified
        by the children.

        :param title: The title of the pygame window
        :type title: str
        :param windowSize: The size of the pigame window
        :type windowSize: (int, int)
        """

        self.title = title

        self.isRunning = True
        self.isPaused = False
        self.windowSize = windowSize
        self.events = None

        self.clock = pygame.time.Clock()

        # Pygame specific stuff
        pygame.init()
        pygame.display.set_caption(self.title)

        self.surface = pygame.display.set_mode(size=self.windowSize)

        self.pauseMenu = pygame_menu.Menu(
            title="Spiel pausiert",
            width=self.windowSize[0] / 2,
            height=self.windowSize[1] / 2,
            theme=pygame_menu.themes.THEME_DARK  # title_close_button=False
        )
        self.pauseMenu.add.button("Resume Playing", self.togglePause)
        self.pauseMenu.add.button("Quit", self.quit)

        self.pauseBehaviour = self.drawMenu

    def run(self):
        """
        Main loop of the application.
        Calls methods self.updateEvents(), self.updateGameState() and self.updateScreen() while self.isRunning is true

        :return: None
        """

        while self.isRunning:
            self.updateEvents()

            if not self.isPaused:
                self.updateGameState()

            self.updateScreen()

            # Target 60 FPS
            self.clock.tick(60)

    def updateEvents(self):
        """
        This functions gets every pygame event and handles quit and pause.
        Unhandled Events are passed down to self.handleEvent() to be handled by children classes.

        :return: None
        """

        self.events = pygame.event.get()

        # Loop through every event
        for event in self.events:
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                # Toggle pause on ESC
                if event.key == pygame.K_ESCAPE:
                    self.togglePause()
            else:
                # further event handling
                self.handleEvent(event)

    def handleEvent(self, event):
        """
        This method specifies game-specific behavior on pygame events

        :param event: The to be handled event
        :type event: pygame.event.Event
        :return: None
        """

        # print("Unhandled event:", event)
        pass

    def updateGameState(self):
        """
        This method handles all game-specific state changes. It is to be implemented by the children classes.

        :return: None
        """

        pass

    def updateScreen(self):
        """
        This method updates the pygame window by drawing object.
        It also handles the pause behaviour.

        :return: None
        """

        if self.isPaused:
            self.pauseBehaviour()

        pygame.display.update()

    def drawMenu(self, menu=None):
        """
        This method draws a given menu to the screen

        :param menu: The menu to draw
        :type menu: pygame_menu.Menu
        :return: None
        """

        if not menu:
            menu = self.pauseMenu

        # Pass events to the menu und draw it onto the surface if enabled
        if menu.is_enabled():
            menu.update(self.events)
            menu.draw(self.surface)

    def togglePause(self):
        """
        This method toggles self.isPaused and is called once the user pressed the ESC-key

        :return: None
        """

        self.isPaused = not self.isPaused

    def quit(self):
        """
        This method is called once the player quits the game.

        :return: None
        """

        self.isRunning = False


class GameContainer(Game):
    def __init__(self):
        """
        Children of class Game.

        This class displays the main menu adding the ability to start games and adjust settings.
        """
        super().__init__()

        # Create menus
        # https://pygame-menu.readthedocs.io/en/4.0.1/index.html
        self.mainMenu = pygame_menu.Menu(
            title="Herzlich Willkommen in der Spielekiste!",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK  # title_close_button=False
        )
        self.optionsMenu = pygame_menu.Menu(
            title="Optionen",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK
        )

        # Add buttons to main menu
        self.mainMenu.add.button("Play Snake", self.startSnake)
        self.mainMenu.add.button("Play Tic Tac Toe", self.startTTT)
        self.mainMenu.add.button("Options", self.optionsMenu)
        self.mainMenu.add.button("Quit", self.quit)

        # Add buttons to options menu
        self.optionsMenu.add.button("Back", pygame_menu.events.BACK)

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

        :return: None
        """

        from games import Snake
        Snake()

    @staticmethod
    def startTTT():
        """
        This function starts the TicTacToe-Game

        :return: None
        """

        from games import TicTacToe
        TicTacToe()

    def quit(self):
        """
        This method quits the application.

        :return: None
        """

        pygame.quit()
        exit(0)
