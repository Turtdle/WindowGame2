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
        # Jump state is tracked by the level to maintain level-specific gravity

    def update(self):
        # Character movement is now handled by the level in Level2
        # This allows the original movement in Level1 to remain unchanged
        # while allowing Level2 to apply gravity
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
        self.vx = 0
        # Don't reset vertical velocity (vy) here to allow gravity to work
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            # In Level2, this will be overridden by gravity
            self.vy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            # In Level2, this will add to gravity
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