import pygame
from pygame import Rect

from src.constants import *
from src.context import Context
from src.int2 import int2
from src.maze import Maze
from src.searcher import Searcher


class MazeDrawer:
    # Maze we are drawing
    maze: Maze

    # Searcher we are using on the maze
    searcher: Searcher

    # Maze pixel start position
    draw_start_xy: tuple[int, int]

    # Background/border for the maze
    maze_border_rect: Rect

    # Dimensions for a tile including its border
    tile_size: int

    # Dimensions for a tile excluding its border
    tile_inner_size: int

    # Number of pixels for the tile border
    tile_border_size: int

    # Radius for drawing the agent circle
    agent_radius: int

    # Radius for drawing the marker circle
    marker_radius: int

    # Radius for drawing the marker indicating currently processing neighbour
    neighbour_radius: int

    # Dimensions for the start/end rect
    start_end_dim: int

    def __init__(self, maze: Maze):
        self.maze = maze
        self.searcher = None

        # Calculate the total number of pixels reserved for a buffer around the maze in each dimension
        buffer_x = int(MAZE_SIZE[0] * BUFFER_PCT)
        buffer_y = int(MAZE_SIZE[1] * BUFFER_PCT)

        # Calculate the maximum tile width/height so we can display the entire maze at once as large as possible
        max_tile_width = (MAZE_SIZE[0] - buffer_x) / self.maze.dimensions.x
        max_tile_height = (MAZE_SIZE[1] - buffer_y) / self.maze.dimensions.y

        # Use the smallest value of max_tile_width/height, this becomes the total dimension of a tile including border
        self.tile_size = int(min(max_tile_height, max_tile_width))

        # Calculate the border size of the tile as a percentage of the total dimension, minimum 1 pixel
        self.tile_border_size = max(int(self.tile_size * BORDER_PCT), 1)

        # Calculate the dimension of the tile without borders
        self.tile_inner_size = self.tile_size - self.tile_border_size * 2

        # Calculate the offset from the edge of the screen to start drawing the maze
        self.draw_start_xy = (int(buffer_x / 2), int(buffer_y / 2))

        # Center the maze vertically/horizontally
        if max_tile_height < max_tile_width:
            self.draw_start_xy = (
                int(MAZE_SIZE[0] / 2 - self.tile_size * self.maze.dimensions.x / 2), self.draw_start_xy[1])
        else:
            self.draw_start_xy = (
                self.draw_start_xy[0], int(MAZE_SIZE[1] / 2 - self.tile_size * self.maze.dimensions.y / 2))

        # Calculate the start and end pixel positions for the background/border for the maze
        maze_border_start = (
            self.draw_start_xy[0] - self.tile_border_size, self.draw_start_xy[1] - self.tile_border_size)
        maze_border_end = (self.tile_size * self.maze.dimensions.x + self.tile_border_size * 2,
                           self.tile_size * self.maze.dimensions.y + self.tile_border_size * 2)
        self.maze_border_rect = Rect(maze_border_start, maze_border_end)

        # Calculates the radius for the agent circle
        self.agent_radius = AGENT_RADIUS_PCT * self.tile_inner_size / 2

        # Calculates the radius for the marker circle
        self.marker_radius = MARKER_RADIUS_PCT * self.tile_inner_size / 2

        # Calculates the radius for the marker indicating currently active neighbour
        self.neighbour_radius = self.marker_radius * NEIGHBOUR_MARKER_RADIUS_PCT

        # Calculate the dimensions for the start/end rect
        self.start_end_dim = int(self.tile_inner_size * (1 - START_END_BUFFER_PCT))

    def set_searcher(self, searcher: Searcher):
        self.searcher = searcher

    def draw_maze(self, ctx: Context):
        # Draw background behind entire maze, sets border colour
        pygame.draw.rect(ctx.surface, BORDER_COLOUR, self.maze_border_rect)

        # Iterate over the nodes of the maze
        for y in range(self.maze.dimensions.y):
            for x in range(self.maze.dimensions.x):
                curr = int2(x, y)
                tile_colour = FLOOR_TILE_COLOUR

                # Adjust the tile colour
                if self.maze.is_wall(curr):
                    tile_colour = WALL_TILE_COLOUR
                if curr == self.maze.start:
                    tile_colour = START_TILE_COLOUR
                elif curr == self.maze.goal:
                    tile_colour = GOAL_TILE_COLOUR
                elif self.searcher is not None and self.searcher.current_pos is not None and curr == self.searcher.current_pos:
                    tile_colour = ACTIVE_TILE_COLOUR
                elif self.maze.is_rough(curr):
                    tile_colour = ROUGH_TILE_COLOUR

                # Calculate start position for tile, then draw
                x_pxl = int(self.draw_start_xy[0] + self.tile_size * x + self.tile_border_size)
                y_pxl = int(self.draw_start_xy[1] + self.tile_size * y + self.tile_border_size)
                pygame.draw.rect(ctx.surface, tile_colour, (x_pxl, y_pxl, self.tile_inner_size, self.tile_inner_size))

                # No searcher attached so no search progress to draw, continue on
                if self.searcher is None:
                    continue

                curr_node = self.searcher.get_node_data(curr)

                # Calculate marker colour, then draw
                if self.searcher.adding_to_queue_pos is not None and curr == self.searcher.adding_to_queue_pos:
                    marker_colour = ADDING_TO_QUEUE_MARKER_COLOUR
                elif curr_node.visited:
                    marker_colour = VISITED_MARKER_COLOUR
                elif curr_node.in_queue():
                    marker_colour = IN_QUEUE_MARKER_COLOUR
                else:
                    continue

                center_x_pxl = int(x_pxl + self.tile_inner_size / 2)
                center_y_pxl = int(y_pxl + self.tile_inner_size / 2)
                self.draw_circle_with_border(ctx, marker_colour, (center_x_pxl, center_y_pxl), self.marker_radius)

        # Skip drawing the current neighbour if there's no searcher attached
        if self.searcher is not None:
            self.draw_current_neighbour(ctx)

    def draw_agent(self, ctx: Context, xy: tuple[float, float]):
        # Draws the agent given x,y float grid position
        x = self.draw_start_xy[0] + float(self.tile_size) * xy[0] + self.tile_size / 2.0
        y = self.draw_start_xy[1] + float(self.tile_size) * xy[1] + self.tile_size / 2.0
        self.draw_circle_with_border(ctx, AGENT_COLOUR, (x, y), self.agent_radius)

    def draw_current_neighbour(self, ctx: Context):
        if self.searcher.current_neighbour_pos is None:
            return
        # Draws the circle on the border between the active tile and the neighbour being processed
        center_x = (self.searcher.current_pos.x + self.searcher.current_neighbour_pos.x + 1) / 2
        center_y = (self.searcher.current_pos.y + self.searcher.current_neighbour_pos.y + 1) / 2
        x = int(self.draw_start_xy[0] + self.tile_size * center_x)
        y = int(self.draw_start_xy[1] + self.tile_size * center_y)
        self.draw_circle_with_border(ctx, VISITING_NEIGHBOUR_MARKER_COLOUR, (x, y), self.neighbour_radius)

    def draw_circle_with_border(self, ctx: Context, colour, xy: tuple[int, int], radius: int):
        pygame.draw.circle(ctx.surface, BORDER_COLOUR, xy, radius + float(self.tile_border_size) * 2.0)
        pygame.draw.circle(ctx.surface, colour, xy, radius)

    def draw_path(self, ctx: Context):
        # Iterates over the path discovered by the search and draws new markers to highlight it
        for xy in self.searcher.path:
            x_pxl = int(self.draw_start_xy[0] + self.tile_size * (xy.x + 0.5))
            y_pxl = int(self.draw_start_xy[1] + self.tile_size * (xy.y + 0.5))
            self.draw_circle_with_border(ctx, PATH_MARKER_COLOUR, (x_pxl, y_pxl), self.marker_radius)
