Video: https://youtu.be/W4bHu_3r9Is

Setup:
install pygame and multiprocessing with pip
run main.py

Game overview:
Title: A Window

Summary: A puzzle game where you direct yourself around mazes and obstacle courses, and you solve the courses by moving two windows around your screen. The player can jump from one window to another if they are next to each other. 

Gameplay loop: There will be multiple levels, and you can select each level from a menu screen. Once you are in the level, you must get to the goal to beat the level. Getting to the goal will differ from level to level.

Gameplay Mechanics:
WASD to move, you win each level by getting to the goal

OS Concept:
Process creation (core game mechanic) (line 179 of main.py)
Inter process communication (core game mechanic) (line 174 of main.py)
File management (save files to be implemented)
Synchronization (to be implemented)
Threading (core game mechanic) (game input and game logic)
