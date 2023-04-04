# CONSTANTS
# Colours
BACKGROUND_COLOUR = (40, 40, 40)
BORDER_COLOUR = (30, 30, 30)
WALL_TILE_COLOUR = (30, 30, 30)
ROUGH_TILE_COLOUR = (193, 154, 107)
FLOOR_TILE_COLOUR = (220, 220, 220)
ACTIVE_TILE_COLOUR = (125, 158, 192)
AGENT_COLOUR = (253, 255, 0)
START_TILE_COLOUR = (76, 187, 23)
GOAL_TILE_COLOUR = (238, 75, 43)
IN_QUEUE_MARKER_COLOUR = (255, 255, 143)
VISITED_MARKER_COLOUR = (170, 170, 170)
ADDING_TO_QUEUE_MARKER_COLOUR = (124, 252, 0)
VISITING_NEIGHBOUR_MARKER_COLOUR = (0, 255, 255)
PATH_MARKER_COLOUR = (255, 128, 128)

# Dimensions
WINDOW_SIZE = [800, 600]
MAZE_SIZE = [600, 600]

# Percentage of the tile the agent circle should cover
AGENT_RADIUS_PCT = 0.8

# Percentage of the tile the marker circle should cover, for showing running algorithm
MARKER_RADIUS_PCT = 0.4

# Percentage of size of the tile marker that the neighbour marker is
NEIGHBOUR_MARKER_RADIUS_PCT = 0.67

# Percentage of window size reserved for blank space around grid
BUFFER_PCT = 0.15

# Percentage of total cell dimensions reserved for border around cell, will be minimum 1 pixel
BORDER_PCT = 0.05

# Buffer around start/end tile
START_END_BUFFER_PCT = 0.3

# Agent movement speed
AGENT_ANIMATION_SPEED = 9

