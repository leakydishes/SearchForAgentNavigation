import time
from typing import Iterator
import pygame
from enum import Enum

import pygame_gui
from pygame.math import clamp
from pygame_gui.elements import UIButton, UILabel, UISelectionList, UIHorizontalSlider

from src.constants import *
from src.context import Context
from src.int2 import int2
from src.search import dfs, astar, dijkstra, bfs
from src.searcher import Searcher
from src.ui.maze_drawer import MazeDrawer


class MazeScreenState(Enum):
    IDLE = 1
    SEARCHING = 2
    ANIMATING_MOVEMENT = 3


class MazeScreen:
    # Current state of the screen
    state: MazeScreenState

    # Searcher to find paths
    searcher: Searcher

    # Class to handle drawing the maze and search progress
    maze_drawer: MazeDrawer

    # Movement animation iterator
    movement_iter: Iterator

    # Time since last update, used to control algorithm speed
    time_since_last_update: float

    # Agents position for animating the agent on the path
    agent_position: tuple[float, float]

    # UI elements - storing only those that need referencing later
    start_button: UIButton
    back_button: UIButton
    benchmark_all_button: UIButton
    title_label: UILabel
    algo_selection_list: UISelectionList
    speed_slider: UIHorizontalSlider
    algorithm_label: UILabel
    nodes_explored_label: UILabel
    path_length_label: UILabel
    current_depth_label: UILabel
    current_cost_label: UILabel
    path_cost_label: UILabel

    def __init__(self):
        # Called when this screen instance is created when the app is loading
        pass

    def initialise(self, ctx: Context):
        # Called when this screen is switched to
        self.state = MazeScreenState.IDLE

        # Initialise searcher and UI
        self.searcher = Searcher(ctx.active_maze)
        self.searcher.set_algorithm(dfs.run)
        self.maze_drawer = MazeDrawer(ctx.active_maze)
        self.maze_drawer.set_searcher(self.searcher)
        self.agent_position = None
        self.time_since_last_update = 0

        self.title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 8), (500, 40)),
                                                       text="Press Start", manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 5), (200, 40)),
                                    text="ALGORITHM:", manager=ctx.manager)

        self.algorithm_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 25), (200, 40)),
                                                           text="Depth-First Search", manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 55), (200, 40)),
                                    text="CURRENT DEPTH:", manager=ctx.manager)

        self.current_depth_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 75), (200, 40)),
                                                               text="0", manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 105), (200, 40)),
                                    text="CURRENT COST:", manager=ctx.manager)

        self.current_cost_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 125), (200, 40)),
                                                              text="0", manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 155), (200, 40)),
                                    text="NODES EXPLORED:", manager=ctx.manager)

        self.nodes_explored_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 175), (200, 40)),
                                                                text="0", manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 205), (200, 40)),
                                    text="PATH LENGTH:", manager=ctx.manager)

        self.path_length_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 225), (200, 40)),
                                                             text="??", manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 255), (200, 40)),
                                    text="PATH COST:", manager=ctx.manager)

        self.path_cost_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 275), (200, 40)),
                                                           text="??", manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 305), (200, 40)),
                                    text="SELECTED ALGORITHM", manager=ctx.manager)

        self.algo_selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((570, 337), (200, 86)),
                                                                       item_list=["Depth-First Search",
                                                                                  "Breadth-First Search", "Dijkstra's",
                                                                                  "A*"],
                                                                       default_selection="Depth-First Search",
                                                                       manager=ctx.manager)

        self.benchmark_all_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((570, 430), (200, 40)),
                                                                 text="BENCHMARK ALL",
                                                                 manager=ctx.manager)

        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((570, 468), (200, 40)),
                                    text="SPEED", manager=ctx.manager)

        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((570, 500), (200, 28)),
                                                                   start_value=150, value_range=(300, 0),
                                                                   click_increment=1, manager=ctx.manager)

        self.back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((570, 540), (90, 40)),
                                                        text="BACK",
                                                        manager=ctx.manager)

        self.start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((680, 540), (90, 40)),
                                                         text="START",
                                                         manager=ctx.manager)

    def run(self, ctx: Context):
        # Called every frame when the screen is active
        for event in pygame.event.get():
            # Process Manager UI Events
            ctx.manager.process_events(event)
            # Process other events
            if event.type == pygame.QUIT:
                ctx.quit = True
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_button:
                    ctx.manager.clear_and_reset()
                    ctx.set_screen_to(ctx.select_screen)
                elif event.ui_element == self.start_button:
                    algorithm = self.algo_selection_list.get_single_selection()
                    self.set_algorithm_and_start(algorithm)
                    self.title_label.set_text(f"Searching using {algorithm}...")
                    print(
                        f"\nSearching for path between {ctx.active_maze.start} and {ctx.active_maze.goal} using {algorithm}...\n")
                elif event.ui_element == self.benchmark_all_button:
                    self.run_benchmarks(ctx)

        if self.state == MazeScreenState.SEARCHING:
            # Calculate time since last update, if past a threshold defined by the speed slider, update the searcher
            self.time_since_last_update += ctx.time_delta
            if self.time_since_last_update > self.speed_slider.get_current_value() / 300:
                self.time_since_last_update = 0
                step_result = self.searcher.step()

                # Update the UI
                self.nodes_explored_label.set_text(str(self.searcher.nodes_explored))
                curr_node_data = self.searcher.get_node_data(self.searcher.current_pos)
                self.current_cost_label.set_text(str(curr_node_data.path_cost))
                self.current_depth_label.set_text(str(curr_node_data.depth))

                # Print the result of the search step to console for debugging purposes
                # print(step_result[1])

                # Update path length on UI and switch to animating movement if the search returns completed
                if step_result[0]:
                    self.on_search_complete(ctx)

        # Draw the maze including its background and search progress
        self.maze_drawer.draw_maze(ctx)

        # Draws path if one exists
        self.maze_drawer.draw_path(ctx)

        # Update the agent position while animating movement, if it completes change state to IDLE
        if self.state == MazeScreenState.ANIMATING_MOVEMENT:
            if next(self.movement_iter, True):
                self.state = MazeScreenState.IDLE

        # If agent has a position draw it
        if self.agent_position is not None:
            self.maze_drawer.draw_agent(ctx, self.agent_position)

    def set_algorithm_and_start(self, algorithm: str):
        # Set the function to be called by the searcher
        if algorithm == "Depth-First Search":
            self.searcher.set_algorithm(dfs.run)
        elif algorithm == "Breadth-First Search":
            self.searcher.set_algorithm(bfs.run)
        elif algorithm == "Dijkstra's":
            self.searcher.set_algorithm(dijkstra.run)
        elif algorithm == "A*":
            self.searcher.set_algorithm(astar.run)
        else:
            print("Please select an algorithm first")
            return

        # Reset UI elements and set the state to SEARCHING
        self.algorithm_label.set_text(algorithm)
        self.nodes_explored_label.set_text("0")
        self.path_length_label.set_text("??")
        self.path_cost_label.set_text("??")
        self.current_cost_label.set_text("0")
        self.current_depth_label.set_text("0")
        self.agent_position = None
        self.state = MazeScreenState.SEARCHING

    def on_search_complete(self, ctx: Context):
        # Update path length label
        path_length = len(self.searcher.path)
        self.path_length_label.set_text(str(path_length - 1) if path_length != 0 else "??")
        self.path_cost_label.set_text(str(self.searcher.path_cost) if path_length != 0 else "??")
        self.current_depth_label.set_text("-")
        self.current_cost_label.set_text("-")

        # Print output to console
        print(f"\n==== SEARCH COMPLETE ====")
        print(f"Maze: {ctx.active_maze.file_name}")
        print(f"Algorithm: {self.algorithm_label.text}")
        print(f"Start: {ctx.active_maze.start}")
        print(f"Goal: {ctx.active_maze.goal}")
        print(f"Nodes Explored: {self.searcher.nodes_explored}")
        print(f"Path Length: {str(path_length - 1) if path_length != 0 else 'NO PATH FOUND'}")
        print(f"Path Cost: {str(self.searcher.path_cost) if path_length != 0 else 'NO PATH FOUND'}\n")

        # Begin animation
        self.movement_iter = iter(animate_movement(ctx, self.searcher.path, self))
        self.state = MazeScreenState.ANIMATING_MOVEMENT

    # Run through all the different algorithms on the maze, printing the results to the console
    def run_benchmarks(self, ctx: Context):
        print("\n\n==== RUNNING BENCHMARKS USING ALL SEARCH ALGORITHMS ====")
        print(f"Maze: {ctx.active_maze.file_name}")
        print(f"Start: {ctx.active_maze.start}")
        print(f"Goal: {ctx.active_maze.goal}")
        self.run_benchmark(ctx, dfs.run, "Depth-First Search")
        self.run_benchmark(ctx, bfs.run, "Breadth-First Search")
        self.run_benchmark(ctx, dijkstra.run, "Dijkstra's")
        self.run_benchmark(ctx, astar.run, "A*")

    def run_benchmark(self, ctx: Context, algorithm, algorithm_name: str):
        num_runs = 50

        timer = time.perf_counter()

        for x in range(num_runs):
            self.searcher.run_search(algorithm)

        average_time = (time.perf_counter() - timer) * 1000 / num_runs

        path_length = len(self.searcher.path)
        print(f"\n== {algorithm_name} ==")
        print(f"Nodes Explored: {self.searcher.nodes_explored}")
        print(f"Path Length: {str(path_length - 1) if path_length != 0 else 'NO PATH FOUND'}")
        print(f"Path Cost: {str(self.searcher.path_cost) if path_length != 0 else 'NO PATH FOUND'}")
        print(f"Operate time (average over {num_runs} runs): {average_time:0.3F} ms")


def animate_movement(ctx: Context, path: list[int2], maze_screen: MazeScreen):
    """
    Crude generator for  animation of agent moving from start to goal
    """
    if len(path) == 0:
        maze_screen.title_label.set_text("No path found...")
        return

    maze_screen.title_label.set_text("Animating agent movement...")

    # Set agent initial position
    maze_screen.agent_position = (float(path[0].x), float(path[0].y))

    for idx, xy in enumerate(path):
        # If we've reached the end of the path, reset the title label and exit out
        if idx + 1 == len(path):
            maze_screen.title_label.set_text("Press start...")
            return

        # Get the position we are moving from and to
        pos = (float(xy.x), float(xy.y))
        next_pos = (float(path[idx + 1].x), float(path[idx + 1].y))

        # Calculate direction of movement, clamped to -1, 1
        dir_x = clamp(next_pos[0] - pos[0], -1.0, 1.0)
        dir_y = clamp(next_pos[1] - pos[1], -1.0, 1.0)

        # Until the agent reaches the next position, keep adding to its current xy pxl position
        while maze_screen.agent_position != next_pos:
            new_x = maze_screen.agent_position[0] + ctx.time_delta * AGENT_ANIMATION_SPEED * dir_x
            new_y = maze_screen.agent_position[1] + ctx.time_delta * AGENT_ANIMATION_SPEED * dir_y

            # A little crude but ensures we don't go past the target xy
            if dir_x > 0:
                new_x = min(new_x, next_pos[0])
            else:
                new_x = max(new_x, next_pos[0])
            if dir_y > 0:
                new_y = min(new_y, next_pos[1])
            else:
                new_y = max(new_y, next_pos[1])

            # Update the agent position and yield to draw changes
            maze_screen.agent_position = (new_x, new_y)
            yield
