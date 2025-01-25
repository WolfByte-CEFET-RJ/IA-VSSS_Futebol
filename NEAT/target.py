import random
import pygame
from constants import TARGET_RADIUS, SCALE, WIDTH, HEIGHT

class Target:
    def __init__(self,color):
        self.x = random.randint(int(20 * SCALE), int((WIDTH - 20) * SCALE))
        self.y = random.randint(int(20 * SCALE), int((HEIGHT - 20) * SCALE))
        self.color = color

    def update_position(self):
        '''Randomly spawn the target at a new position.'''
        self.x = random.randint(0, 900)
        self.y = random.randint(0, 780)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x / SCALE), int(self.y / SCALE)), TARGET_RADIUS)

