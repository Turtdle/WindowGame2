# levels/level_selector.py
import pygame
from levels.level import Level
from levels.level1 import Level1
from levels.level2 import Level2
from levels.level3 import Level3
import level_data  # Import our new level data module

class Level_Selector(Level):
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        super().__init__(window1_width, window1_height, window2_width, window2_height)
        
        # Define box dimensions
        box_width = 200
        box_height = 100
        
        # Load completed levels from JSON file
        self.completed_levels = level_data.load_completed_levels()
        print(f"Loaded completed levels: {self.completed_levels}")
        
        # Define the three level boxes
        self.level_boxes = [
            {
                "rect": pygame.Rect(window1_width//2 - box_width//2, 
                                   window1_height//4, 
                                   box_width, box_height),
                "default_color": (0, 200, 0),  # Green for available level
                "completed_color": (0, 0, 255),  # Blue for completed level
                "text": "Level 1",
                "level_class": Level1,
                "active": True,
                "level_name": "Level1"
            },
            {
                "rect": pygame.Rect(window1_width//2 - box_width//2, 
                                   window1_height//2, 
                                   box_width, box_height),
                "default_color": (0, 200, 0),  # Green for available level
                "completed_color": (0, 0, 255),  # Blue for completed level
                "text": "Level 2",
                "level_class": Level2,
                "active": True,
                "level_name": "Level2" 
            },
            {
                "rect": pygame.Rect(window1_width//2 - box_width//2, 
                                   3*window1_height//4, 
                                   box_width, box_height),
                "default_color": (0, 200, 0),  # Green for available level
                "completed_color": (0, 0, 255),  # Blue for completed level
                "text": "Level 3",
                "level_class": Level3,
                "active": True,
                "level_name": "Level3"
            }
        ]
        
        self.next_level = None
    
    def draw_window1(self, screen, player=None):
        # Draw level selection boxes in window 1
        font = pygame.font.Font(None, 36)
        
        # Draw completion counter
        completion_count = len(self.completed_levels)
        total_levels = len(self.level_boxes)
        
        counter_font = pygame.font.Font(None, 42)
        counter_text = f"Levels Completed: {completion_count}/{total_levels}"
        counter_surface = counter_font.render(counter_text, True, (0, 0, 0))
        counter_rect = counter_surface.get_rect(center=(self.window1_width//2, 50))
        screen.blit(counter_surface, counter_rect)
        
        for box in self.level_boxes:
            # Determine color based on completion status
            if box["level_name"] in self.completed_levels:
                color = box["completed_color"]
            else:
                color = box["default_color"]
                
            pygame.draw.rect(screen, color, box["rect"])
            
            # Draw the level text
            text_surface = font.render(box["text"], True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=box["rect"].center)
            screen.blit(text_surface, text_rect)
            
            # If completed, add a checkmark or completed text
            if box["level_name"] in self.completed_levels:
                complete_text = font.render("✓", True, (255, 255, 255))
                complete_rect = complete_text.get_rect(
                    center=(box["rect"].right - 30, box["rect"].top + 25)
                )
                screen.blit(complete_text, complete_rect)
        
        # Draw the player if present
        if player:
            player.draw(screen)
    
    def draw_window2(self, screen, player=None):
        # Draw title in window 2
        font = pygame.font.Font(None, 48)
        title_text = "A Window"
        title_surface = font.render(title_text, True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(self.window2_width//2, self.window2_height//3))
        screen.blit(title_surface, title_rect)
        
        # Draw instructions
        instr_font = pygame.font.Font(None, 28)
        instructions = [
            "Move with WASD keys",
            "Place windows next to each other to jump between them",
            "Complete all levels to win the game!",
            "Your progress is automatically saved"
        ]
        
        y_pos = self.window2_height//2
        for instruction in instructions:
            instr_surface = instr_font.render(instruction, True, (0, 0, 0))
            instr_rect = instr_surface.get_rect(center=(self.window2_width//2, y_pos))
            screen.blit(instr_surface, instr_rect)
            y_pos += 40
            
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