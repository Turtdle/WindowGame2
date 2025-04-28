# levels/level_selector.py
import pygame
from levels.level import Level
from levels.level1 import Level1
from levels.level2 import Level2
from levels.level3 import Level3  # Import Level3

class Level_Selector(Level):
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        super().__init__(window1_width, window1_height, window2_width, window2_height)
        
        # Define boxes for level selection (only in window1)
        box_width = 200
        box_height = 100
        margin = 50
        
        # Define the three level boxes
        self.level_boxes = [
            {
                "rect": pygame.Rect(window1_width//2 - box_width//2, 
                                   window1_height//4, 
                                   box_width, box_height),
                "color": (0, 200, 0),  # Green for level 1 (active)
                "text": "Level 1",
                "level_class": Level1,
                "active": True
            },
            {
                "rect": pygame.Rect(window1_width//2 - box_width//2, 
                                   window1_height//2, 
                                   box_width, box_height),
                "color": (0, 200, 0),  # Green for level 2 (now active)
                "text": "Level 2",
                "level_class": Level2,  # Set Level2 class
                "active": True         # Set to active
            },
            {
                "rect": pygame.Rect(window1_width//2 - box_width//2, 
                                   3*window1_height//4, 
                                   box_width, box_height),
                "color": (0, 200, 0),  # Green for level 3 (now active)
                "text": "Level 3",
                "level_class": Level3,  # Set to Level3 class
                "active": True         # Set to active
            }
        ]
        
        self.next_level = None
    
    def draw_window1(self, screen, player=None):
        # Draw level selection boxes in window 1
        font = pygame.font.Font(None, 36)
        
        for box in self.level_boxes:
            pygame.draw.rect(screen, box["color"], box["rect"])
            
            # Draw the level text
            text_surface = font.render(box["text"], True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=box["rect"].center)
            screen.blit(text_surface, text_rect)
        
        # Draw the player if present
        if player:
            player.draw(screen)
    
    def draw_window2(self, screen, player=None):
        # Window 2 is empty in the level selector
        # Just draw the player if present
        if player:
            player.draw(screen)
    
    def handle_click(self, position, window_id):
        # Only handle clicks in window 1
        if window_id != "Window 1":
            return
            
        for box in self.level_boxes:
            if box["rect"].collidepoint(position) and box["active"]:
                # Create the selected level
                if box["level_class"]:
                    self.next_level = box["level_class"](
                        self.window1_width, self.window1_height, 
                        self.window2_width, self.window2_height
                    )
                    return True
        return False
    
    def get_next_level(self):
        next_level = self.next_level
        self.next_level = None
        return next_level