import pygame
import neat
import random
import math
from constants import WIDTH, HEIGHT, SCALE, TARGET_RADIUS, ROBOT_SIZE, WHITE, RED, BLUE, ORANGE
FPS = 60

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NEAT Robot Simulation")
clock = pygame.time.Clock()

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # Facing direction in radians
        self.speed_left = 0
        self.speed_right = 0

    def update(self):
        # Calculate linear and angular velocities
        linear_velocity = (self.speed_left + self.speed_right) / 2
        angular_velocity = (self.speed_right - self.speed_left) / ROBOT_SIZE

        # Update angle and position
        self.angle += angular_velocity
        self.x += linear_velocity * math.cos(self.angle)
        self.y += linear_velocity * math.sin(self.angle)

        # Keep the robot within screen bounds
        self.x = max(0, min(SCREEN_WIDTH, self.x))
        self.y = max(0, min(SCREEN_HEIGHT, self.y))

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, pygame.Rect(self.x - ROBOT_SIZE // 2, self.y - ROBOT_SIZE // 2, ROBOT_SIZE, ROBOT_SIZE))

    def distance_to(self, target):
        return math.sqrt((self.x - target.x)**2 + (self.y - target.y)**2)

    def angle_to(self, target):
        return math.atan2(target.y - self.y, target.x - self.x) - self.angle

class Target:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, self.y), TARGET_RADIUS)

def eval_genomes(genomes, config):
    robots = []
    targets = []
    nets = []
    ge = []

    # Initialize robots and NEAT
    for genome_id, genome in genomes:
        x, y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
        robots.append(Robot(x, y))
        targets.append(Target())
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        ge.append(genome)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        for i, robot in enumerate(robots):
            if not running:
                break

            target = targets[i]

            # Calculate inputs for NEAT
            distance = robot.distance_to(target)
            angle = robot.angle_to(target)

            # Normalize inputs
            distance /= math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)
            angle /= math.pi

            # Get outputs from NEAT
            output = nets[i].activate((distance, angle))

            # Set robot speeds
            robot.speed_left = output[0] * 2 - 1  # Scale to [-1, 1]
            robot.speed_right = output[1] * 2 - 1

            robot.update()

            # Calculate fitness
            previous_distance = ge[i].fitness
            ge[i].fitness += (1 - robot.distance_to(target)) - previous_distance

            # Check if target is reached
            if robot.distance_to(target) < TARGET_RADIUS:
                ge[i].fitness += 100  # Reward for reaching target
                targets[i] = Target()  # Spawn a new target

            robot.draw(screen)
            target.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    population.run(eval_genomes, 50)

if __name__ == "__main__":
    config_path = "NEAT/config-feedforward.txt"
    run(config_path)
