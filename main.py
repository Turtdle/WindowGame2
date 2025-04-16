import pygame
import sys
import multiprocessing
from multiprocessing.connection import Connection
from pygame._sdl2.video import Window
from character import Character 
import time

def create_window(window_title="Window", width=1000, height=1000, bg_color=(255, 255, 255), 
                  origin=False, 
                  send_pipe: Connection = None,
                  recv_pipe: Connection = None):
    has_player = False
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(window_title)
    clock = pygame.time.Clock()
    
    player = None
    if origin:
        has_player = True
        player = Character(x=width//2, y=height//2)
    
    other_window_pos = None
    my_window = Window.from_display_module()
    my_position = my_window.position

    running = True
    while running:
        
        if recv_pipe and recv_pipe.poll():
            try:
                msg_type, data = recv_pipe.recv()
                
                if msg_type == "position":
                    other_window_pos = data
                    
                elif msg_type == "player_pass":
                    if not has_player:
                        pass_data = data
                        has_player = True
                        
                        if pass_data.get("side") == "right":
                            player = Character(x=0 + 5, y=pass_data.get("relative", height//2)) 
                        elif pass_data.get("side") == "left":
                             player = Character(x=width - Character().size - 5, y=pass_data.get("relative", height//2))
                        
                        print(f"{window_title} received player at ({player.x}, {player.y})")
                        
            except (EOFError, BrokenPipeError):
                print(f"{window_title}: Pipe connection closed.")
                running = False
            except Exception as e:
                print(f"{window_title}: Error receiving data: {e}")
                pass
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        current_pos = my_window.position
        if send_pipe and current_pos != my_position:
             my_position = current_pos
             try:
                 send_pipe.send(("position", my_position))
             except (BrokenPipeError, OSError):
                 print(f"{window_title}: Error sending position, pipe may be closed.")
                 running = False
        
        if has_player and player:
            player.handle_keys()
            player.update()
            
            transfer_occurred = False

            if player.x + player.size >= width:
                other_win_title = "Window 2" if window_title == "Window 1" else "Window 1"
                if other_window_pos and send_pipe:
                    vert_aligned = abs(my_position[1] - other_window_pos[1]) < 100
                    horz_aligned = abs((my_position[0] + width) - other_window_pos[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{window_title}: Attempting to pass player right to {other_win_title}")
                        pass_data = {
                            "side": "right",
                            "relative": player.y,
                        }
                        try:
                            send_pipe.send(("player_pass", pass_data))
                            has_player = False
                            player = None
                            transfer_occurred = True
                        except (BrokenPipeError, OSError):
                            print(f"{window_title}: Error sending player, pipe may be closed.")
                            running = False

            elif player.x <= 0:
                other_win_title = "Window 2" if window_title == "Window 1" else "Window 1"
                if other_window_pos and send_pipe:
                    vert_aligned = abs(my_position[1] - other_window_pos[1]) < 100
                    horz_aligned = abs((other_window_pos[0] + width) - my_position[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{window_title}: Attempting to pass player left to {other_win_title}")
                        pass_data = {
                            "side": "left",
                            "relative": player.y,
                        }
                        try:
                             send_pipe.send(("player_pass", pass_data))
                             has_player = False
                             player = None
                             transfer_occurred = True
                        except (BrokenPipeError, OSError):
                             print(f"{window_title}: Error sending player, pipe may be closed.")
                             running = False
            
            if has_player and player and not transfer_occurred:
                player.keep_in_bounds(width, height)
                
        screen.fill(bg_color)
        if has_player and player:
            player.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
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
    pipe_1_recv, pipe_1_send = multiprocessing.Pipe(duplex=False)
    pipe_2_recv, pipe_2_send = multiprocessing.Pipe(duplex=False)

    window1_process = multiprocessing.Process(
        target=create_window,
        args=("Window 1",),
        kwargs={
            "bg_color": (240, 240, 255),
            "origin": True,
            "send_pipe": pipe_2_send,
            "recv_pipe": pipe_1_recv
        },
    )
    
    window2_process = multiprocessing.Process(
        target=create_window,
        args=("Window 2",),
        kwargs={
            "bg_color": (255, 240, 240),
            "origin": False,
            "send_pipe": pipe_1_send,
            "recv_pipe": pipe_2_recv
        }
    )
    
    print("Starting processes...")
    window1_process.start()
    time.sleep(0.5) 
    window2_process.start()
    
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
    multiprocessing.freeze_support() 
    main()