import pygame
import neat
import random
import numpy as np
import math
from robot import Robot
import time
from constants import WIDTH, HEIGHT, GENERATION_DURATION, FPS, TARGET_RADIUS, SCALE
from target import Target
from utils import positive_angle, distance, hsv2rgb

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEAT Robot Simulation")
clock = pygame.time.Clock()

# Control how many robots to render (for testing purposes)
RENDER_LIMIT = 10  # Render only the first 10 robots, adjust as needed

def eval_genomes(genomes, config):
    robots = []
    targets = []
    nets = []
    ge = []
    best = None  # Track the best genome of the current generation

    # Initialize all genome fitness values to 0.0
    for _, genome in genomes:
        genome.fitness = 0.0  # Ensure fitness is always initialized

    num_genomes = min(len(genomes), RENDER_LIMIT)
    hues = np.linspace(0, 1, num_genomes, endpoint=False)  # Full range of hues (0 to 1)

    for genome_id, genome in genomes[:RENDER_LIMIT]:  # Limit genomes to RENDER_LIMIT
        color = hsv2rgb(hues[len(robots) % num_genomes], 1, 1)  # Generate a color for this genome
        robot = Robot(WIDTH // 2 * SCALE, HEIGHT // 2 * SCALE, color)  # Pass the color to the robot
        target = Target(robot.color)  # Pass the color to the target
        robots.append(robot)
        targets.append(target)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        ge.append(genome)


    running = True
    start_time = time.time()
    while running:
        timer = time.time() - start_time
        if timer >= GENERATION_DURATION:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # Background color

        for i, robot in enumerate(robots):
            target = targets[i]

            # Compute distance and angle to the target
            dist = robot.distance_to(target)
            angle = math.atan2(target.y - robot.y, target.x - robot.x) - robot.angle

            # Normalize inputs
            dist /= math.sqrt(WIDTH**2 + HEIGHT**2)  # Normalize distance
            angle = positive_angle(angle) / math.pi  # Normalize angle to [0, 1]

            # Neural network output
            output = nets[i].activate((dist, angle))

            # Scale and apply output to robot's motors
            robot.speed_left = (output[0] * 2 - 1) * 2
            robot.speed_right = (output[1] * 2 - 1) * 2

            robot.update()

            # Reward fitness based on proximity to the target
            previous_fitness = ge[i].fitness
            ge[i].fitness += (1 - dist) - previous_fitness  # Reward for getting closer

            # Check if the robot reaches the target
            if robot.distance_to(target) < TARGET_RADIUS:
                ge[i].fitness += 100  # Reward for reaching target
                targets[i] = Target(robot.color)  # Spawn a new target with the same color


            # Track the best genome of the generation
            if best is None or ge[i].fitness > (best.fitness or 0):
                best = ge[i]

            #best_genome = max(ge, key=lambda genome: genome.fitness, default=None)

            # Draw robot and target
            robot.draw(screen)
            target.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    print("Best Genome Fitness:", best.fitness if best else "No best genome found.")





def run(config_path):
    # Load NEAT configuration
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Set up NEAT population
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    # Run the simulation for 50 generations
    population.run(eval_genomes, 50)

if __name__ == "__main__":
    config_path = "NEAT/config-paco.txt"  # Path to NEAT config file
    run(config_path)
    pygame.quit()
