# levels/level.py
import pygame

class Level:
# In levels/level.py, add to the __init__ method:
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        self.window1_width = window1_width
        self.window1_height = window1_height
        self.window2_width = window2_width
        self.window2_height = window2_height
        
        # Default spawn position (center of window1)
        self.spawn_position = (window1_width // 2, window1_height // 2)
        
    def draw_window1(self, screen, player=None):
        # Override in subclasses to draw window1 specific content
        pass
        
    def draw_window2(self, screen, player=None):
        # Override in subclasses to draw window2 specific content
        pass
    
    def handle_click(self, position, window_id):
        # Override in subclasses to handle mouse click events
        pass

    def get_next_level(self):
        # Override in subclasses to return the next level if needed
        return None