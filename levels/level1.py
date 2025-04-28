# levels/level1.py
import pygame
from levels.level import Level

class Level1(Level):
# For example in Level3:
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        super().__init__(window1_width, window1_height, window2_width, window2_height)
        
        # Set custom spawn position
        self.spawn_position = (100, window1_height - 150)  # Near bottom left
        
        # Wall thickness - making it slightly thicker for better collisions
        self.wall_thickness = 25
        
        # Define walls for window 1 (green lines in left window)
        self.window1_walls = [
            # Top horizontal wall
            pygame.Rect(0, 50, window1_width, self.wall_thickness),
            # Right vertical wall
            pygame.Rect(window1_width - 150, 50, self.wall_thickness, window1_height - 100),
            # Bottom horizontal wall
            pygame.Rect(0, window1_height - 50, window1_width, self.wall_thickness),
            # Middle vertical wall
            pygame.Rect(window1_width // 3, 150, self.wall_thickness, window1_height - 200)
        ]
        
        # Define walls for window 2 (green lines in right window)
        self.window2_walls = [
            # Top horizontal wall
            pygame.Rect(50, 50, window2_width , self.wall_thickness),

            # Bottom horizontal wall
            pygame.Rect(50, window2_height - 50, window2_width , self.wall_thickness),
            # Right vertical wall
            pygame.Rect(100, 50, self.wall_thickness, window1_height - 100)
        ]
        
        # Define the goal in window 2 (blue shape)
        self.goal = pygame.Rect(
            window2_width // 2 - 100, 
            window2_height // 3, 
            80, 80
        )
        
        # Track if the level is completed
        self.completed = False
        # Track whether we need to teleport the player back to window 1
        self.should_teleport_player = False
    
    def draw_window1(self, screen, player=None):
        # Draw instructions
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Tutorial: Arrange the windows to cross over and reach the goal", True, (0, 0, 0))
        text_surface2 = font.render("Move the windows next to each other to jump windows", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.window1_width//2, 30))
        screen.blit(text_surface, text_rect)
        text_rect2 = text_surface2.get_rect(center=(self.window1_width//2, 90))
        screen.blit(text_surface2, text_rect2)
        
        # Draw walls
        for wall in self.window1_walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)  # Green walls
        
        # Draw the player if present
        if player:
            # Check collisions before drawing
            self.check_wall_collisions(player, self.window1_walls)
            player.draw(screen)
            
    def draw_window2(self, screen, player=None):
        # Draw walls
        for wall in self.window2_walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)  # Green walls
        
        # Draw the goal
        pygame.draw.rect(screen, (0, 0, 255), self.goal)  # Blue goal
        
        # Add text to identify the goal
        font = pygame.font.Font(None, 36)
        text_surface = font.render("GOAL", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.goal.center)
        screen.blit(text_surface, text_rect)
        
        # Draw the player if present
        if player is not None:
            # Check collisions before drawing
            self.check_wall_collisions(player, self.window2_walls)
            player.draw(screen)
            
            # Check if player reached the goal
            player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
            if player_rect.colliderect(self.goal) and not self.completed:
                self.completed = True
                self.should_teleport_player = True
                print("Level 1 completed! Teleporting player back to Window 1")
    
    def check_wall_collisions(self, player, walls):
        # Store original position to revert if needed
        original_x = player.x
        original_y = player.y
        
        # Create a rectangle for the player's current position
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        
        # Check collision with each wall
        for wall in walls:
            if player_rect.colliderect(wall):
                # Calculate overlap
                dx1 = wall.right - player_rect.left
                dx2 = player_rect.right - wall.left
                dy1 = wall.bottom - player_rect.top
                dy2 = player_rect.bottom - wall.top
                
                # Find minimum penetration
                dx = min(dx1, dx2)
                dy = min(dy1, dy2)
                
                # Resolve collision based on smallest penetration
                if dx < dy:
                    if dx1 < dx2:
                        player.x = wall.right  # Push right
                    else:
                        player.x = wall.left - player.size  # Push left
                else:
                    if dy1 < dy2:
                        player.y = wall.bottom  # Push down
                    else:
                        player.y = wall.top - player.size  # Push up
                
                # Stop movement in the direction of collision
                if dx < dy:
                    player.vx = 0
                else:
                    player.vy = 0
                
                # Update player rect for next wall check
                player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
    
    def get_next_level(self):
        # If the level is completed, return to level selector
        if self.completed:
            print("Returning to level selector...")
            from levels.level_selector import Level_Selector
            return Level_Selector(self.window1_width, self.window1_height, 
                               self.window2_width, self.window2_height)
        return None