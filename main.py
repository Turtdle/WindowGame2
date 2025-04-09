import pygame
import sys
import multiprocessing
from pygame._sdl2.video import Window
from character import Character

def create_window(window_title="Window", width=1000, height=1000, bg_color=(255, 255, 255), 
                  origin=False, window_positions=None, player_passing_queue=None):
    """Function to create a Pygame window in a separate process."""
    has_player = False
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(window_title)
    clock = pygame.time.Clock()
    
    if origin:
        has_player = True
        player = Character(x=width//2, y=height//2)
    
    running = True
    while running:
        
        if player_passing_queue and not player_passing_queue.empty():
            try:
                pass_data = player_passing_queue.get_nowait()
                if pass_data.get("destination") == window_title:
                    has_player = True
                    player = Character(x=0, y=0)  
                    
                    if pass_data.get("side") == "right":
                        player.x = player.size//2
                        player.y = pass_data.get("relative", height//2)
                    
                    # Add handling for other sides if needed
            except:
                pass  
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        window = Window.from_display_module()
        if window_positions is not None:
            window_positions[window_title] = window.position
            print(window_positions)
        if has_player:
            player.handle_keys()
            player.update()
            player.keep_in_bounds(width, height)
            
            if player.x + player.size >= width:
                
                if (window_title == "Window 1" and 
                    window_positions and "Window 2" in window_positions and
                    abs(window_positions["Window 1"][1] - window_positions["Window 2"][1]) < 100 and 
                    (window_positions["Window 1"][0] - window_positions["Window 2"][0]) < -950 and 
                    (window_positions["Window 1"][0] - window_positions["Window 2"][0]) > -1050):
                    
                    
                    pass_data = {
                        "side": "right",
                        "relative": player.y,
                        "destination": "Window 2"
                    }
                    player_passing_queue.put(pass_data)
                    has_player = False
                if (window_title == "Window 2" and 
                    window_positions and "Window 1" in window_positions and
                    abs(window_positions["Window 1"][1] - window_positions["Window 2"][1]) < 100 and 
                    (window_positions["Window 1"][0] - window_positions["Window 2"][0]) > 950 and 
                    (window_positions["Window 1"][0] - window_positions["Window 2"][0]) < 1050):
                    
                    
                    pass_data = {
                        "side": "right",
                        "relative": player.y,
                        "destination": "Window 1"
                    }
                    player_passing_queue.put(pass_data)
                    has_player = False
                
        
        screen.fill(bg_color)
        if has_player:
            player.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def main():
    manager = multiprocessing.Manager()
    window_positions = manager.dict()
    player_passing_queue = multiprocessing.Queue()
    
    window1_process = multiprocessing.Process(
        target=create_window,
        args=("Window 1",),
        kwargs={
            "bg_color": (255, 255, 255),
            "origin": True,
            "window_positions": window_positions,
            "player_passing_queue": player_passing_queue
        },
    )
    
    window2_process = multiprocessing.Process(
        target=create_window,
        args=("Window 2",),
        kwargs={
            "bg_color": (255, 255, 255),
            "window_positions": window_positions,
            "player_passing_queue": player_passing_queue
        }
    )
    
    window1_process.start()
    window2_process.start()
    
    window1_process.join()
    window2_process.join()
    
    sys.exit()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()