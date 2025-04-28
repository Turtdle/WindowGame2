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
            if self.current_level and hasattr(self.current_level, 'spawn_position'):
                spawn_x, spawn_y = self.current_level.spawn_position
                
            else:
                
                spawn_x, spawn_y = width//2, height//2
            self.player = Character(x=spawn_x, y=spawn_y)
            if self.current_level:
                self.player.set_level(self.current_level.__class__.__name__)
        self.mouse_down = False
        
        self.teleport_sent = False

    def tick(self):
        if not hasattr(self, 'last_position_send_time'):
            self.last_position_send_time = 0
        
        current_time = pygame.time.get_ticks() / 1000  
        
        try:
            
            if current_time - self.last_position_send_time >= 0.5:
                if self.pos_send_pipe and not self.pos_send_pipe.closed:
                    self.pos_send_pipe.send(self.my_window.position)
                    self.last_position_send_time = current_time
        except (BrokenPipeError, OSError, IOError):
            print(f"{self.window_title}: Other window appears to be closed, shutting down")
            self.running = False
            return
            
        if self.pos_recv_pipe and self.pos_recv_pipe.poll():
            try:
                self.other_window_pos = self.pos_recv_pipe.recv()
            except (EOFError, BrokenPipeError):
                print(f"{self.window_title}: Position pipe connection closed.")
                self.running = False
            except Exception as e:
                print(f"{self.window_title}: Error receiving position data: {e}")
                
    
        current_pos = self.my_window.position
        if True:
            self.my_position = current_pos
        
                

        if self.pos_recv_pipe and self.pos_recv_pipe.poll():
            try:
                self.other_window_pos = self.pos_recv_pipe.recv()
            except (EOFError, BrokenPipeError):
                print(f"{self.window_title}: Position pipe connection closed.")
                self.running = False
            except Exception as e:
                print(f"{self.window_title}: Error receiving position data: {e}")
                
        current_pos = self.my_window.position
        if True:
            my_position = current_pos
            try:
                self.pos_send_pipe.send(my_position)
            except (BrokenPipeError, OSError):
                print(f"{self.window_title}: Error sending position, pipe may be closed.")
                self.running = False
        
        if self.current_level and hasattr(self.current_level, 'should_teleport_player') and self.current_level.should_teleport_player and not self.teleport_sent:
            
            """
            
            Synchronization
            If you complete a level AND player is on window 2, tell window 1 to spawn the player
            Delete the player on window 2

            """

            if self.window_title == "Window 2" and self.has_player:
                print(f"{self.window_title}: Teleporting player back to Window 1")
                try:
                    teleport_data = {
                        "type": "teleport_player",
                        "position": self.current_level.spawn_position if hasattr(self.current_level, 'spawn_position') else (self.width//2, self.height//2),
                        "level": self.current_level.__class__.__name__
                    }
                    self.transfer_send_pipe.send(teleport_data)
                    self.teleport_sent = True  
                    self.has_player = False
                    self.player = None
                    self.current_level.should_teleport_player = False
                    print(f"{self.window_title}: Teleport message sent to Window 1")
                except (BrokenPipeError, OSError) as e:
                    print(f"{self.window_title}: Error teleporting player: {e}")
        
        if self.current_level:
            next_level = self.current_level.get_next_level()
            if next_level:
                prev_level_name = self.current_level.__class__.__name__
                self.current_level = next_level
                print(f"{self.window_title}: Switched from {prev_level_name} to {next_level.__class__.__name__}")
                
                if self.player:
                    self.player.set_level(next_level.__class__.__name__)
                    if hasattr(next_level, 'spawn_position'):
                        self.player.x, self.player.y = next_level.spawn_position

                """
                
                Synchronization:
                If we move from one level to another, we need to update the other window

                """
                

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
                
                self.teleport_sent = False
                
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
        
        if self.transfer_recv_pipe and self.transfer_recv_pipe.poll():
            
            try:
                data = self.transfer_recv_pipe.recv()
                print(f"{self.window_title}: Received data: {data}")
                
                if isinstance(data, dict) and data.get("type") == "window_closing":
                    print(f"{self.window_title}: Other window is closing, shutting down")
                    self.running = False
                    return  # Exit tick early
                if isinstance(data, dict) and data.get("type") == "teleport_player":
                    if self.window_title == "Window 1":
                        print(f"{self.window_title}: Processing teleport_player data")
                        self.has_player = True
                        
                        position = data.get("position")
                        if position is None and self.current_level and hasattr(self.current_level, 'spawn_position'):
                            position = self.current_level.spawn_position
                        else:
                            position = position or (self.width//2, self.height//2)
                            
                        if not self.player: 
                            self.player = Character(x=position[0], y=position[1])
                        else: 
                            self.player.x = position[0]
                            self.player.y = position[1]
                        
                        if data.get("level"):
                            self.player.set_level(data.get("level"))
                        elif self.current_level:
                            self.player.set_level(self.current_level.__class__.__name__)
                            
                        print(f"{self.window_title}: Player teleported back at position {position}")
                        
                elif isinstance(data, dict) and data.get("type") == "level_change":
                    level_name = data.get("level_name")
                    if level_name == "Level1":
                        from levels.level1 import Level1
                        self.current_level = Level1(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")
                    elif level_name == "Level2":  
                        from levels.level2 import Level2
                        self.current_level = Level2(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")
                    elif level_name == "Level3": 
                        from levels.level3 import Level3
                        self.current_level = Level3(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")
                    elif level_name == "Level_Selector":
                        from levels.level_selector import Level_Selector
                        self.current_level = Level_Selector(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Received level change to {level_name}")

                elif not self.has_player and isinstance(data, dict) and "side" in data:
                    self.has_player = True
                    
                    if data.get("side") == "right":
                        self.player = Character(x=0 + 5, y=data.get("relative", self.height//2))
                    elif data.get("side") == "left":
                        self.player = Character(x=self.width - Character().size - 5, y=data.get("relative", self.height//2))
                    elif data.get("side") == "bottom":
                        self.player = Character(x=data.get("relative", self.width//2), y=0 + 5)
                    elif data.get("side") == "top":
                        self.player = Character(x=data.get("relative", self.width//2), y=self.height - Character().size - 5)
                    
                    if data.get("level"):
                        self.player.set_level(data.get("level"))
                    elif self.current_level:
                        self.player.set_level(self.current_level.__class__.__name__)
                    
                    print(f"{self.window_title} received player at ({self.player.x}, {self.player.y})")
                    """

                    Synchronization:
                    If the player completes the level, we need to tell the other window

                    """
                elif isinstance(data, dict) and data.get("type") == "level_completed":
                    level_name = data.get("level_name")
                    if level_name == "Level_Selector" and self.window_title == "Window 1":
                        from levels.level_selector import Level_Selector
                        self.current_level = Level_Selector(self.width, self.height, self.width, self.height)
                        print(f"{self.window_title}: Switched to level selector due to completion notification")
                        
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
        
        if self.has_player and self.player:
            """

            Inter-Process Communication:
            Passing the player to the other window

            """
            self.player.handle_keys()
            self.player.update()
            
            transfer_occurred = False
            
            allow_transfer = not (self.current_level and self.current_level.__class__.__name__ == "Level_Selector")

            if allow_transfer and self.player.x + self.player.size >= self.width:

                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                if self.other_window_pos and self.transfer_send_pipe:
                    vert_aligned = abs(my_position[1] - self.other_window_pos[1]) < 150
                    horz_aligned = abs((my_position[0] + self.width) - self.other_window_pos[0]) < 150

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
                    vert_aligned = abs(my_position[1] - self.other_window_pos[1]) < 150 
                    horz_aligned = abs((self.other_window_pos[0] + self.width) - my_position[0]) < 150

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

            elif allow_transfer and self.player.y + self.player.size >= self.height:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                if self.other_window_pos and self.transfer_send_pipe:
                    horz_aligned = abs(my_position[0] - self.other_window_pos[0]) < 150
                    vert_aligned = abs((my_position[1] + self.height) - self.other_window_pos[1]) < 150

                    if horz_aligned and vert_aligned:
                        print(f"{self.window_title}: Attempting to pass player down to {other_win_title}")
                        pass_data = {
                            "side": "bottom",
                            "relative": self.player.x,
                            "level": self.current_level.__class__.__name__
                        }
                        try:
                            self.transfer_send_pipe.send(pass_data)
                            self.has_player = False
                            self.player = None
                            transfer_occurred = True
                        except (BrokenPipeError, OSError):
                            print(f"{self.window_title}: Error sending player, pipe may be closed.")
                            self.running = False

            elif allow_transfer and self.player.y <= 0:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                if self.other_window_pos and self.transfer_send_pipe:
                    horz_aligned = abs(my_position[0] - self.other_window_pos[0]) < 150
                    vert_aligned = abs(my_position[1] - (self.other_window_pos[1] + self.height)) < 150

                    if horz_aligned and vert_aligned:
                        print(f"{self.window_title}: Attempting to pass player up to {other_win_title}")
                        pass_data = {
                            "side": "top",
                            "relative": self.player.x,
                            "level": self.current_level.__class__.__name__
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down = True
        elif event.type == pygame.MOUSEBUTTONUP and self.mouse_down:
            self.mouse_down = False
            if self.current_level:
                self.current_level.handle_click(event.pos, self.window_title)
    
    def draw(self, screen):
        screen.fill(self.bg_color)
        
        if self.current_level:
            if self.window_title == "Window 1":
                self.current_level.draw_window1(screen, self.player if self.has_player else None)
            else:
                self.current_level.draw_window2(screen, self.player if self.has_player else None)
        else:
            if self.has_player and self.player:
                self.player.draw(screen)