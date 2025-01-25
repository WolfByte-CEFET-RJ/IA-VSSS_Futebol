import pygame
import math
from constants import ROBOT_SIZE, WIDTH, HEIGHT, SCALE

class Robot(pygame.sprite.Sprite):
    def __init__(self, x, y, color=(0, 0, 255), size=ROBOT_SIZE):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0  # Robot's direction
        self.speed_left = 0
        self.speed_right = 0

    def update(self):
        self.angle += (self.speed_right - self.speed_left) * 0.05
        self.x += math.cos(self.angle) * (self.speed_left + self.speed_right) * 0.5 * SCALE
        self.y += math.sin(self.angle) * (self.speed_left + self.speed_right) * 0.5 * SCALE

        # Constrain the robot's position to the screen boundaries
        half_size = ROBOT_SIZE / 2
        self.x = max(half_size, min(WIDTH * SCALE - half_size, self.x))
        self.y = max(half_size, min(HEIGHT * SCALE - half_size, self.y))


    def distance_to(self, target):
        return math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)

    def draw(self, screen):
        robot_surface = pygame.Surface((ROBOT_SIZE, ROBOT_SIZE), pygame.SRCALPHA)
        robot_surface.fill(self.color)
        rotated_surface = pygame.transform.rotate(robot_surface, -math.degrees(self.angle))
        rect = rotated_surface.get_rect(center=(self.x / SCALE, self.y / SCALE))  # Reverse scaling
        screen.blit(rotated_surface, rect.topleft)

        # Draw a direction line
        dx = math.cos(self.angle) * (ROBOT_SIZE // 2)
        dy = math.sin(self.angle) * (ROBOT_SIZE // 2)
        pygame.draw.line(screen, (0, 0, 0), (self.x / SCALE, self.y / SCALE), ((self.x + dx) / SCALE, (self.y + dy) / SCALE), 2)





