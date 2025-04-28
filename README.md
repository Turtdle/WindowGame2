Video: https://youtu.be/W4bHu_3r9Is
```
Setup:
install pygame
run main.py
```
# Game overview:
## Title: Alt-Tab Adventures

Summary: A puzzle game where you direct yourself around mazes and obstacle courses, and you solve the courses by moving two windows around your screen. The player can jump from one window to another if they are next to each other. 

Gameplay loop:
    Select a level from the level select. Complete the level. Select a new level. After unique 3 levels are completed, you win

Gameplay Mechanics:
WASD to move, space to jump (you can jump in level 2 and 3), you win each level by getting to the goal



## OS Concepts:



Process creation: main.py
We use two processes for the main game mechanic

Inter process communication: main.py, window.py
Inter process communication is used throughout the entire project. Just open window.py
Explicit example:
    Passing the player to the other window

File management: level_data.py
We manage a save file to keep track of what levels we have completed

Synchronization: window.py
Completing a level:
    Teleporting player back to window 1
Moving levels:
    Telling both windows to draw the level to be moved to


Threading: main.py
We use two threads for each of the processes for the main game mechanic
