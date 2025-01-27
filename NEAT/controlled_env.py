import pygame
import os
import random

import math
import time

pygame.init()

# GCs

SCREEN_HEIGHT = 780
SCREEN_WIDTH = 1020

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ROBOT = pygame.Rect(400, 400, 45, 45)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 127, 0)

# Robot
square_size = 45
wheel_speed = 35

# Speed increment for wheels
speed_increment = 10

# Field
field = pygame.image.load(os.path.join('images', 'campo_VSSS.png'))

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
    left_speed = (int(keys[pygame.K_e]) - int(keys[pygame.K_a])) * wheel_speed
    right_speed = (int(keys[pygame.K_q]) - int(keys[pygame.K_d])) * wheel_speed
    
    def pos_angle(angle):
        if angle < 0:
            angle = 360 + angle
        return angle

    for agent in agents:
        agent.move(left_speed, right_speed, dt, SCREEN_WIDTH, SCREEN_HEIGHT)
        agent.update_objective_distance(objectives)
        ag = pos_angle(math.degrees(math.atan2(agent.dist[1], agent.dist[0])) - 180)
        angle_diff = pos_angle(math.degrees(agent.theta)) - ag
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        elif angle_diff < -180:
            angle_diff = 360 + angle_diff
        if time.time() - timer >= 1:
            timer = time.time()
            print('-' * 30)
            print(f"ROBOT ANGLE: {pos_angle(math.degrees(agent.theta))}\n" + \
                  f"ANGLE WITH OBJECTIVE: {ag}\nDIFF: {angle_diff}")


        # Check for collisions
        if check_collision(agent, objectives[agent.id]):
            objectives[agent.id] = spawn_objective()
            agent.score += 1

        
        
        
        '''if ge[i].fitness <= -1:
            agents.pop(i)'''

    # Draw everything
    #SCREEN.fill(WHITE)
    SCREEN.blit(field, (0, 0))
    for agent in agents:
        agent.draw(SCREEN)
        pygame.draw.circle(SCREEN, agent.color, objectives[agent.id], 12, width=3)
        pygame.draw.line(SCREEN, agent.color, objectives[agent.id], (agent.x, agent.y))

    # Boardas do campo
    # TODO: Gerar Colisão
    # Apenas gerando os poligonos como exemplo atualmente
    pygame.draw.polygon(SCREEN, ORANGE, ((0,0),(102,0),(60,42),(60,270),(0,270)))
    pygame.draw.polygon(SCREEN, ORANGE, ((0,510),(60,510),(60,738),(102,780),(0,780)))
    pygame.draw.polygon(SCREEN, ORANGE, ((918,0),(1020,0),(1020,270),(960,270),(960,42)))
    pygame.draw.polygon(SCREEN, ORANGE, ((960,510),(1020,510),(1020,780),(918,780),(960,738)))
    #pygame.draw.polygon(SCREEN, ORANGE, ((102,0),(918,0),(960,42),(960,270),(1020,270),(1020,510),(960,510),(960,738),(918,780),(102,780),(60,738),(60,510),(0,510),(0,270),(60,270),(60,42)))

    pygame.display.flip()
    clock.tick(60)

    # End of generation cleanup
    pygame.display.update()