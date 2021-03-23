import pygame
import pygame_menu


class Game:
    def __init__(self, title="Niklas und Simons Spielekiste"):
        self.title = title

        self.isRunning = True
        self.windowSize = (1920, 1080)
        self.events = None
        self.clock = pygame.time.Clock()

    def run(self):
        while self.isRunning:
            self.updateEvents()

            self.updateGamestate()

            self.updateScreen()

            self.clock.tick(60)

    def updateEvents(self):
        self.events = pygame.event.get()

        for event in self.events:
            if event.type == pygame.QUIT:
                exit(0)
            else:
                # further event handling
                self.handleEvent(event)

    def handleEvent(self, event):
        print("Unhandled event:", event)

    def updateGamestate(self):
        pass

    def updateScreen(self):
        pygame.display.update()


class GameContainer(Game):
    def __init__(self):
        super().__init__()

        # Pygame specific stuff
        pygame.init()
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.set_mode(size=self.windowSize)

        # Create the Menu
        # https://pygame-menu.readthedocs.io/en/4.0.1/index.html
        self.mainMenu = pygame_menu.Menu(
            title="Herzlich Willkommen in der Spielekiste!",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK #title_close_button=False
        )
        self.mainMenu.add.button("Play Snake", self.startSnake)
        self.mainMenu.add.button("Play Tic Tac Toe", self.startTTT)
        self.mainMenu.add.button("Options", self.openOptionsMenu)
        self.mainMenu.add.button("Quit", self.quit)

        self.run()

    def updateScreen(self):
        if self.mainMenu.is_enabled():
            self.mainMenu.update(self.events)
            self.mainMenu.draw(self.surface)

        super().updateScreen()

    def startSnake(self):
        from games import Snake
        Snake()

    def startTTT(self):
        from games import TicTacToe
        TicTacToe()

    def openOptionsMenu(self):
        print("Options selected")

    def quit(self):
        print("Game is gone")
