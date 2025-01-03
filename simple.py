import pygame
from pygame.locals import QUIT
import math
import time

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_ROWS = 10
GRID_COLS = 10
CELL_SIZE = 50  # Size of each grid cell
PADDING = 50  # Padding around the grid for display
ROBOT_SPEED = 4  # Pixels per frame
ROBOT_RADIUS = 15  # Radius of the robots (can be changed)
SHELF_SIZE = CELL_SIZE  # Shelf size (same as grid cell size)
SHELF_RADIUS = SHELF_SIZE // 2  # Collision radius for shelf (half the size of the shelf)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Grid with Padding and Robot Collision")

# Draw the grid
def draw_grid():
    screen.fill(WHITE)
    for r in range(GRID_ROWS + 1):
        pygame.draw.line(
            screen, BLACK,
            (PADDING, PADDING + r * CELL_SIZE), 
            (PADDING + GRID_COLS * CELL_SIZE, PADDING + r * CELL_SIZE), 1
        )
    for c in range(GRID_COLS + 1):
        pygame.draw.line(
            screen, BLACK,
            (PADDING + c * CELL_SIZE, PADDING), 
            (PADDING + c * CELL_SIZE, PADDING + GRID_ROWS * CELL_SIZE), 1
        )

# Convert logical position to display position (add padding for display purposes)
def logical_to_display(logical_pos):
    x, y = logical_pos
    return x * CELL_SIZE + PADDING, y * CELL_SIZE + PADDING

# Smoothly move the robot toward the target
def smooth_move(robot_pos, target_pos):
    x, y = robot_pos
    target_x, target_y = target_pos

    # Move in x direction
    if x < target_x:
        x += min(ROBOT_SPEED, target_x - x)
    elif x > target_x:
        x -= min(ROBOT_SPEED, x - target_x)

    # Move in y direction
    if y < target_y:
        y += min(ROBOT_SPEED, target_y - y)
    elif y > target_y:
        y -= min(ROBOT_SPEED, y - target_y)

    return x, y

# Check for collision between two robots (based on radius)
def check_collision(robot_pos1, robot_pos2, radius1, radius2):
    # Calculate the distance between the centers of the robots
    distance = math.sqrt((robot_pos1[0] - robot_pos2[0])**2 + (robot_pos1[1] - robot_pos2[1])**2)
    
    # If the distance is less than or equal to the sum of their radii, a collision occurs
    return distance <= (radius1 + radius2)

# Check if the robot has reached its target
def has_reached_target(robot_pos, target_pos):
    return robot_pos == target_pos

# Function to move a robot
def move_robot(logical_robot_pos, target_pos):
    return target_pos

# Function to pick up a shelf
def pick_up_shelf(robot_pos, shelf_intersection):
    # Check if the robot is within one cell distance of the shelf
    print(robot_pos[0], shelf_intersection[0])
    return robot_pos[0] == shelf_intersection[0]

# Function to drop a shelf
def drop_shelf(robot_pos, carrying_shelf, shelf_intersection):
    return robot_pos == shelf_intersection

# Main loop
def main():
    running = True
    clock = pygame.time.Clock()

    # Initial robot positions in logical grid coordinates
    logical_robot1_pos = (0, 0)  # Top-left corner of the grid
    logical_robot2_pos = (1, 0)  # Another robot's initial position

    logical_target1_pos = logical_robot1_pos  # Robot 1 target
    logical_target2_pos = logical_robot2_pos  # Robot 2 target

    display_robot1_pos = logical_to_display(logical_robot1_pos)
    display_robot2_pos = logical_to_display(logical_robot2_pos)

    moving_robot1 = False  # Track if Robot 1 is moving
    moving_robot2 = False  # Track if Robot 2 is moving

    carrying_shelf = False  # Track if a robot is carrying a shelf
    shelf_offset = (0, 0)  # Shelf offset relative to the robot

    collision_count = 0  # Initialize collision counter

    # Shelf position at a grid intersection (e.g., at (2, 3) on the grid)
    shelf_intersection = (2, 3)
    display_shelf_pos = logical_to_display(shelf_intersection)

    # Hardcoded scenario instructions (sequence of actions)
    instructions = [
        ("move", logical_robot1_pos, (0, 1)),
        ("move", logical_robot1_pos, (0, 2)),
        ("move", logical_robot1_pos, (0, 3)),
        ("move", logical_robot1_pos, (1, 3)),
        ("move", logical_robot1_pos, (2, 3)),
        ("pick_up_shelf", logical_robot1_pos, shelf_intersection),
        ("move", logical_robot1_pos, (3, 3)),
        ("drop_shelf", logical_robot1_pos, shelf_intersection),
        ("move", logical_robot2_pos, (2, 1)),
    ]

    # Loop through the instructions
    instruction_index = 0
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Execute the next instruction
        if instruction_index < len(instructions):
            action, robot_pos, target_pos = instructions[instruction_index]

            if action == "move":
                logical_robot1_pos = move_robot(logical_robot1_pos, target_pos)
                display_robot1_pos = smooth_move(display_robot1_pos, logical_to_display(logical_robot1_pos))
                if has_reached_target(display_robot1_pos, logical_to_display(logical_robot1_pos)):
                    instruction_index += 1  # Move to next instruction

            elif action == "pick_up_shelf":
                
                    carrying_shelf = True
                    shelf_offset = (display_robot1_pos[0] - display_shelf_pos[0], display_robot1_pos[1] - display_shelf_pos[1])
                    instruction_index += 1

            elif action == "drop_shelf":
                if drop_shelf(robot_pos, carrying_shelf, shelf_intersection):
                    shelf_intersection = logical_robot1_pos
                    carrying_shelf = False
                    shelf_offset = (0, 0)
                    instruction_index += 1

        # Draw the grid, robots, and shelf
        draw_grid()
        pygame.draw.circle(screen, RED, display_robot1_pos, ROBOT_RADIUS)  # Robot 1
        pygame.draw.circle(screen, BLUE, display_robot2_pos, ROBOT_RADIUS)  # Robot 2

        # Draw shelf at the grid intersection (center of the intersection)
        pygame.draw.rect(screen, BLACK, (display_shelf_pos[0] - SHELF_RADIUS, display_shelf_pos[1] - SHELF_RADIUS, SHELF_SIZE, SHELF_SIZE), 3)

        # Display collision count
        font = pygame.font.Font(None, 36)
        text = font.render(f"Collisions: {collision_count}", True, BLACK)
        screen.blit(text, (10, SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
