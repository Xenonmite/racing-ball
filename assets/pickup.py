import pygame
from pygame.math import Vector2 as vec2
from random import random
from assets.particle import Particle
from assets.player import Player

class Pickup(Particle):
    pickup_list: list[Pickup] = []
    
    def __init__(self, pos: vec2, vel: vec2, sprite: pygame.Surface, pickup_range: int = 80, max_age: int = 600, thing: str = "fuel", amount: int = 1):
        self.pickup_range = pickup_range
        self.thing = thing
        self.amount = amount
        self.sprite = sprite
        super().__init__(pos, vel, "#000000", 10, max_age)
        self.age = 0
        Pickup.pickup_list.append(self)
        Particle.particle_list.remove(self)
        
    def update(self, player: Player, game_speed) -> bool:
        self.age += 1 * game_speed
        if self.age >= self.max_age:
            self.kill()
            return False
        
        if self.pos.distance_to(player.pos) < self.pickup_range:
            self.vel += (player.pos - self.pos).normalize() / self.pos.distance_to(player.pos) * self.pickup_range / 2.5
            
        self.vel /= 1.033
        self.pos += self.vel * game_speed
            
        if self.pos.distance_to(player.pos) < player.hit_radius + 3:
            return True
        
    def draw_on(self, draw_surface: pygame.Surface):
        if self.age/self.max_age <= 0.75 or self.age % 15 < 7:
        
            draw_surface.blit(self.sprite, self.pos - vec2(self.sprite.size))
        #pygame.draw.circle(draw_surface, (255, 255, 0), self.pos, 5, 3)
            
    def kill(self):
        Pickup.pickup_list.remove(self)
        del self