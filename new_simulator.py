import pygame
import random
from a_star.a_star import a_star_search, heuristic
from constants import *


# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_ROWS = 10
GRID_COLS = 10
CELL_SIZE = 50  # Size of each grid cell
PADDING = 50  # Padding around the grid for display
ROBOT_SPEED = 1  # Pixels per frame
ROBOT_RADIUS = 15  # Radius of the robots (can be changed)
SHELF_SIZE = CELL_SIZE  # Shelf size (same as grid cell size)
SHELF_RADIUS = SHELF_SIZE // 2  # Collision radius for shelf (half the size of the shelf)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Robot:
    def __init__(self, robot_id, x, y):
        self.id = robot_id
        self.x = x #grid position
        self.y = y
        self.display_x, self.display_y = self.logical_to_display((x, y))  # Display pixel position
        self.state = "idle"
        self.start_position = (x, y)
        self.end_position = None
        self.shelf_assigned = None
        self.shelf_custody = False
        self.shelf_delivered = False
        self.instruction_start_time = -1
        self.elapsed_time = 0  # basically make anmother called instruction assignment time, then check elapsed time to see how long it has been since robot moved then accordingly make it increment such that it reaches in 1 second. the increments wont be exactly same though 
        self.instructions = []
    
    def has_reached_target(self, robot_pos, target_pos, epsilon=0.001):
        # return robot_pos == target_pos
        return abs(robot_pos[0] - target_pos[0]) < epsilon and abs(robot_pos[1] - target_pos[1]) < epsilon
    
    def logical_to_display(self, logical_pos):
        x, y = logical_pos
        return x * CELL_SIZE + PADDING, y * CELL_SIZE + PADDING
    
    def move_robot(self, robot_pos, target_pos, current_time, start_time, duration=1.0):
        proportion = min((current_time - start_time) / duration, 1.0)
        interpolated_x = robot_pos[0] + (target_pos[0] - robot_pos[0]) * proportion
        interpolated_y = robot_pos[1] + (target_pos[1] - robot_pos[1]) * proportion
        print("start_time: ", start_time, " current_time: ", current_time, "x: ", interpolated_x, " y: ", interpolated_y)

        return interpolated_x, interpolated_y

    def reset(self):
        self.x, self.y = self.start_position
        self.state = "idle"
        self.end_position = None
        self.shelf_assigned = None
        self.shelf_custody = False
        self.shelf_delivered = False

class Shelf:
    def __init__(self, shelf_id, x, y):
        self.id = shelf_id
        self.x = x
        self.y = y

class Instruction:
    def __init__(self, robot, target, start_time, instruction):
        self.robot = robot
        self.target = target
        self.start_time = start_time
        self.instruction = instruction

class Environment:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Inventory Management Environment")
        self.clock = pygame.time.Clock()
        self.robots = []
        self.shelves = []
        self.obstacles = []
        self.selected_robot = None
        self.running = True
        self.robot_speed_counter = 0

    def add_robot(self, x, y):
        robot_id = len(self.robots) + 1
        self.robots.append(Robot(robot_id, x, y))
    
    def add_shelf(self, x, y):
        shelf_id = len(self.shelves) + 1
        self.shelves.append(Shelf(shelf_id, x, y))

    def add_obstacle(self, x, y):
        self.obstacles.append((x, y))

    def draw_grid(self):
        self.screen.fill(WHITE)
        for r in range(GRID_ROWS + 1):
            pygame.draw.line(
                self.screen, BLACK,
                (PADDING, PADDING + r * CELL_SIZE), 
                (PADDING + GRID_COLS * CELL_SIZE, PADDING + r * CELL_SIZE), 1
            )
        for c in range(GRID_COLS + 1):
            pygame.draw.line(
                self.screen, BLACK,
                (PADDING + c * CELL_SIZE, PADDING), 
                (PADDING + c * CELL_SIZE, PADDING + GRID_ROWS * CELL_SIZE), 1
            )

    def draw_robots(self):
        for robot in self.robots:
            color = GREEN if robot.state == "active" else BLUE
            pygame.draw.circle(self.screen, color, (robot.display_x, robot.display_y), ROBOT_RADIUS)

    def instruct_robot(self, robot_id, target, start_time, instruction):
    # Check if robot_id exists??
        if robot_id <= len(self.robots):
            self.robots[robot_id - 1].instructions.append(Instruction(self.robots[robot_id - 1], target, start_time, instruction))

    def process_robot_instructions(self, current_time):
        for robot in self.robots:
            if robot.instructions:
                current_instruction = robot.instructions[0]
                if current_time >= current_instruction.start_time:
                    robot.display_x, robot.display_y = robot.move_robot(
                        robot.logical_to_display((robot.x, robot.y)),
                        robot.logical_to_display(current_instruction.target),
                        current_time,
                        current_instruction.start_time
                    )
                    # print(f"Logical Position: ({robot.x}, {robot.y}), Display Position: ({robot.display_x:.1f}, {robot.display_y:.1f}), Time: {current_time}")
                    if robot.has_reached_target(
                        (robot.display_x, robot.display_y),
                        robot.logical_to_display(current_instruction.target)
                    ):
                        robot.x, robot.y = current_instruction.target
                        robot.instructions.pop(0)
                            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def run(self):
        start_ticks = pygame.time.get_ticks()  # Record the start time
        while self.running:
            current_ticks = pygame.time.get_ticks()
            current_time = (current_ticks - start_ticks) / 1000  # Calculate elapsed time in seconds

            self.handle_events()
            self.process_robot_instructions(current_time)  # Process instructions based on the time
            self.draw_grid()
            self.draw_robots()
            pygame.display.flip()
            self.clock.tick(50)

# Main execution
environment = Environment()
environment.add_robot(1, 1)
# environment.add_robot(5, 5)
environment.instruct_robot(1, (2,1), 0, "move")
environment.instruct_robot(1, (3,1), 1, "move")
environment.instruct_robot(1, (4,1), 2, "move")
environment.instruct_robot(1, (5,1), 3, "move")
environment.instruct_robot(1, (5,2), 4, "move")
environment.instruct_robot(1, (5,3), 5, "move")
# environment.instruct_robot(2, (5,6), 1, "move")
# environment.instruct_robot(2, (5,7), 2, "move")
# environment.instruct_robot(2, (5,8), 3, "move")

# # Adding 5 new robots to the environment at different positions
# environment.add_robot(2, 2)  # Robot 2 at position (2, 2)
# environment.add_robot(3, 3)  # Robot 3 at position (3, 3)
# environment.add_robot(4, 4)  # Robot 4 at position (4, 4)
# environment.add_robot(5, 5)  # Robot 5 at position (5, 5)
# environment.add_robot(6, 6)  # Robot 6 at position (6, 6)

# # Instructing robots 2 to 6 to move 1 unit at a time in different directions
# # Robot 2 (starting at (2, 2))
# environment.instruct_robot(2, (3, 2), 0, "move")  # Move right (1 unit)
# environment.instruct_robot(2, (3, 3), 1, "move")  # Move up (1 unit)
# environment.instruct_robot(2, (2, 3), 2, "move")  # Move left (1 unit)
# environment.instruct_robot(2, (2, 2), 3, "move")  # Move down (1 unit)
# environment.instruct_robot(2, (3, 2), 4, "move")  # Move right again (1 unit)

# # Robot 3 (starting at (3, 3))
# environment.instruct_robot(3, (3, 4), 0, "move")  # Move up (1 unit)
# environment.instruct_robot(3, (4, 4), 1, "move")  # Move right (1 unit)
# environment.instruct_robot(3, (4, 3), 2, "move")  # Move down (1 unit)
# environment.instruct_robot(3, (3, 3), 3, "move")  # Move left (1 unit)
# environment.instruct_robot(3, (3, 4), 4, "move")  # Move up again (1 unit)

# # Robot 4 (starting at (4, 4))
# environment.instruct_robot(4, (5, 4), 0, "move")  # Move right (1 unit)
# environment.instruct_robot(4, (5, 5), 1, "move")  # Move up (1 unit)
# environment.instruct_robot(4, (6, 5), 2, "move")  # Move right (1 unit)
# environment.instruct_robot(4, (6, 4), 3, "move")  # Move down (1 unit)
# environment.instruct_robot(4, (5, 4), 4, "move")  # Move left again (1 unit)

# # Robot 5 (starting at (5, 5))
# environment.instruct_robot(5, (5, 6), 0, "move")  # Move up (1 unit)
# environment.instruct_robot(5, (6, 6), 1, "move")  # Move right (1 unit)
# environment.instruct_robot(5, (6, 5), 2, "move")  # Move down (1 unit)
# environment.instruct_robot(5, (5, 5), 3, "move")  # Move left (1 unit)
# environment.instruct_robot(5, (5, 6), 4, "move")  # Move up again (1 unit)

# # Robot 6 (starting at (6, 6))
# environment.instruct_robot(6, (7, 6), 0, "move")  # Move right (1 unit)
# environment.instruct_robot(6, (7, 7), 1, "move")  # Move up (1 unit)
# environment.instruct_robot(6, (6, 7), 2, "move")  # Move left (1 unit)
# environment.instruct_robot(6, (6, 6), 3, "move")  # Move down (1 unit)
# environment.instruct_robot(6, (7, 6), 4, "move")  # Move right again (1 unit)

environment.run()
pygame.quit()