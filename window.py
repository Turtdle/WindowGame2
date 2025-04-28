from multiprocessing.connection import Connection
from character import Character
from pygame._sdl2.video import Window

class WindowClass:
    def __init__(self, window_title="Window", width=1000, height=1000, bg_color=(255, 255, 255), 
                  origin=False, 
                  pos_send_pipe: Connection = None,
                  pos_recv_pipe: Connection = None,
                  transfer_send_pipe: Connection = None,
                  transfer_recv_pipe: Connection = None,
                  my_window=None):
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
        if self.origin:
            self.has_player = True
            self.player = Character(x=width//2, y=height//2)

    def tick(self):
    
        if self.pos_recv_pipe and self.pos_recv_pipe.poll():
            try:
                self.other_window_pos = self.pos_recv_pipe.recv()
            except (EOFError, BrokenPipeError):
                print(f"{self.window_title}: Position pipe connection closed.")
                running = False
            except Exception as e:
                print(f"{self.window_title}: Error receiving position data: {e}")
                pass
                
        if self.transfer_recv_pipe and self.transfer_recv_pipe.poll():
            try:
                data = self.transfer_recv_pipe.recv()
                if not self.has_player:
                    pass_data = data
                    self.has_player = True
                    
                    if pass_data.get("side") == "right":
                        self.player = Character(x=0 + 5, y=pass_data.get("relative", self.height//2)) 
                    elif pass_data.get("side") == "left":
                        self.player = Character(x=self.width - Character().size - 5, y=pass_data.get("relative", self.height//2))
                    
                    print(f"{self.window_title} received player at ({self.player.x}, {self.player.y})")
                    
            except (EOFError, BrokenPipeError):
                print(f"{self.window_title}: Transfer pipe connection closed.")
                running = False
            except Exception as e:
                print(f"{self.window_title}: Error receiving transfer data: {e}")
                pass

        current_pos = self.my_window.position
        if True:
             my_position = current_pos
             try:
                #print(f'window: {window_title} is sending position')
                self.pos_send_pipe.send(my_position)
             except (BrokenPipeError, OSError):
                print(f"{self.window_title}: Error sending position, pipe may be closed.")
                running = False
        
        if self.has_player and self.player:
            self.player.handle_keys()
            self.player.update()
            
            transfer_occurred = False

            if self.player.x + self.player.size >= self.width:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                print(other_win_title)
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
                            running = False
                    else:
                        print("not aligned")
                else:
                    print(f'outer win pos is; {self.other_window_pos}, transfer send pipe is: {self.transfer_send_pipe}')
            elif self.player.x <= 0:
                other_win_title = "Window 2" if self.window_title == "Window 1" else "Window 1"
                print(other_win_title)
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
                             running = False
                    else:
                        print("not aligned")
                else:
                    print(f'outer win pos is; {self.other_window_pos}, transfer send pipe is: {self.transfer_send_pipe}')
            
            if self.has_player and self.player and not transfer_occurred:
                self.player.keep_in_bounds(self.width, self.height)
                
