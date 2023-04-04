from src.int2 import int2


class Maze:
    """
    Class structure to define the maze, including dimensions, start and goal positions, and a 2D grid of walls
    """
    # Maze name
    file_name: str

    # xy dimensions of the maze
    dimensions: int2

    # 2D list of a tuple of bools, first index indicates a wall, second index indicates rough terrain
    nodes: list[list[tuple[bool, bool]]]

    # Offsets to access neighbouring nodes in the four directions
    neighbour_offsets: list[int2]

    # Start position (x, y)
    start: int2

    # Goal position (x, y)
    goal: int2

    def __init__(self, file_name: str, dimensions: int2, nodes: list[list[tuple[bool, bool]]], start: int2, goal: int2):
        self.file_name = file_name
        self.dimensions = dimensions
        self.nodes = nodes
        self.start = start
        self.goal = goal
        self.neighbour_offsets = [int2(-1, 0), int2(0, 1), int2(1, 0), int2(0, -1)]

    # Returns true if the node is a wall
    def is_wall(self, pos: int2) -> bool:
        return self.nodes[pos.y][pos.x][0]

    # Returns true if the node is rough terrain
    def is_rough(self, pos: int2) -> bool:
        return self.nodes[pos.y][pos.x][1]

    def is_goal(self, pos: int2) -> bool:
        return self.goal == pos

    # Returns the cost of traversing an edge to the given xy position, returns None if no edge exists
    def get_edge_cost_to(self, pos: int2) -> int:
        if pos.x < 0 or pos.x >= self.dimensions.x or pos.y < 0 or pos.y >= self.dimensions.y:
            return None
        if self.is_wall(pos):
            return None
        if self.is_rough(pos):
            return 5
        return 1

    # Returns a list of the valid neighbours of the given position as tuple including edge cost
    def get_neighbours(self, pos: int2) -> list[(int2, int)]:
        neighbours = []

        # Iterate over the neighbours in all four directions, in the order W S E N
        for offset in self.neighbour_offsets:
            # Calculate the neighbours xy position
            neighbour_pos = pos + offset

            # Determine the cost of traversing the edge to the neighbour
            edge_cost = self.get_edge_cost_to(neighbour_pos)

            # If the xy position is out of bounds or this neighbour is a wall, skip
            if edge_cost is None:
                continue

            # Add to the list of neighbours
            neighbours.append((neighbour_pos, edge_cost))

        return neighbours
