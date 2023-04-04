from src.int2 import int2
from src.maze import Maze
from src.searcher import Searcher, QueueNode


def run(searcher: Searcher):
    """
    Performs Dijkstra search. Finds the smallest distance between two nodes, recording cost
    Yields after each Pop and after processing all directions to allow for GUI updates.
    Returns a str containing information about the step that is currently in process
    """

    # Initialises the searcher, clearing the queue and resetting the Nodes to default
    searcher.initialise()

    # Add the starting position to the priority queue
    searcher.priority_queue.push(QueueNode(searcher.maze.start, 0))
    searcher.get_node_data(searcher.maze.start).update_node_data(None, 0, 0)

    # Loop until the queue is empty
    while not searcher.priority_queue.empty():
        # Dijkstra search get the QueueNode off the queue with the lowest cost from the starting node
        curr_queue_node = searcher.priority_queue.pop()
        pos = curr_queue_node.pos
        searcher.current_pos = pos
        curr_node_data = searcher.get_node_data(pos)
        curr_node_data.decrement_queue_count()

        # Set current node as visited, and increment node explored
        curr_node_data.visited = True
        searcher.nodes_explored += 1

        # Yield execution to allow graphical update of progress
        yield False, f"Retrieved node {pos} with lowest cost from the start position from the queue."

        # Check if this node is the goal node and break
        if searcher.maze.is_goal(pos):
            yield True, f"  Found goal node {pos}."

        # Process all the valid neighbours of this node, is a list of (pos, edge_cost) tuples
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

    # Get the node of the neighbour
    curr_node_data = searcher.get_node_data(pos)

    # If we've already added this node to the queue with a shorter path, skip
    if curr_node_data.path_cost is not None and curr_node_data.path_cost <= cost:
        return False, "    Already found shorter path, skipping..."

    # Add it to the priority queue with consideration of cost to this node
    searcher.priority_queue.push(QueueNode(pos, cost))

    # Update the node data with parent, cost to reach node, and current depth
    curr_node_data.update_node_data(parent, cost, depth)
    # Store that this node is currently being added to the queue for display purposes
    searcher.adding_to_queue_pos = pos

    return False, "    Added to the queue."
