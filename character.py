import pygame
import math

class Character:
    def __init__(self, x=100, y=100, size=50, color=(0, 255, 0), speed=5):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
        self.vx = 0
        self.vy = 0
        self.current_level = None 

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
        

        eye_radius = self.size // 10
        eye_offset_x = self.size // 4
        eye_offset_y = self.size // 3

        pygame.draw.circle(
            screen,
            (0, 0, 0), 
            (self.x + eye_offset_x, self.y + eye_offset_y),
            eye_radius
        )
        

        pygame.draw.circle(
            screen,
            (0, 0, 0), 
            (self.x + self.size - eye_offset_x, self.y + eye_offset_y),
            eye_radius
        )
        

        smile_radius = self.size // 3
        pygame.draw.arc(
            screen,
            (0, 0, 0), 
            (self.x + self.size//4, self.y + self.size//2, self.size//2, self.size//3),
            math.pi, 
            2 * math.pi, 
            2  
        )

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        self.vx = 0
        
        if self.current_level == "Level2" or self.current_level == "Level3":
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx = -self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx = self.speed
        else:
            self.vy = 0  
            
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