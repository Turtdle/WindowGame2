import pygame
import sys
import multiprocessing
from multiprocessing.connection import Connection # Import Connection for type hinting
from pygame._sdl2.video import Window
# Assuming character.py remains the same as provided in the original question
from character import Character 
import time # Import time for adding a small delay if needed

def create_window(window_title="Window", width=1000, height=1000, bg_color=(255, 255, 255), 
                  origin=False, 
                  send_pipe: Connection = None, # Pipe to send data TO the other process
                  recv_pipe: Connection = None  # Pipe to receive data FROM the other process
                  ):
    """Function to create a Pygame window in a separate process using Pipes."""
    has_player = False
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(window_title)
    clock = pygame.time.Clock()
    
    player = None # Initialize player to None
    if origin:
        has_player = True
        player = Character(x=width//2, y=height//2)
    
    other_window_pos = None # To store the position received from the other window
    my_window = Window.from_display_module()
    my_position = my_window.position

    running = True
    while running:
        
        # --- Receiving Data ---
        if recv_pipe and recv_pipe.poll(): # Check if there's data without blocking
            try:
                msg_type, data = recv_pipe.recv()
                
                if msg_type == "position":
                    other_window_pos = data
                    # print(f"{window_title} received position: {other_window_pos}") # Optional debug
                    
                elif msg_type == "player_pass":
                    if not has_player: # Only accept player if this window doesn't have one
                        pass_data = data
                        has_player = True
                        # Create player based on received side and relative position
                        if pass_data.get("side") == "right": # Means player entered from the LEFT
                            player = Character(x=0 + 5, y=pass_data.get("relative", height//2)) 
                        elif pass_data.get("side") == "left": # Means player entered from the RIGHT
                             player = Character(x=width - Character().size - 5, y=pass_data.get("relative", height//2))
                        # Add handling for top/bottom if needed
                        
                        print(f"{window_title} received player at ({player.x}, {player.y})") # Debug
                        
            except (EOFError, BrokenPipeError):
                print(f"{window_title}: Pipe connection closed.")
                running = False # Stop if the pipe breaks
            except Exception as e:
                print(f"{window_title}: Error receiving data: {e}")
                # Decide how to handle other potential errors, maybe continue or break
                # running = False 
                pass
                
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # --- Sending Window Position ---
        # Send current window position periodically
        # Using Window.from_display_module() repeatedly can be slow, get it once per frame
        current_pos = my_window.position
        if send_pipe and current_pos != my_position: # Only send if position changed
             my_position = current_pos
             try:
                 send_pipe.send(("position", my_position))
             except (BrokenPipeError, OSError):
                 print(f"{window_title}: Error sending position, pipe may be closed.")
                 running = False # Stop if the pipe breaks
        
        # --- Player Logic ---
        if has_player and player:
            player.handle_keys()
            player.update()
            # We modify keep_in_bounds slightly to allow transfer check *before* clamping
            
            # Check boundaries for player transfer BEFORE clamping position
            transfer_occurred = False

            # Check Right Edge
            if player.x + player.size >= width:
                other_win_title = "Window 2" if window_title == "Window 1" else "Window 1"
                # Check if windows are aligned horizontally for right-to-left transfer
                if other_window_pos and send_pipe:
                    # Check vertical alignment
                    vert_aligned = abs(my_position[1] - other_window_pos[1]) < 100 # Allow some vertical tolerance
                    # Check horizontal alignment (Other window is to the right)
                    # my_position[0] + width should be close to other_window_pos[0]
                    horz_aligned = abs((my_position[0] + width) - other_window_pos[0]) < 50 # Allow some pixel tolerance

                    if vert_aligned and horz_aligned:
                        print(f"{window_title}: Attempting to pass player right to {other_win_title}")
                        pass_data = {
                            "side": "right", # Player is exiting from the right side of *this* window
                            "relative": player.y,
                        }
                        try:
                            send_pipe.send(("player_pass", pass_data))
                            has_player = False
                            player = None # Remove player reference
                            transfer_occurred = True
                        except (BrokenPipeError, OSError):
                            print(f"{window_title}: Error sending player, pipe may be closed.")
                            running = False # Stop if the pipe breaks

            # Check Left Edge
            elif player.x <= 0:
                other_win_title = "Window 2" if window_title == "Window 1" else "Window 1"
                # Check if windows are aligned horizontally for left-to-right transfer
                if other_window_pos and send_pipe:
                     # Check vertical alignment
                    vert_aligned = abs(my_position[1] - other_window_pos[1]) < 100
                    # Check horizontal alignment (Other window is to the left)
                    # other_window_pos[0] + width should be close to my_position[0]
                    horz_aligned = abs((other_window_pos[0] + width) - my_position[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{window_title}: Attempting to pass player left to {other_win_title}")
                        pass_data = {
                            "side": "left", # Player is exiting from the left side of *this* window
                            "relative": player.y,
                        }
                        try:
                             send_pipe.send(("player_pass", pass_data))
                             has_player = False
                             player = None # Remove player reference
                             transfer_occurred = True
                        except (BrokenPipeError, OSError):
                             print(f"{window_title}: Error sending player, pipe may be closed.")
                             running = False # Stop if the pipe breaks
            
            # Add checks for Top/Bottom edges similarly if needed

            # Only keep in bounds if no transfer happened
            if has_player and player and not transfer_occurred:
                player.keep_in_bounds(width, height) # Now clamp position if still in this window
                
        
        # --- Drawing ---
        screen.fill(bg_color)
        if has_player and player:
            player.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    # --- Cleanup ---
    print(f"Closing {window_title}")
    if send_pipe:
        try:
            send_pipe.close()
        except Exception as e:
             print(f"{window_title}: Error closing send_pipe: {e}")
    if recv_pipe:
        try:
            recv_pipe.close()
        except Exception as e:
            print(f"{window_title}: Error closing recv_pipe: {e}")
            
    pygame.quit()

def main():
    # Create two pipes:
    # pipe_1_recv: Window 1 receives from this
    # pipe_1_send: Window 2 sends to this (connected to pipe_1_recv)
    pipe_1_recv, pipe_1_send = multiprocessing.Pipe(duplex=False)

    # pipe_2_recv: Window 2 receives from this
    # pipe_2_send: Window 1 sends to this (connected to pipe_2_recv)
    pipe_2_recv, pipe_2_send = multiprocessing.Pipe(duplex=False)

    window1_process = multiprocessing.Process(
        target=create_window,
        args=("Window 1",),
        kwargs={
            "bg_color": (240, 240, 255), # Slightly different color for distinction
            "origin": True, # Start player in Window 1
            "send_pipe": pipe_2_send,   # Window 1 sends data TO Window 2
            "recv_pipe": pipe_1_recv    # Window 1 receives data FROM Window 2
        },
    )
    
    window2_process = multiprocessing.Process(
        target=create_window,
        args=("Window 2",),
        kwargs={
            "bg_color": (255, 240, 240), # Slightly different color for distinction
            "origin": False, # No player initially
            "send_pipe": pipe_1_send,   # Window 2 sends data TO Window 1
            "recv_pipe": pipe_2_recv    # Window 2 receives data FROM Window 1
        }
    )
    
    print("Starting processes...")
    window1_process.start()
    # Give window 1 a moment to initialize before starting window 2
    # This can sometimes help prevent race conditions on startup or display init issues
    time.sleep(0.5) 
    window2_process.start()
    
    # --- Close unused pipe ends in the parent process ---
    # This is important for proper cleanup and signaling
    print("Closing parent pipe ends...")
    try:
        pipe_1_recv.close()
        pipe_1_send.close()
        pipe_2_recv.close()
        pipe_2_send.close()
        print("Parent pipe ends closed.")
    except Exception as e:
        print(f"Error closing parent pipe ends: {e}")

    
    print("Waiting for processes to join...")
    window1_process.join()
    print("Window 1 joined.")
    window2_process.join()
    print("Window 2 joined.")
    
    print("Exiting main application.")
    sys.exit()

if __name__ == "__main__":
    # Ensure compatibility with freezing (e.g., PyInstaller)
    multiprocessing.freeze_support() 
    main()