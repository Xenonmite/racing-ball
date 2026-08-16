import pygame

sounds = {
    "fire": pygame.Sound("assets/sfx/fire.wav"),
    "enemy_hit": pygame.Sound("assets/sfx/enemy_hit.wav"),
    "player_hit": pygame.Sound("assets/sfx/player_hit.wav"),
    "player_die": pygame.Sound("assets/sfx/player_die.wav"),
    "enemy_shoot": pygame.Sound("assets/sfx/enemy_shoot.wav"),
    "heal": pygame.Sound("assets/sfx/heal.wav")
}

sound_groups = {
    "enemy_die": [
        pygame.Sound("assets/sfx/enemy_die1.wav"),
        pygame.Sound("assets/sfx/enemy_die2.wav"),
        pygame.Sound("assets/sfx/enemy_die3.wav"),
        pygame.Sound("assets/sfx/enemy_die4.wav"),
        pygame.Sound("assets/sfx/enemy_die5.wav")
    ]
}

sounds["fire"].set_volume(0.2)
sounds["enemy_hit"].set_volume(0.1)
sounds["player_hit"].set_volume(0.25)
sounds["player_die"].set_volume(0.2)
sounds["enemy_shoot"].set_volume(0.1)
sounds["heal"].set_volume(0.4)

for sfx in sound_groups["enemy_die"]: sfx.set_volume(0.2)

font: pygame.Font = pygame.font.Font("assets/VCR_OSD_MONO_1.001.ttf", 20)
big_font: pygame.Font = pygame.font.Font("assets/VCR_OSD_MONO_1.001.ttf", 50)

debug_mode: bool = False

enemy_multiplier: float = 0.8

def lerp(a, b, x):
    return a + (b - a) * x

def clamp(x, min_num, max_num):
    return max(min(x, max_num), min_num)

MUSIC_END = pygame.event.custom_type()