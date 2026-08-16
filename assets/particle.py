import pygame
from pygame.math import Vector2 as vec2
from random import random
from assets.global_vars import lerp

class Particle:
    particle_list: list[Particle] = []
    
    def spawn_particle_burst_round(center_pos: vec2, max_start_vel: vec2, color: tuple[int, int, int], max_age: int = 100, size: int = 5, damp: int = 1.01, amount: int = 10):
        for _ in range(amount):
            Particle(center_pos, vec2((random()*2 - 1) * max_start_vel.x, (random()*2 - 1) * max_start_vel.y), color, size, max_age, damp)
            
    def spawn_particle_burst_directed(center_pos: vec2, max_start_vel: vec2, centre_angle: float, max_angle_deviation: float, color: str, max_age: int, size: int, damp: int = 1.01, amount: int = 10):
        for _ in range(amount):
            angle = centre_angle + (random()*2 - 1) * max_angle_deviation
            Particle(center_pos, vec2(1, 0).rotate(angle) * max_start_vel.x*random(), color, size, max_age, damp)
            
    def spawn_particle_line(pos1: vec2, pos2: vec2, max_start_vel: vec2, color: str, max_age: int, size: int, damp: int = 1.01, amount: int = 10):
        for i in range(amount):
            Particle(lerp(pos1, pos2, (i + 1) / amount), vec2((random()*2 - 1) * max_start_vel.x, (random()*2 - 1) * max_start_vel.y), color, size, max_age, damp)
        
        
            
    def update_all_particles(draw_surface: pygame.Surface, game_speed):
        for particle in Particle.particle_list:
            particle.update(draw_surface, game_speed)
    
    def __init__(self, pos: vec2, start_vel: vec2, color: str, size: int, max_age: int, damp: int = 1.01):
        self.pos = pos.copy()
        self.vel = start_vel
        self.color = color
        self.damp = damp
        self.size = size
        self.max_age = max_age
        self.age = 0
        
        Particle.particle_list.append(self)
        
    def move(self, game_speed):
        self.vel /= self.damp
        self.pos += self.vel * game_speed
        
    def draw_on(self, draw_surface: pygame.Surface):
        pygame.draw.circle(draw_surface, self.color, self.pos, self.size * (1 - (self.age / self.max_age)))
        
    def update(self, draw_surface: pygame.Surface, game_speed):
        self.age += 1 * game_speed
        if self.age > self.max_age:
            Particle.particle_list.remove(self)
            del self
            
        else:
            self.move(game_speed)
            self.draw_on(draw_surface)
            
