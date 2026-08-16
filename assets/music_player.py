import pygame, os, traceback, random
from colorama import Fore
from assets.global_vars import MUSIC_END
from assets.eventboard_text import Eventboard_text

class Music_player:
    def __init__(self, music_folder_path):
        self.music_path_list = []
        
        files = os.listdir(music_folder_path)
        if len(files) == 0:
            print(f"{Fore.YELLOW}No music found in folder {music_folder_path}{Fore.RESET}")
        else:
            print(f"{Fore.CYAN}Found {len(files)} musics in folder {music_folder_path}{Fore.RESET}")
        
        for file in files:
            self.music_path_list.append(music_folder_path + file)
            print(f"{Fore.CYAN}{file}{Fore.RESET}")
                    
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        self.unplayed_songs = self.music_path_list.copy()
        self.last_song = None
        
        pygame.mixer.music.set_endevent(MUSIC_END)
        
    def play_a_music(self, path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            Eventboard_text(f"{path.split("/")[-1]}", color="#23d17c")
            return True
                
        except Exception as e:
            print(f"{Fore.YELLOW}Could not play {path} :", *traceback.format_exc(e), f"{Fore.RESET}")
            return False
            
            
    def play_random(self):
        if len(self.unplayed_songs) <= 0:
            self.unplayed_songs = self.music_path_list.copy()
            
        if self.last_song != None and self.last_song in self.unplayed_songs:
            self.unplayed_songs.remove(self.last_song)
            
        chosen_music = random.choice(self.unplayed_songs)
        self.unplayed_songs.remove(chosen_music)
        self.last_song = chosen_music
        
        self.play_a_music(chosen_music)
    
    def pause(self):
        pygame.mixer.music.pause()
        self.is_paused = True
        Eventboard_text(f"Music off", 100, color="#BCBD91")
        
    
    def resume(self):
        pygame.mixer.music.unpause()
        self.is_paused = False
        Eventboard_text(f"Music on", 100, color="#BCBD91")
        
    
    def update_volume(self):
        pygame.mixer.music.set_volume(self.volume)
        Eventboard_text(f"Mus volume {round(self.volume, 1)}", 100, color="#BCBD91")
        
        