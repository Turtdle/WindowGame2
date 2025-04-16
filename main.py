import pygame
import sys
import multiprocessing
from multiprocessing.connection import Connection
from pygame._sdl2.video import Window
from character import Character 
import time

def create_window(window_title="Window", width=1000, height=1000, bg_color=(255, 255, 255), 
                  origin=False, 
                  pos_send_pipe: Connection = None,
                  pos_recv_pipe: Connection = None,
                  transfer_send_pipe: Connection = None,
                  transfer_recv_pipe: Connection = None):
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
        
        if pos_recv_pipe and pos_recv_pipe.poll():
            try:
                other_window_pos = pos_recv_pipe.recv()
            except (EOFError, BrokenPipeError):
                print(f"{window_title}: Position pipe connection closed.")
                running = False
            except Exception as e:
                print(f"{window_title}: Error receiving position data: {e}")
                pass
                
        if transfer_recv_pipe and transfer_recv_pipe.poll():
            try:
                data = transfer_recv_pipe.recv()
                if not has_player:
                    pass_data = data
                    has_player = True
                    
                    if pass_data.get("side") == "right":
                        player = Character(x=0 + 5, y=pass_data.get("relative", height//2)) 
                    elif pass_data.get("side") == "left":
                         player = Character(x=width - Character().size - 5, y=pass_data.get("relative", height//2))
                    
                    print(f"{window_title} received player at ({player.x}, {player.y})")
                    
            except (EOFError, BrokenPipeError):
                print(f"{window_title}: Transfer pipe connection closed.")
                running = False
            except Exception as e:
                print(f"{window_title}: Error receiving transfer data: {e}")
                pass
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        current_pos = my_window.position
        if pos_send_pipe and current_pos != my_position:
             my_position = current_pos
             try:
                print(f'window: {window_title} is sending position')
                pos_send_pipe.send(my_position)
             except (BrokenPipeError, OSError):
                print(f"{window_title}: Error sending position, pipe may be closed.")
                running = False
        
        if has_player and player:
            player.handle_keys()
            player.update()
            
            transfer_occurred = False

            if player.x + player.size >= width:
                other_win_title = "Window 2" if window_title == "Window 1" else "Window 1"
                print(other_win_title)
                if other_window_pos and transfer_send_pipe:
                    vert_aligned = abs(my_position[1] - other_window_pos[1]) < 100
                    horz_aligned = abs((my_position[0] + width) - other_window_pos[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{window_title}: Attempting to pass player right to {other_win_title}")
                        pass_data = {
                            "side": "right",
                            "relative": player.y,
                        }
                        try:
                            transfer_send_pipe.send(pass_data)
                            has_player = False
                            player = None
                            transfer_occurred = True
                        except (BrokenPipeError, OSError):
                            print(f"{window_title}: Error sending player, pipe may be closed.")
                            running = False
                    else:
                        print("not aligned")
                else:
                    print(f'outer win pos is; {other_window_pos}, transfer send pipe is: {transfer_send_pipe}')
            elif player.x <= 0:
                other_win_title = "Window 2" if window_title == "Window 1" else "Window 1"
                print(other_win_title)
                if other_window_pos and transfer_send_pipe:
                    vert_aligned = abs(my_position[1] - other_window_pos[1]) < 100 
                    horz_aligned = abs((other_window_pos[0] + width) - my_position[0]) < 50

                    if vert_aligned and horz_aligned:
                        print(f"{window_title}: Attempting to pass player left to {other_win_title}") 
                        pass_data = {
                            "side": "left",
                            "relative": player.y,
                        }
                        try:
                             transfer_send_pipe.send(pass_data)
                             has_player = False
                             player = None
                             transfer_occurred = True
                        except (BrokenPipeError, OSError):
                             print(f"{window_title}: Error sending player, pipe may be closed.")
                             running = False
                    else:
                        print("not aligned")
                else:
                    print(f'outer win pos is; {other_window_pos}, transfer send pipe is: {transfer_send_pipe}')
            
            if has_player and player and not transfer_occurred:
                player.keep_in_bounds(width, height)
                
        screen.fill(bg_color)
        if has_player and player:
            player.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    print(f"Closing {window_title}")
    if pos_send_pipe:
        try:
            pos_send_pipe.close()
        except Exception as e:
             print(f"{window_title}: Error closing pos_send_pipe: {e}")
    if pos_recv_pipe:
        try:
            pos_recv_pipe.close()
        except Exception as e:
            print(f"{window_title}: Error closing pos_recv_pipe: {e}")
            
    if transfer_send_pipe:
        try:
            transfer_send_pipe.close()  
        except Exception as e:
            print(f"{window_title}: Error closing transfer_send_pipe: {e}")
    if transfer_recv_pipe:
        try:
            transfer_recv_pipe.close()
        except Exception as e:
            print(f"{window_title}: Error closing transfer_recv_pipe: {e}")
            
    pygame.quit()

def main():
    pos_pipe_1_recv, pos_pipe_1_send = multiprocessing.Pipe(duplex=False)
    pos_pipe_2_recv, pos_pipe_2_send = multiprocessing.Pipe(duplex=False)
    transfer_pipe_1_recv, transfer_pipe_1_send = multiprocessing.Pipe(duplex=False)  
    transfer_pipe_2_recv, transfer_pipe_2_send = multiprocessing.Pipe(duplex=False)

    window1_process = multiprocessing.Process(
        target=create_window,
        args=("Window 1",),    
        kwargs={
            "bg_color": (240, 240, 255),
            "origin": True,
            "pos_send_pipe": pos_pipe_2_send,
            "pos_recv_pipe": pos_pipe_1_recv,
            "transfer_send_pipe": transfer_pipe_2_send,
            "transfer_recv_pipe": transfer_pipe_1_recv
        },
    )
    
    window2_process = multiprocessing.Process(
        target=create_window, 
        args=("Window 2",),
        kwargs={
            "bg_color": (255, 240, 240),
            "origin": False,
            "pos_send_pipe": pos_pipe_1_send,
            "pos_recv_pipe": pos_pipe_2_recv,
            "transfer_send_pipe": transfer_pipe_1_send,
            "transfer_recv_pipe": transfer_pipe_2_recv  
        }
    )
    
    print("Starting processes...")
    window1_process.start()
    time.sleep(0.5) 
    window2_process.start()
    
    print("Closing parent pipe ends...")
    try:
        pos_pipe_1_recv.close() 
        pos_pipe_1_send.close()
        pos_pipe_2_recv.close()
        pos_pipe_2_send.close()
        transfer_pipe_1_recv.close()
        transfer_pipe_1_send.close()
        transfer_pipe_2_recv.close()  
        transfer_pipe_2_send.close()
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