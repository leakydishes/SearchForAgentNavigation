from pygame import Surface, SurfaceType
from pygame_gui import UIManager

from src.maze import Maze


class Context:
    """
    Execution context of the app
    """
    # Stores the currently active screen
    active_screen: object

    # All screens in the app
    maze_screen: object
    select_screen: object

    # Drawing surface for pygame
    surface: Surface

    # UI manager for handling UI elements
    manager: UIManager

    # Time delta from last frame
    time_delta: float

    # Loaded mazes
    mazes: dict[str, Maze]

    # Currently active maze, selected on select_screen
    active_maze: Maze

    # App will exit loop if quit is set to True
    quit: bool

    def __init__(self, surface: Surface, manager: UIManager, select_screen, maze_screen, mazes: dict[str, Maze]):
        """
        Initialises a new Context class instance that will be passed to each screen
        """
        self.surface = surface
        self.manager = manager
        self.mazes = mazes
        self.quit = False
        self.select_screen = select_screen
        self.maze_screen = maze_screen
        self.time_delta = 0
        self.active_maze = None

    def set_screen_to(self, screen):
        """
        Changes the active_screen to the supplied screen instance, then calls the initialise method on that screen
        """
        self.active_screen = screen
        self.active_screen.initialise(self)
