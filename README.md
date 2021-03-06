# Spielekiste
Game Container to support multiple arcade games 

## Beschreibung
Spielekiste mit den Spielen:
- TicTacToe 
- Pong
- Snake 

Pong und TicTacToe können lokal gegen einen echten Menschen gespielt werden. Des Weiteren wurde für Pong ein statischer
Computerspieler implementiert, gegen den gespielt werden kann.

Die Spiele können über ein Hauptmenü gestartet werden, welches parallel zu den Spielen auch noch deren Highscores
beinhaltet. Zusätzlich dazu kann man noch eine Einstellung treffen, die den Vollbildmodus (de-)aktiviert.

## Contributors
- Niklas Drössler
- Simon Stauss

## How to play
1. Open the application folder.
2. Make sure every required package in `requirements.txt` is installed
3. Run `main.py`, i. e. with `python3 main.py`.
4. Now the main menu should open, and you should be able to choose from a list of supported games.
5. Quit the game by selecting the quit option in the main menu or by closing the window or by pressing ESC.

## Criteria
Pasted from a lesson:

Kernkriterien:
- (20%) - alle Funktionen und Module sowie Klassen müssen Docstrings nach z.B. Google (Docstrings pep8) enthalten
- (10%) - alle Funktionen und Klassen müssen jeweils 2 Testbeschreibungen enthalten

Sitekriterien:
- (10%) - Eigenleistung: geeignetes Logverfahren suchen und anwenden
  - Umgesetzt mit Loguru (https://github.com/Delgan/loguru)
- (20%) - Codequalität und Stil
  - Verwendung Numpy
  - Verwendung Pandas Dataframe
- (20%) - Funktionalität (requirement Informationen --- welche Module, Frameworks, Versionen, OS ...)

- (20%) - Eigenaufwand/ Intuitivität der UI
  - eigene Erstellung vieler Gamegrafiken
  - eigene Erstellung der Endscreens

weitere Kriterien:
- wir wollen am Ende kein kundenfähiges System
- Programm Intuitivität für den Nutzer möglichst einfach
- Besondere Bemühungen und Aufwand, Elemente (Sound, Grafikdateien, Gameplay, ...)
- pi mal Daumen 48 Stunden zur Orientierung

Bonuspunkte: -- Copy+Paste vs. Eigenaufwand
