from src.int2 import int2
from src.searcher import Searcher


def run(searcher: Searcher):
    """
    Performs DFS search. Yields after each Pop and after processing all directions to allow for GUI updates.
    Returns a str containing information about the step that is currently in process
    """

    # Initialises the searcher, clearing the queues and resetting the Nodes to default
    searcher.initialise()

    # Add the starting position to the queue
    searcher.deque.append(searcher.maze.start)
    searcher.get_node_data(searcher.maze.start).update_node_data(None, 0, 0)

    # Loop until the queue is empty
    while len(searcher.deque) > 0:
        # As this is DFS search get the most recently added node off the queue, LIFO, using pop()
        pos = searcher.deque.pop()
        searcher.current_pos = pos
        curr_node_data = searcher.get_node_data(pos)
        curr_node_data.decrement_queue_count()

        # Yield execution to allow graphical update of progress
        yield False, f"Popped {pos} off the top of the queue."

        # Skip this node if it has already been visited
        if curr_node_data.visited:
            yield False, "  Already explored, skipping..."
            continue

        # Increment node explored
        searcher.nodes_explored += 1

        # Set this node as visited so we skip it if it appears in the queue again
        curr_node_data.visited = True

        # Check if this node is the goal node and break
        if searcher.maze.is_goal(pos):
            yield True, f"  Found goal node {pos}."

        # Process all the valid neighbours of this node, is a list of (pos, edge_cost) tuples
        # Given DFS behaviour will mean search will prefer to go in the reverse order - IE explore north first
        for neighbour in searcher.maze.get_neighbours(pos):
            searcher.current_neighbour_pos = neighbour[0]
            yield False, f"  Processing neighbour {neighbour[0]}."
            # Processes the neighbour, yields a string explaining the current processing step
            yield process_neighbour(searcher, pos, neighbour[0], curr_node_data.path_cost + neighbour[1],
                                    curr_node_data.depth + 1)

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

    # Add this node to the queue
    searcher.deque.append(pos)

    # Update the node data with parent, cost to reach node, and current depth. Do not overwrite parent if it exists
    curr_node_data.update_node_data(parent, cost, depth, False)
    # Store that this node is currently being added to the queue for display purposes
    searcher.adding_to_queue_pos = pos

    return False, "    Added to the queue."
