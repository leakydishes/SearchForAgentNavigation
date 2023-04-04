from src.int2 import int2
from src.maze import Maze
import os
from pathlib import Path


# Mazes are stored in ./mazes/ and are text files ending with .txt
# '#' represents a wall,'.' floor, 'S' the starting position of the agent, and 'G' the goal position
# Mazes must have a start point, a goal point, the dimensions must be rectangular, ie every row has the same width
# and every column must have the same height


def load():
    """
    Loads maze text files into on a dict of Maze class objects where the key is the maze filename
    """

    # Dict to store mazes in
    mazes: dict[str, Maze] = {}

    print("Loading mazes...")

    # Get all directories and files in the mazes directory
    for path in os.scandir("./mazes/"):
        # Skip any directories
        if not path.is_file():
            continue

        # Skip any files that aren't txt files
        if not path.name.endswith(".txt"):
            continue

        print(f"Loading {path.name}")

        file = open(path.path, "r")
        lines = file.readlines()
        if len(lines) == 0:
            raise Exception(f"File '{file.name}' is empty")

        # Set the width of the maze to the length of the first read line with special characters stripped
        width = len(str.strip(lines[0]))
        # Set the height of the maze to the number of lines in the file
        height = len(lines)

        # Initialise start and goal position
        start: int2 = None
        goal: int2 = None

        # Generate an empty grid. (bool, bool) at each position, where the first bool indicates a wall, second is rough terrain
        nodes = [[(False, False) for x in range(width)] for y in range(height)]

        # Iterate over the lines in the file, where y is the current line number
        for y, line in enumerate(lines):
            # Remove carriage returns/whitespaces from line to normalise the line length
            line = str.strip(line)
            # Check that each line matches the width of the first line, otherwise error out
            if len(line) != width:
                raise Exception(f"Non matching line length on line {y}")

            # Iterate the contents of the line char by char, setting terrain and start/end positions
            for x, char in enumerate(line):
                pos = int2(x, y)

                if char == '#':
                    # Is a wall
                    nodes[pos.y][pos.x] = (True, False)
                elif char == '.':
                    # Floor, so no changes
                    pass
                elif char == '^':
                    # Is rough terrain
                    nodes[pos.y][pos.x] = (False, True)
                elif char == 'S':
                    # Make sure we haven't already got a start pos, otherwise set it
                    if start is not None:
                        raise Exception(f"Duplicate start position found at {pos}")
                    start = pos
                elif char == 'G':
                    # Make sure we haven't already got a goal pos, otherwise set it
                    if goal is not None:
                        raise Exception(f"Duplicate goal position found at {pos}")
                    goal = pos
                else:
                    raise Exception(f"Invalid character '{char}' found at {pos}")

        # Ensure we have a start and goal position after all is done
        if start is None or goal is None:
            raise Exception(f"Maze must have both a start and a goal position")

        file.close()
        
        # Get the filename without extension
        maze_name = Path(file.name).stem

        # Create a new Maze instance and add it to the list
        mazes.update({maze_name: Maze(maze_name, int2(width, height), nodes, start, goal)})

    # Return the dict of loaded mazes
    return mazes
