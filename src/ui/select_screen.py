import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UISelectionList
from src.context import Context
from src.ui.maze_drawer import MazeDrawer


class SelectScreen:
    # UI elements - storing only those that need referencing later
    maze_label: UILabel
    maze_selection_list: UISelectionList
    load_button: UIButton
    title_label: UILabel

    # List of the file names of loaded mazes
    maze_list: list[str]

    # Class for drawing the currently selected maze
    drawer: MazeDrawer

    def __init__(self):
        # Called when this screen instance is created when the app is loading
        pass

    def initialise(self, ctx: Context):
        # Called when this screen is switched to
        # Store the file names of the mazes
        self.maze_list = list(ctx.mazes.keys())

        # Start with the first maze in the list selected
        ctx.active_maze = ctx.mazes[self.maze_list[0]]
        # Create an instance of MazeDrawer to render the selected maze
        self.drawer = MazeDrawer(ctx.active_maze)

        # Title Label of UI for authors
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 70), (200, 40)),
                                    text="Agent Search 2023", manager=ctx.manager)
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 103), (200, 40)),
                                    text="Created by:", manager=ctx.manager)
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 123), (200, 40)),
                                    text="Tim Butler & Te' Claire", manager=ctx.manager)

        # Label of UI for Maze
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 183), (200, 40)),
                                    text="MAZES", manager=ctx.manager)

        # Selection of mazes from drop down/ scroll -> populate selection list using stored list (maze_names)
        self.maze_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((570, 215), (200, 288)),
                                                                       item_list=self.maze_list,
                                                                       default_selection=self.maze_list[0],
                                                                       manager=ctx.manager)

        # Load Maze Button
        self.load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((680, 540), (90, 40)), text="LOAD",
                                                        manager=ctx.manager)

        # Label of UI for button
        self.title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 8), (500, 40)),
                                                       text="Press Load to Select Maze", manager=ctx.manager)

    def run(self, ctx: Context):

        # Called every frame when the screen is active
        for event in pygame.event.get():
            # Process Manager UI Events
            ctx.manager.process_events(event)
            # Process other events
            if event.type == pygame.QUIT:
                ctx.quit = True

            # Load new maze based on maze_selection_list.get_single_selection()
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.load_button:
                    # Clears UI elements and switches to the maze screen when the user clicks Load
                    ctx.manager.clear_and_reset()
                    ctx.set_screen_to(ctx.maze_screen)

            # UI selection of maze type displayed to screen
            if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.maze_selection_list:
                    # Look up maze from selection
                    ctx.active_maze = ctx.mazes[self.maze_selection_list.get_single_selection()]
                    # Create new drawer
                    self.drawer = MazeDrawer(ctx.active_maze)

        # Draw Maze to screen by calling draw_maze()
        self.drawer.draw_maze(ctx)
