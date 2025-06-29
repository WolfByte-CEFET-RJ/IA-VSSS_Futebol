import pygame
import pymunk
import math
import ctypes
import configparser
import os

from sim_utils import to_scale as ts
from sim_utils import interrupt, Colors

from agent import DDR
from props import Ball

def draw_boundaries(screen, static_lines):
    for line in static_lines:
        pygame.draw.line(screen, (255, 255, 255), line.a, line.b, 2)

def draw_agents(screen, agents):
    for agent in agents:
        agent.draw(screen)

def draw_props(screen, props):
    for prop in props:
        prop.draw(screen)

def hit_prop(arbiter, space, data):
    agent_shape, ball_shape = arbiter.shapes  # Get colliding objects

    direction = ball_shape.body.position - agent_shape.body.position
    direction = direction.normalized()

    force = 10  # Adjust for desired effect
    ball_shape.body.apply_impulse_at_local_point(direction * force)

    return True  # Allows Pymunk to continue handling collision

def make_field_bounds():
    bt = ts(1)
    goals = [
        pymunk.Segment(space.static_body, ts((40, 110)), ts((20, 110)), bt),
        pymunk.Segment(space.static_body, ts((20, 110)), ts((20, 190)), bt),
        pymunk.Segment(space.static_body, ts((20, 190)), ts((40, 190)), bt),
        pymunk.Segment(space.static_body, ts((WIDTH-40, 110)), ts((WIDTH-20, 110)), bt),
        pymunk.Segment(space.static_body, ts((WIDTH-20, 110)), ts((WIDTH-20, 190)), bt),
        pymunk.Segment(space.static_body, ts((WIDTH-20, 190)), ts((WIDTH-40, 190)), bt)
        ]
    
    borders = [
        pymunk.Segment(space.static_body, ts((40, 20)), ts((40, 110)), bt),  
        pymunk.Segment(space.static_body, ts((40, 20)), ts((WIDTH-40, 20)), bt),
        pymunk.Segment(space.static_body, ts((WIDTH-40, 20)), ts((WIDTH-40, 110)), bt),
        pymunk.Segment(space.static_body, ts((WIDTH-40, HEIGHT-20)), ts((WIDTH-40, HEIGHT-110)), bt),
        pymunk.Segment(space.static_body, ts((40, HEIGHT-20)), ts((WIDTH-40, HEIGHT-20)), bt),
        pymunk.Segment(space.static_body, ts((40, HEIGHT-20)), ts((40, HEIGHT-110)), bt)
        ]
    corners = [
        pymunk.Segment(space.static_body, ts((40, 34)), ts((54, 20)), bt),
        pymunk.Segment(space.static_body, ts((WIDTH-40, 34)), ts((WIDTH-54, 20)), bt),
        pymunk.Segment(space.static_body, ts((WIDTH-40, HEIGHT-34)), ts((WIDTH-54, HEIGHT-20)), bt),
        pymunk.Segment(space.static_body, ts((40, HEIGHT-34)), ts((54, HEIGHT-20)), bt)
    ]
    
    return goals + borders + corners

# Colors
colors = Colors()

# Set DPI Awareness  (Windows 10 and 8)
errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)

SIM_CONFIG = configparser.ConfigParser()
SIM_CONFIG.read(r'NEAT\simulation_config.ini')

print("Sections found:", SIM_CONFIG.sections())

os.environ['V3S_SIM_DPI_SCALING_FACTOR'] = SIM_CONFIG['SCALING']['dpi_scaling_factor']
os.environ['V3S_SIM_PSI_SCALING_FACTOR'] = SIM_CONFIG['SCALING']['psi_scaling_factor']

WIDTH = SIM_CONFIG.getint('ENVIRONMENT', 'env_width')
HEIGHT = SIM_CONFIG.getint('ENVIRONMENT', 'env_height')

AGT_WID = SIM_CONFIG.getint('AGENT', 'agent_width')
AGT_LEN = SIM_CONFIG.getint('AGENT', 'agent_length')
AGT_SPD = SIM_CONFIG.getint('AGENT', 'agent_speed')

print(WIDTH, HEIGHT)

#interrupt()

space = pymunk.Space()
space.gravity = 0, 0
space.iterations = 60
space.collision_bias = 0.0000001
space.collision_slop = 1



static_lines = make_field_bounds()

for line in static_lines:
    line.collision_type = 3  
    line.elasticity = .2
    line.friction = .2  
    space.add(line)

pygame.init()

screen = pygame.display.set_mode(ts((WIDTH, HEIGHT)))  
background_color = (30, 30, 30)
clock = pygame.time.Clock()
dt = 0.1

# Prop Initialization
props = [Ball(ts(WIDTH) // 2, ts(HEIGHT) // 2, int(ts(4.72/2)), 46, space, colors.ORANGE)]

# Agent Initialization
agent_info = [{'pos': ts((115, 70)), 'role': colors.RED, 'team': colors.CYAN, 'id': 0},
              {'pos': ts((115, 150)), 'role': colors.GREEN, 'team': colors.CYAN, 'id': 1},
              {'pos': ts((115, HEIGHT-70)), 'role': colors.PINK, 'team': colors.CYAN, 'id': 2},
              {'pos': ts((WIDTH-115, 70)), 'role': colors.RED, 'team': colors.YELLOW, 'id': 3},
              {'pos': ts((WIDTH-115, 150)), 'role': colors.GREEN, 'team': colors.YELLOW, 'id': 4},
              {'pos': ts((WIDTH-115, HEIGHT-70)), 'role': colors.PURPLE, 'team': colors.YELLOW, 'id': 5},
              ]

agents = [DDR(a['pos'][0], a['pos'][1], (a['team'], a['role']), ts(AGT_WID), ts(AGT_LEN), a['id'], space, 200) for a in agent_info]

agent_collision_type = 1
prop_collision_type = 2

for agent in agents:
    agent.shape.collision_type = agent_collision_type
for prop in props:
    prop.shape.collision_type = prop_collision_type

# Add collision handler
agent_ball_handler = space.add_collision_handler(agent_collision_type, prop_collision_type)
agent_ball_handler.post_solve = hit_prop  # Calls hit_ball() after a collision is resolved

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update agents and check collisions
    keys = pygame.key.get_pressed()
    # Interpret NN output for agent movement
    vl = 0
    vr = 0
    if keys[pygame.K_a]:
        vl = AGT_SPD
    if keys[pygame.K_d]:
        vr = AGT_SPD
    if keys[pygame.K_z]:
        vl = -AGT_SPD
    if keys[pygame.K_c]:
        vr = -AGT_SPD

    if vl or vr:
        print("I should be moving.")
        agents[0].move(ts(vl), ts(vr), dt, ts(WIDTH), ts(HEIGHT))

    screen.fill((30, 30, 30))  # Background color
    draw_boundaries(screen, static_lines)
    draw_agents(screen, agents)
    draw_props(screen, props)
    
    pygame.display.flip()
    dt = clock.tick(60) / 1000  # Convert ms to seconds
    for _ in range(900):
        space.step(dt / 900)  # ✅ Prevents objects from skipping collisions

pygame.quit()