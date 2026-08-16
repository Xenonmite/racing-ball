import pygame
from pygame.math import Vector2 as vec2
from random import random
from assets.particle import Particle
from assets.atlas import main_atlas

class Projectile:
    projectile_list: list[Projectile] = []
    
    def __init__(self, pos: vec2, vel: vec2, size: int, is_player_launched: bool = True, damage: int = 4):
        self.pos = pos.copy()
        self.vel = vel
        self.size = size
        self.angle = -self.vel.angle
        self.is_played_launched = is_player_launched
        self.damage = damage
        
        if is_player_launched:
            self.sprite = pygame.transform.rotate(main_atlas.get_sprite([90, 0, 9, 9], 2), self.angle)
        else:
            self.sprite = pygame.transform.rotate(main_atlas.get_sprite([100, 0, 9, 9], 2), self.angle)
        
        #self.rect = pygame.rect.Rect(self.pos.x, self.pos.y, size, size)
            
        Projectile.projectile_list.append(self)
        
    def update(self, draw_surface: pygame.Surface, game_speed):
        self.pos += self.vel * game_speed
        #self.rect.center += self.vel
        #pygame.draw.circle(draw_surface, (255, 255, 255), self.pos, self.size, 1)
        draw_surface.blit(self.sprite, self.pos.elementwise() - self.size)
        #Particle(self.pos, vec2(0, 0), (180, 180, 180), 5, 5)
        
    def kill(self):
        Projectile.projectile_list.remove(self)
        del self