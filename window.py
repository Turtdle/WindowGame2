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

# In window.py __init__ method:
        if self.origin:
            self.has_player = True
            # Use level's spawn position if available
            if self.current_level and hasattr(self.current_level, 'spawn_position'):
                spawn_x, spawn_y = self.current_level.spawn_position
                
            else:
                
                spawn_x, spawn_y = width//2, height//2
            self.player = Character(x=spawn_x, y=spawn_y)
            if self.current_level:
                self.player.set_level(self.current_level.__class__.__name__)
        self.mouse_down = False
        
        # DEBUG: Track teleportation status
        self.teleport_sent = False

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
        
        # Check if player should be teleported after level completion - Do this FIRST
        if self.current_level and hasattr(self.current_level, 'should_teleport_player') and self.current_level.should_teleport_player and not self.teleport_sent:
            # If we're Window 2 and need to teleport player to Window 1
            if self.window_title == "Window 2" and self.has_player:
                print(f"{self.window_title}: Teleporting player back to Window 1")
                try:
                    teleport_data = {
                        "type": "teleport_player",
                        "position": self.current_level.spawn_position if hasattr(self.current_level, 'spawn_position') else (self.width//2, self.height//2),
                        "level": self.current_level.__class__.__name__
                    }
                    self.transfer_send_pipe.send(teleport_data)
                    self.teleport_sent = True  # Mark that we've sent the teleport message
                    self.has_player = False
                    self.player = None
                    self.current_level.should_teleport_player = False
                    print(f"{self.window_title}: Teleport message sent to Window 1")
                except (BrokenPipeError, OSError) as e:
                    print(f"{self.window_title}: Error teleporting player: {e}")
        
        # THEN handle level changes
        if self.current_level:
            next_level = self.current_level.get_next_level()
            if next_level:
                # Set our own level
                prev_level_name = self.current_level.__class__.__name__
                self.current_level = next_level
                print(f"{self.window_title}: Switched from {prev_level_name} to {next_level.__class__.__name__}")
                
                # Update the player's level information
                if self.player:
                    self.player.set_level(next_level.__class__.__name__)
                # If this is Window 1, send level change to Window 2
                if self.window_title == "Window 1":
                    try:
                        level_data = {
                            "type": "level_change",
                            "level_name": next_level.__class__.__name__
                        }
                        self.transfer_send_pipe.send(level_data)
                        print(f"{self.window_title}: Sent level change to Window 2")
                    except (BrokenPipeError, OSError) as e:
                        print(f"{self.window_title}: Error sending level change: {e}")
                
                # Reset teleport tracking when changing levels
                self.teleport_sent = False
                
                # If this is Window 2, notify Window 1 that it has completed a level
                if self.window_title == "Window 2":
                    try:
                        level_data = {
                            "type": "level_completed",
                            "level_name": "Level_Selector"
                        }
                        self.transfer_send_pipe.send(level_data)
                        print(f"{self.window_title}: Notified Window 1 of level completion")
                    except (BrokenPipeError, OSError) as e:
                        print(f"{self.window_title}: Error notifying of level completion: {e}")
        
        # Handle transfer data (player movement & level changes)
        if self.transfer_recv_pipe and self.transfer_recv_pipe.poll():
            try:
                data = self.transfer_recv_pipe.recv()
                print(f"{self.window_title}: Received data: {data}")
                
                # When receiving teleport data:
                if isinstance(data, dict) and data.get("type") == "teleport_player":
                    if self.window_title == "Window 1":
                        print(f"{self.window_title}: Processing teleport_player data")
                        self.has_player = True
                        
                        # Check for custom spawn position in the level
                        if self.current_level and hasattr(self.current_level, 'spawn_posi   tion'):
                            position = self.current_level.spawn_position
                        else:
                            # Fall back to position from data or default center
                            position = data.get("position", (self.width//2, self.height//2))
                            
                        if not self.player: # Create player if it doesn't exist
                            self.player = Character(x=position[0], y=position[1])
                        else: # Update player position if it exists
                            self.player.x = position[0]
                            self.player.y = position[1]
                        
                        # Set the player's level based on received information
                        if data.get("level"):
                            self.player.set_level(data.get("level"))
                        elif self.current_level:
                            self.player.set_level(self.current_level.__class__.__name__)
                            
                        print(f"{self.window_title}: Player teleported back at position {position}")
                        
                # Check if this is a level change notification
                elif isinstance(data, dict) and data.get("type") == "level_change":
                    level_name = data.get("level_name")
                    if level_name == "Level1":
                        from levels.level1 import Level1
                        self.current_level = Level1(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")
                    elif level_name == "Level2":  # Add Level2 handling
                        from levels.level2 import Level2
                        self.current_level = Level2(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")
                    elif level_name == "Level3":  # Add Level3 handling
                        from levels.level3 import Level3
                        self.current_level = Level3(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")
                    elif level_name == "Level_Selector":
                        from levels.level_selector import Level_Selector
                        self.current_level = Level_Selector(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")

                # Handle player transfers
# Handle player transfers
                elif not self.has_player and isinstance(data, dict) and "side" in data:
                    self.has_player = True
                    
                    if data.get("side") == "right":
                        self.player = Character(x=0 + 5, y=data.get("relative", self.height//2))
                    elif data.get("side") == "left":
                        self.player = Character(x=self.width - Character().size - 5, y=data.get("relative", self.height//2))
                    
                    # Set the player's level based on received information
                    if data.get("level"):
                        self.player.set_level(data.get("level"))
                    elif self.current_level:
                        self.player.set_level(self.current_level.__class__.__name__)
                    
                    print(f"{self.window_title} received player at ({self.player.x}, {self.player.y})")
                    
                elif isinstance(data, dict) and data.get("type") == "level_completed":
                    level_name = data.get("level_name")
                    if level_name == "Level_Selector" and self.window_title == "Window 1":
                        from levels.level_selector import Level_Selector
                        self.current_level = Level_Selector(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Switched to level selector due to completion notification")
                        
                        # Also inform Window 2 to switch to the level selector
                        try:
                            level_data = {
                                "type": "level_change",
                                "level_name": "Level_Selector"
                            }
                            self.transfer_send_pipe.send(level_data)
                            print(f"{self.window_title}: Sent level change to Window 2")
                        except (BrokenPipeError, OSError) as e:
                            print(f"{self.window_title}: Error sending level change: {e}")
                
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
            
            # Only allow transfers if not in level selector
            allow_transfer = not (self.current_level and self.current_level.__class__.__name__ == "Level_Selector")

            if allow_transfer and self.player.x + self.player.size >= self.width:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                if self.other_window_pos and self.transfer_send_pipe:
                    vert_aligned = abs(my_position[1] - self.other_window_pos[1]) < 100
                    horz_aligned = abs((my_position[0] + self.width) - self.other_window_pos[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{self.window_title}: Attempting to pass player right to {other_win_title}")
                        pass_data = {
                            "side": "right",
                            "relative": self.player.y,
                            "level": self.current_level.__class__.__name__  # Add this line
                        }
                        try:
                            self.transfer_send_pipe.send(pass_data)
                            self.has_player = False
                            self.player = None
                            transfer_occurred = True
                        except (BrokenPipeError, OSError):
                            print(f"{self.window_title}: Error sending player, pipe may be closed.")
                            self.running = False
            elif allow_transfer and self.player.x <= 0:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                if self.other_window_pos and self.transfer_send_pipe:
                    vert_aligned = abs(my_position[1] - self.other_window_pos[1]) < 100 
                    horz_aligned = abs((self.other_window_pos[0] + self.width) - my_position[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{self.window_title}: Attempting to pass player left to {other_win_title}")
                        pass_data = {
                            "side": "left",
                            "relative": self.player.y,
                            "level": self.current_level.__class__.__name__  # Add this line
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