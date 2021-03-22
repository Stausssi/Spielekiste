import pygame


class Game:
    def __init__(self):
        self.isRunning = True

        self.events = None
        self.clock = pygame.time.Clock()

    def run(self):
        while self.isRunning:
            self.events = pygame.event.get()

            for event in self.events:
                if event.type == pygame.QUIT:
                    exit(0)

                print(event)

            pygame.display.update()
            self.clock.tick(60)


class GameContainer(Game):
    def __init__(self):
        super().__init__()

        self.test = False
        self.games = []

        # Pygame specific stuff
        pygame.init()
        pygame.display.set_caption("Niklas und Simons Spielekiste")
        pygame.display.set_mode((1920, 1080))
        self.run()

    def run(self):
        super().run()

        print("Hello there from the container")
