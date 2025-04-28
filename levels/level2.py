import pygame
from levels.level import Level
import level_data  # Import our level data module

class Level2(Level):
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        super().__init__(window1_width, window1_height, window2_width, window2_height)
        
        self.spawn_position = (100, window1_height - 150)  # Near bottom left
        self.wall_thickness = 25
        
        self.window1_walls = [
            pygame.Rect(0, 50, window1_width, self.wall_thickness),
            pygame.Rect(0, window1_height - 50, window1_width, self.wall_thickness),
            pygame.Rect(0, window1_height//2, window1_width - 200, self.wall_thickness),
            pygame.Rect(window1_width - 200, window1_height//2 - 200, self.wall_thickness, 200)
        ]
        
        self.window2_walls = [
            pygame.Rect(0, 50, window2_width, self.wall_thickness),
            pygame.Rect(0, window2_height - 50, window2_width, self.wall_thickness),
            pygame.Rect(window2_width//4, window2_height - 200, window2_width//4, self.wall_thickness),
            pygame.Rect(window2_width//2, window2_height - 350, window2_width//4, self.wall_thickness)
        ]
        
        
        self.goal = pygame.Rect(
            window1_width - 150, 
            window1_height//2 - 150, 
            80, 80
        )
        
        self.gravity = 0.5
        self.jump_power = -12
        self.on_ground = False
        
        self.completed = False
        self.should_teleport_player = False
    
    def draw_window1(self, screen, player=None):
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Level 2: Moving Between Windows", True, (0, 0, 0))
        text_surface2 = font.render("Space to jump", True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.window1_width//2, 30))
        screen.blit(text_surface, text_rect)
        text_rect2 = text_surface2.get_rect(center=(self.window1_width//2, 90))
        screen.blit(text_surface2, text_rect2)
        
        pygame.draw.rect(screen, (0, 0, 255), self.goal)
        
        goal_font = pygame.font.Font(None, 36)
        goal_text = goal_font.render("GOAL", True, (255, 255, 255))
        goal_text_rect = goal_text.get_rect(center=self.goal.center)
        screen.blit(goal_text, goal_text_rect)
        
        
        for wall in self.window1_walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)
        
        if player:
            
            self.apply_gravity(player)
            
            self.handle_jump(player)
            
            self.check_wall_collisions(player, self.window1_walls)
            
            player.draw(screen)
            
            player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
            if player_rect.colliderect(self.goal) and not self.completed:
                self.completed = True
                self.should_teleport_player = True
                print("Level 2 completed! Teleporting player back to Window 1")
                
                level_data.mark_level_completed("Level2")
            
    def draw_window2(self, screen, player=None):
        font = pygame.font.Font(None, 36)
        
        for wall in self.window2_walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)
        

        if player:
            original_vx, original_vy = player.vx, player.vy
            
            self.handle_player_movement(player)
            
            self.apply_gravity(player)
            
            self.handle_jump(player)
            
            self.check_wall_collisions(player, self.window2_walls)
            
            player.draw(screen)
    
    def apply_gravity(self, player):
        player.vy += self.gravity
        
        if player.vy > 15:
            player.vy = 15
            
        player.y += player.vy
        player.x += player.vx

    def handle_player_movement(self, player):
        keys = pygame.key.get_pressed()
        player.vx = 0  # Reset horizontal velocity
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.vx = -player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.vx = player.speed
        
    
    def handle_jump(self, player):
        keys = pygame.key.get_pressed()
        
        self.debug_info = f"On ground: {self.on_ground}, Vy: {player.vy:.1f}, Space: {keys[pygame.K_SPACE]}"
        
        if self.on_ground:
            if keys[pygame.K_SPACE]:
                player.vy = self.jump_power
                self.on_ground = False
                print(f"JUMP! vy set to {player.vy}")
    
    def check_wall_collisions(self, player, walls):
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        
        self.on_ground = False
        
        for wall in walls:
            if player_rect.colliderect(wall):
                dx1 = wall.right - player_rect.left
                dx2 = player_rect.right - wall.left
                dy1 = wall.bottom - player_rect.top
                dy2 = player_rect.bottom - wall.top
                
                dx = min(dx1, dx2)
                dy = min(dy1, dy2)
                
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
                        
                        if wall.top > player.y + (player.size / 2):
                            self.on_ground = True
                        
                        player.vy = 0
                
                player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
    
    def get_next_level(self):
        if self.completed:
            print("Returning to level selector...")
            from levels.level_selector import Level_Selector
            return Level_Selector(self.window1_width, self.window1_height, 
                               self.window2_width, self.window2_height)
        return None