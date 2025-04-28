# levels/level1.py
import pygame
from levels.level import Level

class Level1(Level):
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        super().__init__(window1_width, window1_height, window2_width, window2_height)
        
        # Create a goal in window 2
        self.goal = pygame.Rect(
            window2_width//2 - 50, 
            window2_height//2 - 50, 
            100, 100
        )
        
        # Track if the level is completed
        self.completed = False
    
    def draw_window1(self, screen, player=None):
        # Draw instructions in window 1
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Level 1: Reach the goal in Window 2", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.window1_width//2, 100))
        screen.blit(text_surface, text_rect)
        
        # Draw the player if present
        if player:
            player.draw(screen)
            
    def draw_window2(self, screen, player=None):
        # Draw the goal in window 2 - make it more visible
        pygame.draw.rect(screen, (255, 0, 0), self.goal)  # Red goal
        pygame.draw.rect(screen, (0, 0, 0), self.goal, 3)  # Black border
        
        # Add text to identify the goal
        font = pygame.font.Font(None, 36)
        text_surface = font.render("GOAL", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.goal.center)
        screen.blit(text_surface, text_rect)
        
        # Draw the player if present - make sure player is not None
        if player is not None:
            player.draw(screen)
            
            # Check if player reached the goal
            player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
            if player_rect.colliderect(self.goal):
                self.completed = True
                print("Level 1 completed!")