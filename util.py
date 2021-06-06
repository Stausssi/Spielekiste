"""
    file: util.py
    description: Contains the main classes of the application. Main classes meaning the Game superclass,
    GameContainer to display the main menu and Image to display an image on the screen

    author: Niklas Drössler, Simon Stauss
    date: 25.03.2021
    licence: free
"""

import os
import re

import pygame
from pandas import DataFrame
from loguru import logger

from pygame_textinput import TextInput
import pygame_menu

from config import Configuration, Colors


class Game:
    def __init__(self, game="", windowSize=Configuration.windowSize):
        """
        Superclass for every component in this application.

        Implements predefined behaviour and supplies the children with method-prototypes, which will be slightly
        modified by the children.

        Tests:
            - Alle Variablen korrekt angelegt und Fehler abgefangen
            - Nichts wichtiges überschrieben durch Kinderklassen

        Args:
            game (str): The name of the game
            windowSize (tuple[int, int]): The size of the pygame window
        """

        self.game = game
        self.isRunning = True
        self.isGameOver = False
        self.isPaused = False
        self.showGameOver = False
        self.hasScore = True
        self.score = 0
        self.scoreX, self.scoreY = (windowSize[0] // 2, 100)
        try:
            self.scores = Configuration.SCORE_DATA[game]
        except KeyError:
            self.scores = None
            # no logging, because the logging happens in Configuration.SCORE_DATA

        self.windowSize = windowSize
        self.events = None

        self.clock = pygame.time.Clock()

        # Pygame specific stuff
        pygame.init()

        # Display
        title = Configuration.windowTitle
        if self.game != "":
            title += f" | {self.game}"
        pygame.display.set_caption(title)

        if Configuration.isFullscreen:
            self.surface = pygame.display.set_mode(size=self.windowSize, flags=pygame.FULLSCREEN)
        else:
            self.surface = pygame.display.set_mode(size=self.windowSize)

        self.backgroundImage = None

        # Music
        pygame.mixer.init()
        self.backgroundMusic = None
        self.sounds = {}

        # Font
        pygame.font.init()
        try:
            self.defaultFont = pygame.font.SysFont("arial", 25)
        except():
            logger.critical("Default font could not be loaded")

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

        self.score = 0
        self.gameOverText = ""  # has to be set by the specific game
        self.endFont = pygame.font.SysFont("arial", 50)
        self.nameSubmit = False
        self.nameInputX, self.nameInputY = (Configuration.windowWidth // 2, Configuration.windowHeight // 2)
        try:
            self.nameBackground = Image(
                x=0,
                y=0,
                size=Configuration.windowSize,
                image="nameInput.png",
                hasColorkey=False
            )
        except FileNotFoundError:
            logger.critical("File: nameInput.png could not be loaded")

    def run(self) -> None:
        """
        Main loop of the application.
        Calls methods self.updateEvents(), self.updateGameState() and self.updateScreen() while self.isRunning is True.
        If self.isRunning is False, self.gameOver() will be called to ask the user for their name.
        
        !DO NOT OVERWRITE THIS METHOD!

        Tests:
            - Keine Möglichkeit Fehler zu produzieren
            - Programmablauf immer gleich und keine Möglichkeit frühzeitig zu verlasen

        Returns: None
        """

        # Log the start of the gameloop
        if self.game:
            game = self.game
        else:
            game = "Menu"
        logger.info("Start the gameloop of {}", game)

        # Play background music
        if self.backgroundMusic is not None:
            try:
                pygame.mixer.music.load(self.backgroundMusic)
            except FileNotFoundError:
                logger.critical("Background music could not be loaded")
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

        if self.isGameOver and (self.hasScore or self.showGameOver):
            self.gameOver()

    def updateEvents(self, nameInput=False) -> None:
        """
        This functions gets every pygame event and handles quit and pause.
        Unhandled Events are passed down to self.handleEvent() to be handled by children classes.

        !DO NOT OVERWRITE THIS METHOD!

        Tests:
            - Nur Events abfangen, die in Kinderklassen nicht benötigt werden
            - Kein Event überspringen / Nicht beachten -> Logging überprüfen

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

                # Toggle Fullscreen on F11
                elif event.key == pygame.K_F11:
                    self.toggleFullscreen()
                    eventHandled = True

                # Enter name on Enter
                elif event.key == pygame.K_RETURN and nameInput:
                    self.nameSubmit = True
                    eventHandled = True

            if not eventHandled:
                # Further event handling
                self.handleEvent(event)

    def handleEvent(self, event) -> None:
        """
        This method specifies game-specific behavior on pygame events.
        Overwrite this method in your class!

        Tests:
            - Korrektes Logging des Events
            - Rest siehe Testbeschreibung der Kinderklassen

        Args:
            event (pygame.event.Event): The to be handled event

        Returns: None
        """

        pass

    def updateGameState(self) -> None:
        """
        This method handles all game-specific state changes. It is to be implemented by the children classes.

        Tests:
            - Siehe Testbeschreibungen in den Kinderklassen

        Returns: None
        """

        pass

    def updateScreen(self) -> None:
        """
        This method updates the pygame window.
        It also handles pause behaviour.

        Tests:
            - Korrektes Verhalten des Pausenmenüs
            - Score wird fehlerlos angezeigt

        Returns: None
        """

        if self.isPaused:
            self.pauseBehaviour()

        if self.hasScore:
            # Print score at a given position
            self.drawTextOnSurface(f"Score: {self.score}", (self.scoreX, self.scoreY))

        pygame.display.update()

    def drawTextOnSurface(self, text, position, color=Colors.White, font=None, surface=None, center=True) -> None:
        """
        This method draws a given text on a surface.

        Tests:
            - Korrekte Defaultparameter
            - Richtige Darstellung des Textes
            - Keine Fehler durch falsche Variablen

        Args:
            text (String): The text to draw
            position ((int, int)): The position of the top left corner of the text
            color (tuple[int, int, int]): The color of the drawn text
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

    def drawImageOnSurface(self, image, position=None, surface=None) -> None:
        """
        This method draws a given image on a surface.

        Tests:
            - Korrekte Defaultparameter
            - Korrekte Darstellung des Bildes an der richtigen Stelle

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

    def drawMenu(self, menu=None) -> None:
        """
        This method draws a given menu to the screen. Default menu is the pause menu

        Tests:
            - Darstellung des richtigen Menüs
            - Keine Fehler beim Zeichnen und Updaten des Menüs

        Args:
            menu (pygame_menu.Menu): The menu to draw

        Returns: None
        """

        if not menu:
            menu = self.pauseMenu

        # Pass events to the menu und draw it onto the surface if enabled
        if menu.is_enabled():
            menu.update(self.events)
            menu.draw(self.surface)

    def togglePause(self) -> None:
        """
        This method toggles self.isPaused and is called once the user pressed the ESC-key.

        Tests:
            - Toggle der Variable immer fehlerlos
            - Immer korrekt aufgerufen

        Returns: None
        """

        self.isPaused = not self.isPaused
        if not self.isGameOver:
            if self.isPaused:
                logger.info("The game was paused")
            else:
                logger.info("The game was unpaused")

    def toggleFullscreen(self, *args) -> None:
        """
        This method toggles pygame fullscreen.

        Tests:
            - Toggle der Variable immer fehlerlos
            - Wird Fullscreen unterstützt:
            https://www.pygame.org/docs/ref/display.html#pygame.display.toggle_fullscreen

        Args:
            args: Optional. Only needed to satisfy pygame-menu requirements.

        Returns: None
        """

        Configuration.isFullscreen = not Configuration.isFullscreen

        if Configuration.isFullscreen:
            logger.info("Fullscreen is enabled")
        else:
            logger.info("Fullscreen is disabled")

        pygame.display.toggle_fullscreen()

    def playSound(self, sound, volume=1.0) -> None:
        """
        This method plays a sound.

        Tests:
            - Korrekte Wiedergabe des Sounds
            - Abfangen von fehlerhaften Sounds. (Keine pygame.mixer.Sound Objekte)

        Args:
            sound (str): The name of the sound
            volume (float): The volume of the sound. Ranges from 0.0 to 1.0, where 1.0 is the loudest

        Returns: None
        """

        sound = self.sounds[sound]

        if sound:
            sound.set_volume(volume)
            sound.play()

    def gameOver(self) -> None:
        """
        This method is called once the game finished.
        It asks the user to input a name and saves their score afterwards.

        Tests:
            - Korrektes Anlegen des pandas DataFrame
            - Korrektes Abfangen von Fehlern

        Returns: None
        """

        logger.info("Gameover in game: {game}", game=self.game)

        # Ask the user for their name to save the score
        name = self.getUserName()

        # Create the values to be saved to the DataFrame
        values = {
            Configuration.PLAYER_HEADER: name
        }

        try:
            dataHeader = Configuration.DATA_HEADERS[self.game]
        except KeyError:
            dataHeader = None
            logger.critical("Game score could not be saved")

        if dataHeader:
            for header in dataHeader:
                if header != Configuration.PLAYER_HEADER:
                    # Add 1 win or the score
                    value = 1
                    if header == Configuration.SCORE_HEADER:
                        value = self.score

                    values.update({
                        header: [value]
                    })

            self.saveScore(DataFrame(data=values))

        self.gameOverText = ""  # clear gameover text

    def getUserName(self) -> str:
        """
        This method shows an input dialog for the user to write their name.
        The name will be used in the scoreboard.

        Tests:
            - Name wird vom TextInput korrekt zurückgegeben
            - Darstellung mit richtigem Hintergrund

        Returns: The name of the user as a string
        """

        nameInput = TextInput(text_color=Colors.White, font_family="Arial", font_size=50)

        while not self.nameSubmit:
            self.updateEvents(True)

            nameInput.update(self.events)

            self.drawImageOnSurface(self.nameBackground)
            nameSurface = nameInput.get_surface()
            self.surface.blit(nameSurface, (self.nameInputX + 10, self.nameInputY - nameSurface.get_height() // 2))

            # Draw the game over notification
            self.drawTextOnSurface(
                self.gameOverText,
                (Configuration.windowWidth / 2, Configuration.windowHeight * 5 / 12),
                Colors.White,
                font=self.endFont
            )

            # Notify user of validity of their name
            text = "Your name is valid! Press Enter to submit!"
            color = Colors.Green
            if not self.validateName(nameInput.get_text()):
                self.nameSubmit = False
                text = "Your name is not valid!"
                color = Colors.Red

            self.drawTextOnSurface(
                text,
                (Configuration.windowWidth / 2, Configuration.windowHeight * 55 / 100),
                color
            )

            pygame.display.update()

            self.clock.tick(Configuration.FRAMERATE)

        logger.info("User has entered his name: {}", nameInput.get_text())

        return nameInput.get_text()

    @staticmethod
    def validateName(name) -> bool:
        """
        This method returns whether the given string fulfills the requirements of a name. It has to have at least a
        single character and can only contain numbers and letters. In total the name has to contain less than 25
        characters.

        Args:
            name (str): The name to validate

        Returns: Whether the string meets the requirements
        """

        # Regex Validation from: https://www.geeksforgeeks.org/how-to-check-a-valid-regex-string-using-python/
        pattern = re.compile(r"[A-Za-z0-9.]+")
        return bool(re.fullmatch(pattern, name)) and len(name) <= 25

    def saveScore(self, values) -> None:
        """
        This method saves the score of the user in a game

        Tests:
            - Übergebener Parameter ist ein DataFrame
            - Richtiges Summieren der Wins
            - Korrekte Sortierung des DataFrames
            - Schreiben der CSV-Datei korrekt

        Args:
            values (DataFrame): The data to be appended to the dataframe. It contains the player name and other
                value(s)

        Returns: None
        """

        if self.scores is not None:
            self.scores = self.scores.append(values, ignore_index=True)

            # Sum wins grouped by Player
            if Configuration.WIN_HEADER in self.scores.columns:
                self.scores = self.scores. \
                    groupby(Configuration.PLAYER_HEADER, as_index=False)[Configuration.WIN_HEADER]. \
                    sum()

            # Sort the DataFrame
            # Sort after score by default
            sortType = Configuration.SCORE_HEADER

            if sortType not in self.scores.columns:
                # Sort after wins
                sortType = Configuration.WIN_HEADER

            # Sort the data in a descending order
            self.scores.sort_values(
                by=[sortType],
                ascending=False,
                inplace=True
            )

            # Save the csv file without the index
            try:
                self.scores.to_csv(f"scores/{self.game}.csv", index=False)

                # logging
                try:
                    score = values["Score"][0]
                except KeyError:
                    score = values["Wins"][0]
                logger.info("Score {} has been added for {} in game {}", score, values["Player"][0], self.game)
            except():
                logger.critical("Score could not be saved")

            # Update global scores
            Configuration.SCORE_DATA[self.game] = self.scores
            Configuration.UPDATE_GAME_SCORE = self.game

    def setGameOverText(self, text) -> None:
        """
        This function generates a gameover text when a player has won or lost that will be displayed on the endscreen.
        It internally sets the attribute gameOverText.

        Tests:
            - Übergebener Text ist ein valider String
            - Variable wird korrekt gesetzt

        Args:
            text (str): the text that will be displayed on the endscreen

        Returns: None
        """

        logger.info("The gameover text for {game} has been set to: {text}", game=self.game, text=text)

        self.gameOverText = text

    def quit(self) -> None:
        """
        This method is called once the player quits the game.
        It also stops the background music.

        Tests:
            - Musik wird ohne Probleme gestoppt
            - Variable wird korrekt gesetzt

        Returns: None
        """

        if not self.isGameOver:
            if self.game != "":
                logger.info("{} has been quit", self.game)
            else:
                logger.info("Menu has been quit")

        pygame.mixer.music.stop()

        self.isRunning = False


class GameContainer(Game):
    def __init__(self):
        """
        Children of class Game.

        This class displays the main menu adding the ability to start games and adjust settings.

        Tests:
            - Korrektes Anlegen der Menüs
            - Bedienung der Menüs ohne Fehler und Bugs möglich
        """

        super().__init__()

        # Disable the score display
        self.hasScore = False

        # Create menus
        # https://pygame-menu.readthedocs.io/en/4.0.7/index.html
        self.mainMenu = pygame_menu.Menu(
            title="Herzlich Willkommen in der Spielekiste!",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK  # title_close_button=False
        )
        self.playMenu = pygame_menu.Menu(
            title="Choose Game",
            width=self.windowSize[0],
            height=self.windowSize[1],
            theme=pygame_menu.themes.THEME_DARK
        )
        self.optionsMenu = pygame_menu.Menu(
            title="Options",
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
        self.pongMenu = pygame_menu.Menu(
            title="Number of players",
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
        self.playMenu.add.button(f"Play {Configuration.GAME_SNAKE}", self.startSnake)
        self.playMenu.add.button(f"Play {Configuration.GAME_TTT}", self.startTTT)
        self.playMenu.add.button(f"Play {Configuration.GAME_PONG}", self.pongMenu)
        self.playMenu.add.button("Back", pygame_menu.events.BACK)

        # Add buttons to options menu
        toggle = self.optionsMenu.add.toggle_switch(
            title="Fullscreen",
            default=Configuration.isFullscreen,
            onchange=self.toggleFullscreen,
            toggleswitch_id="fullscreen"
        )
        toggle.add_draw_callback(self.updateFullscreenToggle)
        self.optionsMenu.add.button("Back", pygame_menu.events.BACK)

        # Add buttons to highscore menu
        self.highscoreMenu.add.dropselect(
            title="Game",
            items=[
                (Configuration.GAME_SNAKE, Configuration.GAME_SNAKE),
                (Configuration.GAME_TTT, Configuration.GAME_TTT),
                (Configuration.GAME_PONG, Configuration.GAME_PONG),
            ],
            placeholder="Select a game",
            onchange=self.updateScoreTable,
            margin=(0, 20),
            dropselect_id="score_select"
        )
        self.highscoreMenu.add.button("Back", pygame_menu.events.BACK)

        # Add buttons to pong menu
        self.pongMenu.add.button("One player", self.startPongComputer)
        self.pongMenu.add.button("Two players", self.startPongMultiplayer)
        self.pongMenu.add.button("Back", pygame_menu.events.BACK)

        # Quit the game on esc
        self.pauseBehaviour = self.quit

        # Run the container
        self.run()

    def updateScreen(self) -> None:
        """
        This method draws the main menu of the application.

        Tests:
            - Darstellung des richtigen Menüs
            - Variablen alle korrekt initialisiert

        Returns: None
        """

        # Draw the main menu
        self.drawMenu(self.mainMenu)

        super().updateScreen()

    @staticmethod
    def startSnake() -> None:
        """
        This function starts the Snake-Game

        Tests:
            - Spiel wird korrekt gestartet
            - Programmfluss wird korrekt weitergeführt

        Returns: None
        """

        logger.info("Start snake game")

        from games.Snake import Snake
        Snake()

    @staticmethod
    def startTTT() -> None:
        """
        This function starts the TicTacToe-Game

        Tests:
            - Spiel wird korrekt gestartet
            - Programmfluss wird korrekt weitergeführt

        Returns: None
        """

        logger.info("Start TikTakToe game")

        from games.TicTacToe import TicTacToe
        TicTacToe()

    @staticmethod
    def startPongMultiplayer() -> None:
        """
        This functions starts the Pong-Game with two players

        Tests:
            - Spiel wird korrekt gestartet
            - Spieler spielt nicht gegen einen Computer

        Returns: None
        """

        logger.info("Start Pong multiplayer")

        from games.Pong import Pong
        Pong(False)

    @staticmethod
    def startPongComputer() -> None:
        """
        This functions starts the Pong-Game with a computer player

        Tests:
            - Spiel wird korrekt gestartet
            - Spieler spielt gegen einen Computer

        Returns: None
        """

        logger.info("Start Pong with computer player")

        from games.Pong import Pong
        Pong(True)

    def toggleFullscreen(self, *args) -> None:
        """
        This method toggles fullscreen and also updates the fullscreen switch in the options menu

        Tests:
            - Spielfenster wechselt korrekt in den Fullscreen oder zurück in den Fenstermodus
            - Methodenaufruf wird immer korrekt ausgeführt

        Args:
            args: Optional. Only needed to satisfy pygame-menu requirements.

        Returns: None
        """

        super().toggleFullscreen(args)

        # Update the value of the menu widget and force render the menu
        self.updateFullscreenToggle(self.optionsMenu.get_widget("fullscreen"), self.optionsMenu)

    def updateFullscreenToggle(self, widget, menu) -> None:
        """
        This method updates the state of the fullscreen toggle switch depending on the value in the Configuration.
        It is also registered as a draw callback for the toggle switch

        Tests:
            - Configuration.isFullscreen spiegelt immer den aktuellen Stand des Fensters wieder
            - Status des Toggle Switch wird korrekt aktualisiert

        Args:
            widget (pygame_menu.widgets.core.widget.Widget): The widget that was drawn. In this case the toggle switch
            menu (pygame_menu.menu.Menu): The menu the widget is in

        Returns: None
        """

        if widget:
            widget.set_value(Configuration.isFullscreen)
            self.mainMenu.render()

    def updateScoreTable(self, selectValue, *args) -> None:
        """
        This method updates the table displaying the scores in the highscore menu.

        Tests:
            - Übergebener Parameter enthält das ausgewählte Spiel
            - Korrekter DataFrame wird ausgewählt
            - Tabelle spiegelt genau den DataFrame wieder

        Args:
            selectValue (tuple[tuple[str, str], int]): The value of the dropdown select
            args: pygame_menu requirement. Will not be used in this method.

        Returns: None
        """

        # Reset the flag in the config
        Configuration.UPDATE_GAME_SCORE = ""

        # Get the selected game
        game = self.getGameFromSelectValue(selectValue)

        # https://pygame-menu.readthedocs.io/en/4.0.7/_source/widgets_table.html
        # Remove table from highscore menu if it exists
        if self.highscoreMenu.get_widget("scores"):
            self.highscoreMenu.remove_widget("scores")

        # Check if data exists
        scores = Configuration.SCORE_DATA[game]
        if scores is not None:
            if not scores.empty:
                if self.highscoreMenu.get_widget("no_scores"):
                    self.highscoreMenu.remove_widget("no_scores")

                # Create a new table and move it to the correct index
                table = self.highscoreMenu.add.table(
                    "scores",
                    font_color=Colors.Black,
                    margin=(0, 20)
                )
                table.default_cell_padding = 10
                table.default_row_background_color = Colors.White
                self.highscoreMenu.move_widget_index(table, 1)

                # Add header row
                table.add_row(
                    cells=Configuration.DATA_HEADERS[game]
                )

                # Add a row for the top 10
                for row in scores.head(10).itertuples(index=False):
                    table.add_row(row)

                # Create a draw callback to be fired each time the table is drawn.
                # This is used to refresh the table
                table.add_draw_callback(self.refreshScoreTable)

                logger.info("Highscore table was updated for {game}", game=game)
            else:
                # Display a label telling the user no scores are available just yet
                label = self.highscoreMenu.add.label(
                    title=f"No scores available for {game} yet! Make sure to be the first one!",
                    label_id="no_scores",
                    margin=(0, 20)
                )
                self.highscoreMenu.move_widget_index(label, 1)

                logger.info("Highscore table was updated for {game}, but was empty ", game=game)

    def refreshScoreTable(self, widget, menu) -> None:
        """
        This method is a draw callback from the highscore table meaning it is called every time the score table is
        drawn. This is needed to update the table after a new score was set and the widget wasn't reloaded.

        Tests:
            - Methode wird immer korrekt aufgerufen -> Callback funktioniert
            - Refresh wird nur unter den richtigen Bedingungen getriggert

        Args:
            widget (pygame_menu.widgets.core.widget.Widget): The widget that was drawn. In this case it is the table
            menu (pygame_menu.menu.Menu): The menu the widget is in

        Returns: None
        """

        # Get the currently selected game
        select = menu.get_widget("score_select")
        if select:
            # Update the table if the flag is the same as the selected game
            selectValue = select.get_value()
            game = self.getGameFromSelectValue(selectValue)
            if game == Configuration.UPDATE_GAME_SCORE:
                self.updateScoreTable(selectValue)

    @staticmethod
    def getGameFromSelectValue(selectValue) -> str:
        """
        This method returns the game of a given dropdown select value.

        Tests:
            - Übergebener Parameter enthält das Spiel
            - Spiel wird korrekt zurückgegeben

        Args:
            selectValue (tuple[tuple[str, str], int]): The value of the dropdown select

        Returns: The selected game
        """

        return selectValue[0][0]

    def quit(self) -> None:
        """
        This method quits the application.

        Tests:
            - Applikation wird ohne Fehler beendet
            - Rückgabecode wird korrekt übergeben

        Returns: None
        """

        super().quit()

        pygame.quit()
        exit(0)


class Image(pygame.sprite.Sprite):
    def __init__(self, x, y, size, image, pathToImage="images/", colorkey=(0, 0, 0), hasColorkey=True):
        """
        This class represents a image in a game. This can be a texture, character, etc.
        It's parent is pygame.sprite.Sprite

        Tests:
            - Bild wird korrekt geladen
            - Variablen werden korrekt gesetzt

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
        try:
            self.image = pygame.transform.smoothscale(pygame.image.load(os.path.join(pathToImage, image)).convert(), size)
        except FileNotFoundError:
            logger.info("Image {} could not be loaded", image)

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

        Tests:
            - Variable wird korrekt zurückgegeben
            - Variable spiegelt genau den Wert der x-Koordinate wieder

        Returns: x-coordinate of the image
        """

        return self.rect.x

    def setX(self, x) -> None:
        """
        This method moves the image to the given value on the x-axis

        Tests:
            - Variable wird korrekt gesetzt
            - Übergebener Parameter ist eine Ganzzahl

        Args:
            x (int): The x-coordinate to move the image to

        Returns: None
        """

        self.rect.x = x

    def getY(self) -> int:
        """
        This method returns the y-axis value of the image

        Tests:
            - Variable wird korrekt zurückgegeben
            - Variable spiegelt genau den Wert der x-Koordinate wieder

        Returns: y-coordinate of the image
        """

        return self.rect.y

    def setY(self, y) -> None:
        """
        This method moves the image to the given value on the y-axis

        Tests:
            - Variable wird korrekt gesetzt
            - Übergebener Parameter ist eine Ganzzahl

        Args:
            y (int): The y-coordinate to move the image to

        Returns: None
        """

        self.rect.y = y

    def getRect(self) -> pygame.rect.Rect:
        """
        This method returns the rect of the image.

        Tests:
            - Variable wird korrekt zurückgegeben
            - Variable spiegelt genau den Wert der Bildumrisse wieder

        Returns: The rect of the image
        """

        return self.rect

    def setRect(self, rect) -> None:
        """
        This method updates the rect of the image.

        Tests:
            - Variable wird korrekt gesetzt
            - Übergebener Parameter ist ein gültiges Rechteck

        Args:
            rect (pygame.rect.Rect): The new rect object

        Returns: None
        """

        self.rect = pygame.rect.Rect(rect)

    def getImage(self) -> pygame.surface.Surface:
        """
        This method returns the image surface of the image.

        Tests:
            - Variable wird korrekt zurückgegeben
            - Variable enthält das Bild der Klasse

        Returns: The image surface of the image
        """

        return self.image

    def setImage(self, image) -> None:
        """
        This method updates the image of the image.

        Tests:
            - Variable wird korrekt gesetzt
            - Übergebener Parameter ist ein gültiges Bild

        Args:
            image (pygame.surface.Surface): The new image surface

        Returns: None
        """

        self.image = image
