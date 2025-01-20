import math
import pygame

class DDR:

    """A class representing a Differential Drive Robot (DDR).
    :param x: Initial x position of the agent.
    :param y: Initial y position of the agent.
    :param color: Agent render color.
    :param width: The given width of the agent.
    :param length: The given length of the agent.
    :param id: An unique id for the agent.
    """

    def __init__(self, x, y, color, width, length, id):
        self.id = id

        # Coordinates and dimensions
        self.x = x
        self.y = y
        self.width = width
        self.length = length

        # Wheel speeds
        self.vl = 0 # Left
        self.vr = 0 # Right
        self.vc = 0 # Center

        self.theta = 0 # Robot rotation theta

        # Wheel accelerations - NYI
        self.accl = 0 # Left
        self.accr = 0 # Right

        self.color = color

        self.score = 0
        # self.lrc = (WIDTH // 2, HEIGHT // 2)

        self.clamped = False
        self.dist = None
        self.last_dist = None
        self.facing = 0


    # Not yet implemented
    def accelerate(self, accs=(0, 0)):
        raise(NotImplementedError())
    
        '''
        self.accs = accs
        self.vl = max(-50, min(50, self.vl + dt * self.accs[0]))
        self.vr = max(-50, min(50, self.vr + dt * self.accs[1]))
        '''

    
    def set_id(self, n_agents):
        self.id = n_agents


    def move(self, vl, vr, dt, W, H):
        """Move the agent with the given speed and rotation."""
        self.vl = vl
        self.vr = vr
        self.vc = (vl + vr) / 2

        rotation = (self.vl - self.vr) / self.width  # Correct distance between wheel and center
        self.theta += rotation * dt
        if abs(self.theta) > 2*math.pi:
            self.theta = 0

        self.x += math.cos(self.theta) * self.vc * dt
        self.y += math.sin(self.theta) * self.vc * dt

        # Clamp position within bounds considering rotation
        self.clamp_position_with_rotation(W, H)

    def clamp_position_with_rotation(self, WIDTH, HEIGHT):
        """Clamp the agent's position within the screen bounds."""
        corners = self.get_rotated_corners()

        # Check for out-of-bounds corners
        for cx, cy in corners:
            if cx < 0:
                self.x += 0 - cx  # Push right
                self.clamped = True
            elif cx > WIDTH:
                self.x -= cx - WIDTH  # Push left
                self.clamped = True
            if cy < 0:
                self.y += 0 - cy  # Push down
                self.clamped = True
            elif cy > HEIGHT:
                self.y -= cy - HEIGHT  # Push up
                self.clamped = True

    def get_rotated_corners(self):
        """Calculate the screen positions of the agent's rotated corners."""
        half_size = self.width / 2
        corners = [
            (-half_size, -half_size),  # Top-left
            (half_size, -half_size),  # Top-right
            (half_size, half_size),   # Bottom-right
            (-half_size, half_size),  # Bottom-left
        ]

        rotated_corners = []
        for cx, cy in corners:
            # Apply rotation
            rotated_x = self.x + (cx * math.cos(self.theta) - cy * math.sin(self.theta))
            rotated_y = self.y + (cx * math.sin(self.theta) + cy * math.cos(self.theta))
            rotated_corners.append((rotated_x, rotated_y))

        return rotated_corners

    def draw(self, surface):
        """Draw the agent on the surface with rotation."""
        half_size = self.width / 2
        rect = pygame.Rect(self.x - half_size, self.y - half_size, self.width, self.width)
        rotated_surface = pygame.Surface((self.width, self.width), pygame.SRCALPHA)
        pygame.draw.rect(rotated_surface, self.color, (0, 0, self.width, self.width))
        rotated_surface = pygame.transform.rotate(rotated_surface, -math.degrees(self.theta))
        rotated_rect = rotated_surface.get_rect(center=rect.center)
        surface.blit(rotated_surface, rotated_rect.topleft)

    def update_objective_distance(self, objectives):
        obj = objectives[self.id]
        x_distance = self.x - obj[0]
        y_distance = self.y - obj[1]

        self.dist = x_distance, y_distance

