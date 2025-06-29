import math
import pygame
import numpy as np
import pymunk

STANDARD_ORANGE = '#ff9700'
STANDARD_WHITE = '#ffffff'

STANDARD_COLORS = (STANDARD_ORANGE, STANDARD_WHITE)
class _DDR:

    """A class representing a Differential Drive Robot (DDR).
    :param x: Initial x position of the agent.
    :param y: Initial y position of the agent.
    :param color: Agent render color.
    :param width: The given width of the agent.
    :param length: The given length of the agent.
    :param id: An unique id for the agent.
    """

    def __init__(self, x, y, color, width, length, id, sprite_id=0):
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
        self.image = pygame.image.load(rf'NEAT\sprites\robot{sprite_id}.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, length))
        self.image = pygame.transform.rotate(self.image, 90)
        self.recolor_surface(self.color, '#777777')


    # Not yet implemented
    def accelerate(self, accs=(0, 0)):
        raise(NotImplementedError())
    
        '''
        self.accs = accs
        self.vl = max(-50, min(50, self.vl + dt * self.accs[0]))
        self.vr = max(-50, min(50, self.vr + dt * self.accs[1]))
        '''

    def recolor_surface(self, team_color, role_color):
        # Convert the surface to a 3D numpy array (RGB format)
        pixel_array = pygame.surfarray.pixels3d(self.image)
        
        # Iterate over the color map and replace colors
        for old_color, new_color in zip(STANDARD_COLORS, (team_color, role_color)):
            # Convert HEX to RGB
            old_rgb = pygame.Color(old_color).r, pygame.Color(old_color).g, pygame.Color(old_color).b
            new_rgb = pygame.Color(new_color).r, pygame.Color(new_color).g, pygame.Color(new_color).b
            
            # Find and replace matching pixels
            mask = np.all(pixel_array == old_rgb, axis=-1)
            pixel_array[mask] = new_rgb
        
        del pixel_array  # Unlock the surface
    
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
        '''half_size = self.width / 2
        
        rotated_surface = pygame.Surface((self.width, self.width), pygame.SRCALPHA)
        pygame.draw.rect(rotated_surface, self.color, (0, 0, self.width, self.width))
        rotated_surface = pygame.transform.rotate(rotated_surface, -math.degrees(self.theta))
        rotated_rect = rotated_surface.get_rect(center=rect.center)
        surface.blit(rotated_surface, rotated_rect.topleft)'''
        """Draw the agent on the surface with rotation."""

       

        # Rotate the image around its center
        rotated_surface = pygame.transform.rotate(self.image, -math.degrees(self.theta))

        # Get the new rectangle for the rotated surface
        rect = rotated_surface.get_rect(center = (self.x, self.y))
        # Blit the rotated image onto the surface
        surface.blit(rotated_surface, rect.topleft)
            

    def update_objective_distance(self, objectives):
        obj = objectives[self.id]
        x_distance = self.x - obj[0]
        y_distance = self.y - obj[1]

        self.dist = x_distance, y_distance


class DDR:

    """A class representing a Differential Drive Robot (DDR).
    :param x: Initial x position of the agent.
    :param y: Initial y position of the agent.
    :param color: Agent render color.
    :param width: The given width of the agent.
    :param length: The given length of the agent.
    :param id: An unique id for the agent.
    """

    def __init__(self, x, y, colors, width, length, id, space, mass=1, sprite_id=0):
        self.id = id

        # Coordinates and dimensions
        self.width = width
        self.length = length
        self.mass = mass

        # RigidBody
        self.body = pymunk.Body(mass, pymunk.moment_for_box(mass, (width, length)))
        self.body.position = x, y
        self.shape = pymunk.Poly.create_box(self.body, (width, length))
        self.shape.elasticity = 0.1
        space.add(self.body, self.shape)

        # Wheel speeds
        self.vl = 0 # Left
        self.vr = 0 # Right
        self.vc = 0 # Center

        # Wheel accelerations - NYI
        self.accl = 0 # Left
        self.accr = 0 # Right

        self.colors = {'team': colors[0], 'role': colors[1]}

        self.score = 0
        # self.lrc = (WIDTH // 2, HEIGHT // 2)

        self.clamped = False
        self.dist = None
        self.last_dist = None
        self.facing = 0
        self.image = pygame.image.load(rf'NEAT\sprites\robot{sprite_id}.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, length))
        self.image = pygame.transform.rotate(self.image, 90)
        self.recolor_surface(self.colors['team'], self.colors['role'])

    def get_position(self):
        return self.body.position
    
    def get_angle(self):
        return self.body.angle
    
    # Not yet implemented
    def accelerate(self, accs=(0, 0)):
        raise(NotImplementedError())
    
        '''
        self.accs = accs
        self.vl = max(-50, min(50, self.vl + dt * self.accs[0]))
        self.vr = max(-50, min(50, self.vr + dt * self.accs[1]))
        '''

    def recolor_surface(self, team_color, role_color):
        # Convert the surface to a 3D numpy array (RGB format)
        pixel_array = pygame.surfarray.pixels3d(self.image)
        
        # Iterate over the color map and replace colors
        for old_color, new_color in zip(STANDARD_COLORS, (team_color, role_color)):
            # Convert HEX to RGB
            old_rgb = pygame.Color(old_color).r, pygame.Color(old_color).g, pygame.Color(old_color).b
            new_rgb = pygame.Color(new_color).r, pygame.Color(new_color).g, pygame.Color(new_color).b
            
            # Find and replace matching pixels
            mask = np.all(pixel_array == old_rgb, axis=-1)
            pixel_array[mask] = new_rgb
        
        del pixel_array  # Unlock the surface
    
    def set_id(self, n_agents):
        self.id = n_agents


    def move(self, vl, vr, dt, W, H):
        """Move the agent using differential drive physics."""
        self.vl = vl
        self.vr = vr
        self.vc = (vl + vr) / 2  # Linear velocity

        # Angular velocity (rotation)
        rotation = (vr - vl) / self.width  # Width = wheelbase distance
        self.body.angle = math.fmod(self.body.angle + rotation * dt, 2 * math.pi)  # Keep angle in [0, 2π]

        # Compute new position
        dx = math.cos(self.body.angle) * self.vc * dt
        dy = math.sin(self.body.angle) * self.vc * dt
        new_x = self.body.position.x + dx
        new_y = self.body.position.y + dy

        # Keep within screen bounds
        new_x = max(0, min(W, new_x))
        new_y = max(0, min(H, new_y))

        self.body.position = (new_x, new_y)  # Update position

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

        theta = -math.degrees(self.body.angle)  # Get rotation from Pymunk
        rotated_surface = pygame.transform.rotate(self.image, theta)
        rect = rotated_surface.get_rect(center=self.body.position)
        surface.blit(rotated_surface, rect.topleft)
            

    def update_objective_distance(self, objectives):
        obj = objectives[self.id]
        x_distance = self.x - obj[0]
        y_distance = self.y - obj[1]

        self.dist = x_distance, y_distance

