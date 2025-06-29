import pygame
import pymunk
from sim_utils import Colors

colors = Colors()

class Ball:
    def __init__(self, x, y, radius, mass, space, color=(255, 255, 255)):
        self.radius = radius
        self.color = color

        # Create body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y

        # Create shape
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.7  # Bounciness
        self.shape.friction = 0.1    # Friction
        self.body.damping = 0.99
        space.add(self.body, self.shape)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.body.position.x), int(self.body.position.y)), self.radius)