# character.py
import pygame

class Character:
    def __init__(self, x=100, y=100, size=50, color=(0, 255, 0), speed=5):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
        self.vx = 0
        self.vy = 0
        self.current_level = None  # Track which level we're in

    def set_level(self, level_name):
        self.current_level = level_name

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (self.x, self.y, self.size, self.size)
        )

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        self.vx = 0  # Always reset horizontal velocity
        
        # Handle level-specific movement
        if self.current_level == "Level2":
            # For Level2: Don't reset vy, only control horizontal movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx = -self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx = self.speed
            # Intentionally NOT handling W/S here
        else:
            # For Level1 and Level_Selector: Reset vy and handle all directions
            self.vy = 0  # Reset vertical velocity
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx = -self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx = self.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.vy = -self.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vy = self.speed

    def keep_in_bounds(self, screen_width, screen_height):
        if self.x < 0:
            self.x = 0
        elif self.x + self.size > screen_width:
            self.x = screen_width - self.size
        
        if self.y < 0:
            self.y = 0
        elif self.y + self.size > screen_height:
            self.y = screen_height - self.size