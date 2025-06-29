import pygame

class StandardEnv:
    def __init__(self, w=900, h=780):
        self.w, self.h = w, h
        self.screen = pygame.display.set_mode((self.w, self.h))
    
    def get_screen(self):
        return self.screen

    