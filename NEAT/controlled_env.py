import pygame
import os
import random
import sys

import math
import time

pygame.init()

# GCs

SCREEN_HEIGHT = 780
SCREEN_WIDTH = 900

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ROBOT = pygame.Rect(400, 400, 45, 45)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 127, 0)

# Square properties
square_size = 50
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Initial position
angle = 0  # Rotation in radians

# Wheel speeds
left_wheel_speed = 0
right_wheel_speed = 0

# Speed increment for wheels
speed_increment = 10

# Time properties
clock = pygame.time.Clock()
dt = 0.1  # Time step

# Simulation parameters
wheel_base = square_size  # Distance between wheels
n_agents = 10

# Agents and objectives
agents = []
objectives = {}

from agent import DDR

agents.append(DDR(300, 300, (0, 0, 0), 45, 45, 0))

def spawn_objective():
    """Spawn an objective at a random position."""
    # while math.sqrt((x - WIDTH/2)**2 + (y - HEIGHT/2)**2) < 100:
    x = random.randint(12, SCREEN_WIDTH - 12)
    y = random.randint(12, SCREEN_HEIGHT - 12)
    return (x, y)

def check_collision(agent, objective):
    """Check if the agent has collided with its objective."""
    ax, ay = agent.x, agent.y
    ox, oy = objective
    distance = math.sqrt((ax - ox)**2 + (ay - oy)**2)
    return distance < (agent.width / 2 + 12)

# Initialize the first objective
objective_position = spawn_objective()

running = True
timer = time.time()

# Assign objectives
for agent in agents:
    objectives[agent.id] = spawn_objective()
    agent.update_objective_distance(objectives)
    agent.last_dist = math.sqrt(agent.dist[0] ** 2 + agent.dist[1] ** 2)

while running:
    # Check if generation duration is over
    last_time = math.floor(timer)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Update agents and check collisions
    keys = pygame.key.get_pressed()
    # Interpret NN output for agent movement
    left_speed, right_speed = 0, 0
    if keys[pygame.K_a]:
        left_speed += 25
    elif keys[pygame.K_z]:
        left_speed -= 25
    if keys[pygame.K_d]:
        right_speed += 25
    elif keys[pygame.K_c]:
        right_speed -= 25
    
    def pos_angle(angle):
        if angle < 0:
            angle = 360 + angle
        return angle

    for agent in agents:
        agent.move(left_speed, right_speed, dt, SCREEN_WIDTH, SCREEN_HEIGHT)
        agent.update_objective_distance(objectives)
        ag = pos_angle(math.degrees(math.atan2(agent.dist[1], agent.dist[0])) - 180)
        if time.time() - timer >= 1:
            timer = time.time()
            print('-' * 30)
            print(f"ROBOT ANGLE: {pos_angle(math.degrees(agent.theta))}\n" + \
                  f"ANGLE WITH OBJECTIVE: {ag}\nDIFF: {pos_angle(math.degrees(agent.theta)) - ag}")


        # Check for collisions
        if check_collision(agent, objectives[agent.id]):
            objectives[agent.id] = spawn_objective()
            agent.score += 1

        
        
        
        '''if ge[i].fitness <= -1:
            agents.pop(i)'''

    # Draw everything
    SCREEN.fill(WHITE)
    for agent in agents:
        agent.draw(SCREEN)
        pygame.draw.circle(SCREEN, agent.color, objectives[agent.id], 12, width=3)
        pygame.draw.line(SCREEN, agent.color, objectives[agent.id], (agent.x, agent.y))


    pygame.display.flip()
    clock.tick(60)

    # End of generation cleanup
    pygame.display.update()