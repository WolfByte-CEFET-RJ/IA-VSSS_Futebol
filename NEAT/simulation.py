import pygame
import math
import neat
import random
import time
import colorsys
import numpy

import agent as AGT

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Agents and Objectives")


# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 127, 0)

# Agent properties
agent_size = 45

# Objective properties
objective_radius = 12

# Time properties
clock = pygame.time.Clock()
dt = 0.1  # Time step

gen = 0 # Generation Counter

def positive_angle(angle):
    '''Converts an angle in degrees to its positive identity.
    
    :param angle: The angle to convert to positive.
    '''
    if angle < 0:
        angle = 360 + angle
    return angle


def spawn_objective():
    """Spawn an objective at a random position."""
    x = random.choice([i for i in range(0, WIDTH) if not ((WIDTH / 2) - 100 > i > (WIDTH / 2) + 100)])
    y = random.choice([i for i in range(0, HEIGHT) if not ((HEIGHT / 2) - 100 > i > (HEIGHT / 2) + 100)])

    return (x, y)

def check_collision(agent, objective):
    """Check if the agent has collided with its objective."""
    ax, ay = agent.x, agent.y
    ox, oy = objective
    distance = math.sqrt((ax - ox)**2 + (ay - oy)**2)
    return distance < (agent_size / 2 + objective_radius)


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 1000)

def check_end(s, e, sim_time=5):
    if (e - s) >= sim_time:
        return True
    return False

def remove(index):
    agents.pop(index)

def clear():
    while agents:
        agents.pop(0)

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def draw_scoreboard(screen, agents, ge, time_seconds, time_max, gen):
    """Draw a scoreboard with agent colors and scores."""
    font = pygame.font.Font(None, 13)  # Default font, size 24
    time_font = pygame.font.Font(None, 25)
    x_offset = 10  # Starting x-position for the scoreboard
    y_offset = 10  # Starting y-position for the scoreboard
    square_size = 13  # Size of the color square
    spacing = 2  # Space between squares and text

    for i, agent in enumerate(agents):
        # Draw the color square
        pygame.draw.rect(screen, agent.color, (x_offset, y_offset, square_size, square_size))

        # Render the score as text
        render_text = f"{ge[i].fitness:.1f}"
        if agent.score > 0:
            render_text += f" - SCORED {agent.score}!"
        score_text = font.render(render_text, True, (255, 255, 255))
        screen.blit(score_text, (x_offset + square_size + spacing, y_offset))
        print(time_max - time_seconds)
        time_text = time_font.render(f"Gen. {gen} - Timer: " + str(time_max - time_seconds), True, (127, 127, 127))
        screen.blit(time_text, (WIDTH - 150, HEIGHT - 50))

        # Move to the next line for the next agent
        y_offset += square_size + spacing

def eval_genomes(genomes, config):
    global dt, agents, objectives, ge, nets, gen

    gen += 1

    # Timer variables
    generation_duration = 6  # Time in seconds per generation
    start_time = time.time()

    # Initialize agents, genomes, and neural networks
    agents = []
    objectives = {}
    ge = []
    nets = []
    h = 0
    for genome_id, genome in genomes:
        
        hues = numpy.linspace(0, 0.9, len(genomes))
 
        agents.append(AGT.DDR(WIDTH // 2, HEIGHT // 2, hsv2rgb(hues[h], 1, 1), agent_size, agent_size, len(agents)))
        h += 1
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    # Assign objectives
    for agent in agents:
        objectives[agent.id] = spawn_objective()
        agent.update_objective_distance(objectives)
        agent.last_dist = math.sqrt(agent.dist[0] ** 2 + agent.dist[1] ** 2)

    running = True
    timer = 0
    while running:
        # Check if generation duration is over
        last_time = math.floor(timer)
        timer = time.time() - start_time

        if last_time != math.floor(timer):
            for i, agent in enumerate(agents):
                '''ge[i].fitness -= 100 - agent.speeds[0] - agent.speeds[1]'''
            print(f"{math.floor(timer)}/{generation_duration} seconds elapsed.")

            
        
        if timer >= generation_duration:
            break  # Exit the loop to move to the next generation

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Update agents and check collisions
        for i, agent in enumerate(agents):

            agent.update_objective_distance(objectives)
            dist_to_obj = math.sqrt(agent.dist[0] ** 2 + agent.dist[1] ** 2)
        
            if dist_to_obj < agent.last_dist:
                ge[i].fitness += 5  # Reward moving closer
            else:
                ge[i].fitness -= 1  # Penalize moving farther
            agent.last_dist = dist_to_obj

            if abs(agent.vl - agent.vr) < 5:
                ge[i].fitness -= 1  # Penalty for low movement

            if abs(agent.last_dist - dist_to_obj) < 0.1:  # Minimal progress
                ge[i].fitness -= 5  # Penalize stagnation
            
            ag = positive_angle(math.degrees(math.atan2(agent.dist[1], agent.dist[0])) - 180)

            phi = abs(ag - positive_angle(math.degrees(agent.theta)))
            output = nets[i].activate((
                objectives[agent.id][0] / WIDTH,  # X distance normalized
                objectives[agent.id][1] / HEIGHT,  # Y distance normalized
                phi / 360
            ))

            # Interpret NN output for agent movement
            if output[0] > 0.5:
                left_speed = 45
            else:
                left_speed = -45

            if output[1] > 0.5:
                right_speed = 45
            else:
                right_speed = -45
            
            agent.move(left_speed, right_speed, dt, WIDTH, HEIGHT)

            if agent.clamped:
                ge[i].fitness -= 2
                agent.clamped = False

            # Check for collisions
            if check_collision(agent, objectives[agent.id]):
                objectives[agent.id] = spawn_objective()
                ge[i].fitness += 5000  # Reward the genome for reaching the objective
                agent.score += 1

            
            
            
            '''if ge[i].fitness <= -1:
                agents.pop(i)'''

        # Draw everything
        screen.fill((0, 0, 0))
        for agent in agents:
            agent.draw(screen)
            pygame.draw.circle(screen, agent.color, objectives[agent.id], objective_radius, width=3)
            pygame.draw.line(screen, agent.color, objectives[agent.id], (agent.x, agent.y))

        draw_scoreboard(screen, agents, ge, last_time, generation_duration, gen)

        pygame.display.flip()
        clock.tick(60)

    # End of generation cleanup
    pygame.display.update()

if __name__ == '__main__':
    run(r'NEAT\config.txt')
    pygame.quit()