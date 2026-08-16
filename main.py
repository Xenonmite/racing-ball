import random, math, time, pygame, traceback
from colorama import Fore
pygame.mixer.init()
pygame.init()
from assets.global_vars import MUSIC_END

from assets.main_loop import init_game, do_main_loop

WIDTH: int = 1040
HEIGHT: int = 720

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Racing ball")
pygame.mouse.set_visible(0)

icon = pygame.image.load("assets/spr/icon.png")
pygame.display.set_icon(icon)

fps: int = 60

clock = pygame.time.Clock()
running: bool = True

try:
    init_game(WIDTH, HEIGHT)
except Exception as e:
    print(f"Exception in init_game:{Fore.RED}", *traceback.format_exc(e), f"{Fore.RESET}")
    pygame.mixer.quit()
    input("\n   press ENTER to close")
    running = False

resize_flag: bool = False
music_end_flag: bool = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        
        if event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            WIDTH = window.get_width()
            HEIGHT = window.get_height()
            resize_flag = True
            
        if event.type == MUSIC_END:
            music_end_flag = True
            
    clock.tick(fps)
    
    try:
        do_main_loop(window, WIDTH, HEIGHT, resize_flag, music_end_flag)
    except Exception as e:
        print(f"Exception in do_main_loop:{Fore.RED}", *traceback.format_exception(e), f"{Fore.RESET}")
        pygame.mixer.quit()
        input("\n   press ENTER to close")
        running = False
        break
    
    resize_flag = False
    music_end_flag = False
    

pygame.quit()