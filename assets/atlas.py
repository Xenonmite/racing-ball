import pygame

class Atlas:
    def __init__(self, path: str):
        self.path: str = path
        self.sprite: pygame.Surface = pygame.image.load(path)
        
    def get_sprite(self, rect: list[int, int, int, int], scale: int = 1) -> pygame.Surface:
        spr = self.sprite.subsurface(rect)
        return pygame.transform.scale_by(spr, scale)
    
    def get_sprite_strip(self, first_sprite_rect: list[int, int, int, int], sprite_amount: int, scale: int = 1) -> list[pygame.Surface]:
        first_sprite_rect = list(first_sprite_rect)
        spr_list = []
        left_point = first_sprite_rect[0]
        
        for i in range(sprite_amount):
            first_sprite_rect[0] = left_point + first_sprite_rect[2] * i
            spr = self.sprite.subsurface(first_sprite_rect)
            spr = pygame.transform.scale_by(spr, scale)
            spr_list.append(spr)
            
        return spr_list
    
main_atlas: Atlas = Atlas("assets/spr/atlas.png")