import pygame
import random
from a_star.a_star import a_star_search, heuristic
from constants import *

class Robot:
    def __init__(self, robot_id, x, y):
        self.id = robot_id
        self.x = x
        self.y = y
        self.state = "idle"
        self.start_position = (x, y)
        self.end_position = None
        self.shelf_assigned = None
        self.shelf_custody = False
        self.shelf_delivered = False

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.shelf_custody:
            self.shelf_assigned.x = self.x
            self.shelf_assigned.y = self.y

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
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))

    def draw_robots(self):
        for robot in self.robots:
            color = GREEN if robot.state == "active" else BLUE
            font_color = BLACK if color == GREEN else WHITE
            center_x = robot.x * GRID_SIZE + GRID_SIZE // 2
            center_y = robot.y * GRID_SIZE + GRID_SIZE // 2
            pygame.draw.circle(self.screen, color, (center_x, center_y), GRID_SIZE // 3 - 5)  # Reduced radius
            font = pygame.font.SysFont(None, 24)
            text = font.render(str(robot.id), True, font_color)
            text_rect = text.get_rect(center=(center_x, center_y))
            self.screen.blit(text, text_rect)

    def draw_shelves(self):
        for shelf in self.shelves:
            rect = pygame.Rect(shelf.x * GRID_SIZE, shelf.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, BLACK, rect, width=2)
            font = pygame.font.SysFont(None, 16)
            text = font.render(str(shelf.id), True, BLACK)
            self.screen.blit(text, (shelf.x * GRID_SIZE + GRID_SIZE - 12, shelf.y * GRID_SIZE + 2))

    def draw_obstacles(self):
        for (x, y) in self.obstacles:
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, RED, rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def move_robot_along_path(self, robot, path):
        if self.robot_speed_counter % ROBOT_SPEED == 0:
            if path:
                next_pos = path.pop(0)
                robot.move(next_pos[0] - robot.x, next_pos[1] - robot.y)
                robot.state = "active"
            else:
                robot.state = "idle"
        self.robot_speed_counter += 1

    def run(self):
        # Assign task to the first robot
        if self.robots:
            robot = self.robots[0]
            shelf = self.shelves[0]
            robot.shelf_assigned = shelf
            robot.end_position = (7, 7)  # Arbitrary end position

            # Calculate paths
            path_to_shelf = a_star_search((robot.x, robot.y), (shelf.x, shelf.y))
            path_to_goal = []

            if path_to_shelf:
                robot.state = "active"

        while self.running:
            self.handle_events()
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_obstacles()
            self.draw_shelves()
            self.draw_robots()

            # Robot automation
            if robot.state == "active":
                if path_to_shelf:
                    self.move_robot_along_path(robot, path_to_shelf)
                elif not robot.shelf_custody:
                    robot.shelf_custody = True
                    path_to_goal = a_star_search((robot.x, robot.y), robot.end_position)
                elif path_to_goal:
                    self.move_robot_along_path(robot, path_to_goal)
                else:
                    robot.shelf_custody = False
                    robot.shelf_delivered = True
                    robot.state = "idle"

            pygame.display.flip()
            self.clock.tick(10)

# Main execution
environment = Environment()

# Add robots, shelves, and obstacles
environment.add_robot(1, 1)
environment.add_shelf(5, 5)
environment.add_obstacle(6, 6)
environment.add_obstacle(4, 4)

# Run the environment simulation
environment.run()

pygame.quit()
