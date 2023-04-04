import pygame
import pygame_gui

from src import maze_loader
from src.constants import *
from src.context import Context
from src.ui.maze_screen import MazeScreen
from src.ui.select_screen import SelectScreen


def run():
    pygame.init()

    # Create the window and set the size
    surface = pygame.display.set_mode(WINDOW_SIZE)

    # Set window title
    pygame.display.set_caption("SIT215 Assignment 1 - Agent Search")

    # Used to manage FPS
    clock = pygame.time.Clock()

    # Instances of the screens
    select_screen = SelectScreen()
    maze_screen = MazeScreen()

    # Load the maze text files to a list of Maze class instances
    mazes = maze_loader.load()

    # Create an instance of UIManager to handle UI elements
    manager = pygame_gui.UIManager(WINDOW_SIZE)

    # Initialises the app context, for sharing data/instances between screens
    ctx = Context(surface, manager, select_screen, maze_screen, mazes)

    # Sets the starting screen
    ctx.set_screen_to(ctx.select_screen)

    # Main loop
    while not ctx.quit:
        # Limit FPS, and calculate time delta between frames
        ctx.time_delta = clock.tick(300) / 1000.0

        # Set the background colour
        surface.fill(BACKGROUND_COLOUR)

        # Calls the run() method on the currently active screen
        ctx.active_screen.run(ctx)

        # Process UI elements
        manager.update(ctx.time_delta)

        # Draw the UI
        manager.draw_ui(surface)

        # Update window display with what's been drawn
        pygame.display.flip()

    pygame.quit()
