import queue
from collections import deque
from typing import Iterator

from src.maze import Maze
from src.int2 import int2


class NodeData:
    """
    Data for each node on the graph
    """

    # The (x, y) position that precedes this node in a path, used for reconstructing the path
    parent: int2

    # Best cost from the start position to this node so far, including extra cost of traversing rough
    path_cost: int

    # The depth of this node when searching, always increases by 1 regardless of edge cost
    depth: int

    # Whether this node has been visited by the algorithm or not
    visited: bool

    # How many times this node appears in the queue for rendering purposes
    in_queue_count: int

    def __init__(self):
        self.parent = None
        self.path_cost = None
        self.depth = None
        self.visited = False
        self.in_queue_count = 0

    def in_queue(self):
        return self.in_queue_count != 0

    def decrement_queue_count(self):
        # Decrease the counter for the number of times this node is in the queue for visualisation
        self.in_queue_count -= 1

    def update_node_data(self, parent: int2, path_cost: int, depth: int, overwrite_parent=True):
        # Increase the counter for the number of times this node is in the queue for visualisation
        self.in_queue_count += 1
        # Set the parent node for tracing the path
        if overwrite_parent or self.parent is None:
            self.parent = parent
        # Set the cost to reach this node
        self.path_cost = path_cost
        # Set the depth of this node
        self.depth = depth


class QueueNode:
    """
    Data structure to use in the PriorityQueue to track nodes that need visiting.
    """
    # X,Y position of the node
    pos: int2
    # Cost, can mean different things for different algorithms, but the queue will return the QueueNode with the
    # lowest cost first, with ties broken by whatever node was added last, io LIFO
    cost: int

    def __init__(self, pos: int2, cost: int):
        self.pos = pos
        self.cost = cost


class PriorityQueue:
    """
    Wrapper for priority queue that allows for strong typing of the stored data, and changing to LIFO behaviour
    """
    q: queue.PriorityQueue

    # Used in the priority queue, gives a second element to sort by allowing it to behave as LIFO rather than FIFO
    sort_order_number: int

    def __init__(self):
        self.q = queue.PriorityQueue()
        self.sort_order_number = 0

    def push(self, queue_node: QueueNode):
        """
        Pushes a new item to the queue
        """
        self.q.put((queue_node.cost, self.sort_order_number, queue_node.pos))
        # Decrement the sort order number for next item, when popping items from the queue it will behave as LIFO
        self.sort_order_number -= 1

    def pop(self) -> QueueNode:
        """
        Gets the node with the smallest cost
        """
        result = self.q.get()
        return QueueNode(result[2], result[0])

    def empty(self) -> bool:
        """
        Checks if the Queue is empty
        """
        return self.q.empty()


class Searcher:
    # Maze to be searched
    maze: Maze

    # Queue structure for storing (x,y) positions to process during pathfinding.
    # Used in Algorithm DFS & BFS, acts as LIFO for BFS using pop(), and FIFO for DFS using popleft()
    deque: deque[int2]

    # Alternate priority queue data structure used in Algorithms Astar, Dijkstra
    priority_queue: PriorityQueue

    # Current (x,y) position being visited during pathfinding
    current_pos: int2

    # Current neighbour (x,y) position being processed
    current_neighbour_pos: int2

    # Node that is currently being added to the queue
    adding_to_queue_pos: int2

    # Node data for the search, includes path information, costs, visited status and whether in queue
    nodes: list[list[NodeData]]

    # A count of the total number of nodes visited
    nodes_explored: int

    # Iterator of the search algorithm to run
    iterator: Iterator

    # Reconstructed Path from start to goal
    path: list[int2]

    # Total cost of the path
    path_cost: int

    def __init__(self, maze: Maze):
        self.maze = maze
        self.path = []
        self.deque = deque()
        self.priority_queue = PriorityQueue()
        self.nodes = [[NodeData() for x in range(maze.dimensions.x)] for y in range(maze.dimensions.y)]
        self.current_pos = None
        self.current_neighbour_pos = None
        self.adding_to_queue_pos = None
        self.nodes_explored = 0
        self.path = []
        self.path_cost = None

    def set_algorithm(self, algorithm):
        self.iterator = iter(algorithm(self))

    def initialise(self):
        self.deque = deque()
        self.priority_queue = PriorityQueue()
        self.nodes = [[NodeData() for x in range(self.maze.dimensions.x)] for y in range(self.maze.dimensions.y)]
        self.current_pos = None
        self.current_neighbour_pos = None
        self.adding_to_queue_pos = None
        self.nodes_explored = 0
        self.path = []
        self.path_cost = None

    def step(self) -> tuple[bool, str]:
        """
        Performs a single step through the search algorithm
        :return: A tuple (bool, str) where bool is True when algorithm complete, and str is a message to display
        """
        result = next(self.iterator, (True, str))

        # Calculate the path if completed
        if result[0]:
            self.calculate_path()

        return result

    # Run a search from start to finish without yielding
    def run_search(self, algorithm):
        iterator = iter(algorithm(self))
        for result in iterator:
            if result[0]:
                break
        self.calculate_path()

    def get_node_data(self, pos: int2) -> NodeData:
        """
        Returns the NodeData for the provided xy position
        """
        return self.nodes[pos.y][pos.x]

    def calculate_path(self):
        """
        Stores the reconstructed path from Start to Goal if one exists, otherwise stores an empty list
        """
        self.path = []

        # Starting at the end point
        curr_node_data = self.get_node_data(self.maze.goal)

        # Add end point cost to the path cost
        self.path_cost = self.maze.get_edge_cost_to(self.maze.goal)

        # If we have never visited the goal node and set its came_from attribute then there was no path, exit
        if curr_node_data.parent is None:
            return

        # Add goal node
        self.path.append(self.maze.goal)

        # Loop over the came_from values until we reach the start node
        while curr_node_data.parent != self.maze.start:
            self.path.append(curr_node_data.parent)
            # Add the cost of traversing this edge
            self.path_cost += self.maze.get_edge_cost_to(curr_node_data.parent)
            curr_node_data = self.get_node_data(curr_node_data.parent)

        # Add start node
        self.path.append(self.maze.start)

        # Reverse the path so it's in order from Start -> Goal
        self.path.reverse()
