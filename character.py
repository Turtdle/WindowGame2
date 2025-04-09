import pygame

class Character:
    def __init__(self, x=100, y=100, size=50, color=(0, 255, 0), speed=5):
        # Position
        self.x = x
        self.y = y
        
        # Dimensions
        self.size = size
        
        # Appearance
        self.color = color  # Green by default
        
        # Movement
        self.speed = speed
        self.vx = 0  # Velocity in x direction
        self.vy = 0  # Velocity in y direction
    
    def update(self):
        """Update character position based on velocity"""
        self.x += self.vx
        self.y += self.vy
    
    def draw(self, screen):
        """Draw the character (green square) on the screen"""
        pygame.draw.rect(
            screen, 
            self.color, 
            (self.x, self.y, self.size, self.size)
        )
    
    def handle_keys(self):
        """Handle keyboard input for character movement"""
        keys = pygame.key.get_pressed()
        
        # Reset velocity
        self.vx = 0
        self.vy = 0
        
        # Set velocity based on keys pressed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = self.speed
    
    def keep_in_bounds(self, screen_width, screen_height):
        """Prevent character from moving off-screen"""
        # Left boundary
        if self.x < 0:
            self.x = 0
        # Right boundary
        elif self.x + self.size > screen_width:
            self.x = screen_width - self.size
        # Top boundary
        if self.y < 0:
            self.y = 0
        # Bottom boundary
        elif self.y + self.size > screen_height:
            self.y = screen_height - self.size