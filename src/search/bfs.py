from src.int2 import int2
from src.maze import Maze
from src.searcher import Searcher, QueueNode
from collections import deque


def run(searcher: Searcher):
    """
    Executes Breadth First Search Algorithm (BFS).
    Visits all nodes at the current depth before moving to the next depth.
    Yields after each popleft and after processing all directions to allow for GUI updates.
    """

    # Initialises the searcher and clearing the queue, resetting the Nodes to default
    searcher.initialise()

    # Add the starting position to the queue, Deque to enable FIFO behaviour
    searcher.deque.append(searcher.maze.start)
    searcher.get_node_data(searcher.maze.start).update_node_data(None, 0, 0)

    # while priority queue is not empty
    while len(searcher.deque) > 0:
        # This is BFS search gets source node (first node inserted into queue) off the queue, FIFO using popleft()
        pos = searcher.deque.popleft()
        searcher.current_pos = pos
        curr_node_data = searcher.get_node_data(pos)
        curr_node_data.decrement_queue_count()

        # Set current node as visited, and increment node explored
        curr_node_data.visited = True
        searcher.nodes_explored += 1

        # Yield execution to allow graphical update of progress
        yield False, f"Dequeued {pos} from the queue."

        # Check if this node is the goal node and break
        if searcher.maze.is_goal(pos):
            yield True, f"  Found goal node {pos}."

        # Process all the valid neighbours of this node, is a list of (pos, edge_cost) tuples
        # BFS will start at the tree root (source node/ starting node) and explore all nodes at the present depth
        # prior to moving on to the nodes at the next depth level.
        for neighbour in searcher.maze.get_neighbours(pos):
            searcher.current_neighbour_pos = neighbour[0]
            yield False, f"  Processing neighbour {neighbour[0]}."
            # Processes the neighbour, yields a string explaining the current processing step
            yield process_neighbour(searcher, pos, neighbour[0], curr_node_data.path_cost + neighbour[1], curr_node_data.depth + 1)

        # Clear that any neighbour is being processed
        searcher.current_neighbour_pos = None

        # Clear that any node is being added to the queue
        searcher.adding_to_queue_pos = None

    yield True, "Path not found."


def process_neighbour(searcher: Searcher, parent: int2, pos: int2, cost: int, depth: int) -> tuple[bool, str]:
    """
    Tests if a neighbour node is suitable for adding to queue, if so it's added
    """

    # Get the node data of this neighbour
    curr_node_data = searcher.get_node_data(pos)

    # Verify we haven't visited this node yet, and it hasn't already been added to queue
    if curr_node_data.visited:
        return False, "    Already visited, skipping..."
    if curr_node_data.in_queue():
        return False, "    Already in queue, skipping..."

    # Add this node to the queue
    searcher.deque.append(pos)

    # Update the node data with parent, cost to reach node, and current depth
    curr_node_data.update_node_data(parent, cost, depth)
    # Store that this node is currently being added to the queue for display purposes
    searcher.adding_to_queue_pos = pos

    return False, "    Added to the Queue."
