# window.py
from multiprocessing.connection import Connection
from character import Character
from pygame._sdl2.video import Window
import pygame

class WindowClass:
    def __init__(self, window_title="Window", width=1000, height=1000, bg_color=(255, 255, 255), 
                  origin=False, 
                  pos_send_pipe: Connection = None,
                  pos_recv_pipe: Connection = None,
                  transfer_send_pipe: Connection = None,
                  transfer_recv_pipe: Connection = None,
                  my_window=None, current_level=None, running=True):
        
        self.has_player = False
        self.window_title = window_title
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.origin = origin
        self.pos_send_pipe = pos_send_pipe
        self.pos_recv_pipe = pos_recv_pipe
        self.transfer_send_pipe = transfer_send_pipe
        self.transfer_recv_pipe = transfer_recv_pipe
        self.other_window_pos = None
        self.my_window = my_window
        self.my_position = self.my_window.position
        self.player = None
        self.running = running
        self.current_level = current_level

        if self.origin:
            self.has_player = True
            self.player = Character(x=width//2, y=height//2)
            
        # Initialize mouse handling
        self.mouse_down = False

    def tick(self):
        # Handle window position communication
        if self.pos_recv_pipe and self.pos_recv_pipe.poll():
            try:
                self.other_window_pos = self.pos_recv_pipe.recv()
            except (EOFError, BrokenPipeError):
                print(f"{self.window_title}: Position pipe connection closed.")
                self.running = False
            except Exception as e:
                print(f"{self.window_title}: Error receiving position data: {e}")
                
        # Send window position
        current_pos = self.my_window.position
        if True:
            my_position = current_pos
            try:
                self.pos_send_pipe.send(my_position)
            except (BrokenPipeError, OSError):
                print(f"{self.window_title}: Error sending position, pipe may be closed.")
                self.running = False
        
        # Check for level changes in Window 1
        if self.window_title == "Window 1" and self.current_level:
            next_level = self.current_level.get_next_level()
            if next_level:
                # Set our own level
                self.current_level = next_level
                print(f"{self.window_title}: Switched to new level")
                
                # Send level change to Window 2
                try:
                    level_data = {
                        "type": "level_change",
                        "level_name": next_level.__class__.__name__
                    }
                    self.transfer_send_pipe.send(level_data)
                    print(f"{self.window_title}: Sent level change to other window")
                except (BrokenPipeError, OSError) as e:
                    print(f"{self.window_title}: Error sending level change: {e}")
        
        # Handle transfer data (player movement & level changes)
        if self.transfer_recv_pipe and self.transfer_recv_pipe.poll():
            try:
                data = self.transfer_recv_pipe.recv()
                
                # Check if this is a level change notification
                if isinstance(data, dict) and data.get("type") == "level_change":
                    level_name = data.get("level_name")
                    if level_name == "Level1":
                        from levels.level1 import Level1
                        self.current_level = Level1(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")
                    # Can add other levels here as they're implemented
                    
                # Handle player transfers
                elif not self.has_player and isinstance(data, dict) and "side" in data:
                    self.has_player = True
                    
                    if data.get("side") == "right":
                        self.player = Character(x=0 + 5, y=data.get("relative", self.height//2)) 
                    elif data.get("side") == "left":
                        self.player = Character(x=self.width - Character().size - 5, y=data.get("relative", self.height//2))
                    
                    print(f"{self.window_title} received player at ({self.player.x}, {self.player.y})")
                    
            except (EOFError, BrokenPipeError):
                print(f"{self.window_title}: Transfer pipe connection closed.")
                self.running = False
            except Exception as e:
                print(f"{self.window_title}: Error receiving transfer data: {e}")
        
        # Player movement and window transfer logic
        if self.has_player and self.player:
            self.player.handle_keys()
            self.player.update()
            
            transfer_occurred = False

            if self.player.x + self.player.size >= self.width:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                if self.other_window_pos and self.transfer_send_pipe:
                    vert_aligned = abs(my_position[1] - self.other_window_pos[1]) < 100
                    horz_aligned = abs((my_position[0] + self.width) - self.other_window_pos[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{self.window_title}: Attempting to pass player right to {other_win_title}")
                        pass_data = {
                            "side": "right",
                            "relative": self.player.y,
                        }
                        try:
                            self.transfer_send_pipe.send(pass_data)
                            self.has_player = False
                            self.player = None
                            transfer_occurred = True
                        except (BrokenPipeError, OSError):
                            print(f"{self.window_title}: Error sending player, pipe may be closed.")
                            self.running = False
            elif self.player.x <= 0:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                if self.other_window_pos and self.transfer_send_pipe:
                    vert_aligned = abs(my_position[1] - self.other_window_pos[1]) < 100 
                    horz_aligned = abs((self.other_window_pos[0] + self.width) - my_position[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{self.window_title}: Attempting to pass player left to {other_win_title}") 
                        pass_data = {
                            "side": "left",
                            "relative": self.player.y,
                        }
                        try:
                            self.transfer_send_pipe.send(pass_data)
                            self.has_player = False
                            self.player = None
                            transfer_occurred = True
                        except (BrokenPipeError, OSError):
                            print(f"{self.window_title}: Error sending player, pipe may be closed.")
                            self.running = False
            
            if self.has_player and self.player and not transfer_occurred:
                self.player.keep_in_bounds(self.width, self.height)
    
    def handle_event(self, event):
        # Process mouse events for level selection
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down = True
        elif event.type == pygame.MOUSEBUTTONUP and self.mouse_down:
            self.mouse_down = False
            if self.current_level:
                self.current_level.handle_click(event.pos, self.window_title)
    
    def draw(self, screen):
        # Clear the screen
        screen.fill(self.bg_color)
        
        # Draw the current level
        if self.current_level:
            if self.window_title == "Window 1":
                self.current_level.draw_window1(screen, self.player if self.has_player else None)
            else:
                self.current_level.draw_window2(screen, self.player if self.has_player else None)
        else:
            # If no level, just draw the player
            if self.has_player and self.player:
                self.player.draw(screen)