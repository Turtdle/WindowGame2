# levels/level3.py
import pygame
from levels.level import Level
import level_data  # Import our level data module

class Level3(Level):
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        super().__init__(window1_width, window1_height, window2_width, window2_height)
        
        # Set custom spawn position
        self.spawn_position = (0, 100)  # Near bottom left
        # Wall thickness
        self.wall_thickness = 25
        
        # Define walls for window 1 (lower window) - platforms with a hole
        self.window1_walls = [
            # Top horizontal wall
            pygame.Rect(0, 50, window1_width, self.wall_thickness),
            # Bottom horizontal wall - ground
            pygame.Rect(0, window1_height - 50, window1_width, self.wall_thickness),
            # Left platform
            pygame.Rect(0, window1_height // 3, window1_width // 2 - 100, self.wall_thickness),
            # Right platform
            pygame.Rect(window1_width // 2 + 100, window1_height // 3, window1_width // 2, self.wall_thickness),
        ]
        
        # Define walls for window 2 (upper window) - L-shaped platforms
        self.window2_walls = [
            # Top horizontal wall
            pygame.Rect(0, 50, window2_width, self.wall_thickness),
            # Bottom horizontal wall - ground
            pygame.Rect(0, window2_height - 50, window2_width, self.wall_thickness),
            # Left L-shape
            pygame.Rect(0, window2_height // 3, window2_width // 3, self.wall_thickness),  # Horizontal part
            pygame.Rect(window2_width // 3 - self.wall_thickness, window2_height // 3, self.wall_thickness, window2_height // 3),  # Vertical part
            # Right L-shape
            pygame.Rect(2 * window2_width // 3, window2_height // 3, window2_width // 3, self.wall_thickness),  # Horizontal part
            pygame.Rect(2 * window2_width // 3, window2_height // 3, self.wall_thickness, window2_height // 3),  # Vertical part
        ]
        
        # Define the goal in window 1
        self.goal = pygame.Rect(
            window1_width - 150, 
            window1_height - 150, 
            80, 80
        )
        
        # Gravity settings (similar to Level2)
        self.gravity = 0.5
        self.jump_power = -12
        self.on_ground = False
        
        # Track if the level is completed
        self.completed = False
        self.should_teleport_player = False
    
    def draw_window1(self, screen, player=None):
        # Draw instructions
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Level 3: Fall Through the Gap", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.window1_width//2, 30))
        screen.blit(text_surface, text_rect)
        
        # Draw goal
        pygame.draw.rect(screen, (0, 0, 255), self.goal)
        
        # Add text to identify the goal
        goal_font = pygame.font.Font(None, 36)
        goal_text = goal_font.render("GOAL", True, (255, 255, 255))
        goal_text_rect = goal_text.get_rect(center=self.goal.center)
        screen.blit(goal_text, goal_text_rect)
        
        # Draw walls
        for wall in self.window1_walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)
        
        # Draw the player if present
        if player:
            # Apply gravity
            self.apply_gravity(player)
            
            # Check for spacebar jumps
            self.handle_jump(player)
            
            # Check collisions
            self.check_wall_collisions(player, self.window1_walls)
            
            # Draw player
            player.draw(screen)
            
            # Check if player reached the goal
            player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
            if player_rect.colliderect(self.goal) and not self.completed:
                self.completed = True
                self.should_teleport_player = True
                print("Level 3 completed! Teleporting player back to Window 1")
                
                # Mark level as completed in the JSON file
                level_data.mark_level_completed("Level3")
            
    
    def draw_window2(self, screen, player=None):
        # Draw info text
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Use these L-shaped platforms and fall through the gap!", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.window2_width//2, 30))
        screen.blit(text_surface, text_rect)
        
        # Draw walls and platforms
        for wall in self.window2_walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)
        
        # Draw the player if present
        if player:
            # Handle player input - OVERRIDE default character movement
            self.handle_player_movement(player)
            
            # Apply gravity
            self.apply_gravity(player)
            
            # Check for spacebar jumps
            self.handle_jump(player)
            
            # Check collisions
            self.check_wall_collisions(player, self.window2_walls)
            
            # Draw player
            player.draw(screen)
            
    def apply_gravity(self, player):
        # Apply gravity to the player's vertical velocity
        player.vy += self.gravity
        
        # Cap falling speed to prevent too fast falling
        if player.vy > 15:
            player.vy = 15
            
        # Update player position
        player.y += player.vy
        player.x += player.vx

    def handle_player_movement(self, player):
        # Override the default Character.handle_keys() behavior
        # This method handles horizontal movement but lets gravity control vertical movement
        keys = pygame.key.get_pressed()
        player.vx = 0  # Reset horizontal velocity
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.vx = -player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.vx = player.speed
    
    def handle_jump(self, player):
        # Handle jumping when spacebar is pressed
        keys = pygame.key.get_pressed()
        
        if self.on_ground:
            if keys[pygame.K_SPACE]:
                player.vy = self.jump_power
                self.on_ground = False
    
    def check_wall_collisions(self, player, walls):
        # Create a rectangle for the player's current position
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        
        # Initially set on_ground to False - will be set to True if standing on a platform
        self.on_ground = False
        
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
                    player.vx = 0
                else:
                    if dy1 < dy2:
                        player.y = wall.bottom  # Push down
                        player.vy = 0
                    else:
                        player.y = wall.top - player.size  # Push up
                        
                        # If collision with bottom wall, set on_ground to True
                        # This happens when the player lands on top of a platform
                        if wall.top > player.y + (player.size / 2):
                            self.on_ground = True
                        
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