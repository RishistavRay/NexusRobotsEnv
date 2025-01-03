import heapq
from constants import *

def heuristic(start, goal):
    """
    Heuristic function for A* search. This uses Manhattan distance between the
    current point and the goal point, assuming the movement is grid-based.
    """
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

def a_star_search(start, goal):
    """
    A* search algorithm to find the shortest path between start and goal.
    Returns the list of nodes in the path from start to goal.
    """
    # Open and closed sets
    open_set = []
    closed_set = set()

    # Heap queue for open set, initialized with the start point
    heapq.heappush(open_set, (0, start))

    # Cost from start to each point (g-score)
    g_score = {start: 0}

    # Estimated total cost from start to goal through each point (f-score)
    f_score = {start: heuristic(start, goal)}

    # To reconstruct the path
    came_from = {}

    while open_set:
        # Get the node with the lowest f-score
        _, current = heapq.heappop(open_set)

        # If we reached the goal, reconstruct the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        closed_set.add(current)

        # Check neighbors (4-connected grid)
        for neighbor in get_neighbors(current):
            if neighbor in closed_set or not is_valid(neighbor):
                continue

            tentative_g_score = g_score[current] + 1  # All moves have a cost of 1

            # If this path is better, add it to the open set
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Return empty if no path found

def get_neighbors(position):
    """
    Returns the list of valid neighboring positions.
    This assumes movement is allowed in 4 directions (up, down, left, right).
    """
    x, y = position
    neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    return neighbors

def is_valid(position):
    """
    Determines if the position is valid (i.e., it is within the bounds of the grid and not an obstacle).
    """
    x, y = position
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return True
    return False