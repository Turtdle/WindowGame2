import pygame
import sys
import multiprocessing
from multiprocessing.connection import Connection
from pygame._sdl2.video import Window
from character import Character 
import time
from window import WindowClass
from levels.level_selector import Level_Selector

def create_window(window_title="Window", width=1000, height=1000, bg_color=(255, 255, 255), 
                  origin=False, 
                  pos_send_pipe: Connection = None,
                  pos_recv_pipe: Connection = None,
                  transfer_send_pipe: Connection = None,
                  transfer_recv_pipe: Connection = None):
        
    print(f"Creating {window_title}...")

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(window_title)
    clock = pygame.time.Clock()
    
    # Create the level selector
    level_selector = Level_Selector(width, height, width, height)
    
    window = WindowClass(window_title=window_title, width=width, height=height, bg_color=bg_color,
                    origin=origin, 
                    pos_send_pipe=pos_send_pipe,
                    pos_recv_pipe=pos_recv_pipe,
                    transfer_send_pipe=transfer_send_pipe,
                    transfer_recv_pipe=transfer_recv_pipe,
                    my_window=Window.from_display_module(),
                    current_level=level_selector,
                    running=True)
    
    try:
        while window.running:
            window.tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    window.running = False
                    # Signal to the other window that we're closing
                    if transfer_send_pipe:
                        try:
                            transfer_send_pipe.send({"type": "window_closing"})
                        except:
                            pass
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        window.running = False
                        # Signal to the other window that we're closing
                        if transfer_send_pipe:
                            try:
                                transfer_send_pipe.send({"type": "window_closing"})
                            except:
                                pass
                
                # Pass other events to the window
                window.handle_event(event)
            
            # Draw the window
            window.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
    finally:
        # Always clean up resources
        print(f"Closing {window_title}")
        try:
            if transfer_send_pipe and not transfer_send_pipe.closed:
                transfer_send_pipe.send({"type": "window_closing"})
        except:
            pass  # Ignore errors during shutdown
        
        # Close pipes with better error handling
        for pipe in [pos_send_pipe, pos_recv_pipe, transfer_send_pipe, transfer_recv_pipe]:
            if pipe:
                try:
                    if not pipe.closed:
                        pipe.close()
                except Exception as e:
                    print(f"{window_title}: Error closing pipe: {e}")
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