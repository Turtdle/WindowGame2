import pygame

class Level:
    def __init__(self, window1_width, window1_height, window2_width, window2_height):
        self.window1_width = window1_width
        self.window1_height = window1_height
        self.window2_width = window2_width
        self.window2_height = window2_height
        
        self.spawn_position = (window1_width // 2, window1_height // 2)
        
    def draw_window1(self, screen, player=None):
        pass
        
    def draw_window2(self, screen, player=None):
        pass
    
    def handle_click(self, position, window_id):
        pass

    def get_next_level(self):
        return None