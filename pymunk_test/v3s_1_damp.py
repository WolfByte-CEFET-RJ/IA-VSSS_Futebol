"""
Velocidade e velocidade angular do robô diminuem baseado em um fator de atrito

* Deslizando muito
"""

import pygame
import pymunk
import pymunk.pygame_util

SCREEN_WIDTH = 1020
SCREEN_HEIGHT = 780
FPS = 60

BALL_MASS = 2
ROBOT_MASS = 20

BALL_ELASTICITY = 0.85
WALL_ELASTICITY = 0.2
ROBOT_ELASTICITY = 0.5

ROBOT_SIZE = 45
BALL_SIZE = 10

ROBOT_FRICTION = 0.9
ROBOT_ANGULAR_FRICTION = 0.8
WHEEL_SPEED = 20000

# Pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Create the screen
pygame.display.set_caption("V3S Simulação") # Set the window title
clock = pygame.time.Clock()

field_img = pygame.image.load('images\campo_VSSS.png')

# Pymunk Space
space = pymunk.Space()
space.damping = 0.5

#static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)
#space.gravity = (0, 1000)

def create_walls(shape):
    for i in range(len(shape)):
        wall_shape = pymunk.Segment(space.static_body, (shape[i]), (shape[i-1]), radius=2)
        wall_shape.elasticity = WALL_ELASTICITY
        wall_shape.friction = 0.5
        space.add(wall_shape)

def create_ball(pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, BALL_SIZE)
    shape.mass = BALL_MASS
    shape.elasticity = BALL_ELASTICITY

    space.add(body, shape)
    return shape

def create_robot(pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Poly.create_box(body, (ROBOT_SIZE, ROBOT_SIZE))
    shape.mass = ROBOT_MASS
    shape.elasticity = ROBOT_ELASTICITY
    space.add(body, shape)

    return shape

wall = create_walls(((102,0),(918,0),(960,42),(960,270),(1020,270),(1020,510),(960,510),(960,738),(918,780),(102,780),(60,738),(60,510),(0,510),(0,270),(60,270),(60,42)))
ball = create_ball((SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
robot = create_robot((SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))

create_robot((200, 500))

def game():
    pygame.init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_r]:
            robot.body.position = (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2)
            robot.body.velocity = (0, 0)
            robot.body.angular_velocity = 0
            robot.body.angle = 0

        robot.body.velocity *= ROBOT_FRICTION
        robot.body.angular_velocity *= ROBOT_ANGULAR_FRICTION
        # Apply wheel forces on the Differential Drive Robot (DDR)
        left_speed = (int(keys[pygame.K_e]) - int(keys[pygame.K_a])) * WHEEL_SPEED
        right_speed = (int(keys[pygame.K_q]) - int(keys[pygame.K_d])) * WHEEL_SPEED

        robot.body.apply_force_at_local_point((right_speed, 0), (0, ROBOT_SIZE/2))
        robot.body.apply_force_at_local_point((left_speed, 0), (0, -ROBOT_SIZE/2))

        # Draw Images
        #screen.fill((255, 255, 255))
        screen.blit(field_img, (0,0))
        space.debug_draw(draw_options)

        pygame.display.update()
        clock.tick(FPS)
        space.step(1/FPS)

game()