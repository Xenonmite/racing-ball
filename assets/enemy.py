import pygame, math
from pygame.math import Vector2 as vec2
import assets.atlas as atlas
import random
from assets.global_vars import sounds, font, debug_mode, enemy_multiplier, sound_groups
from assets.particle import Particle

class Enemy:
    enemy_list: list[Enemy] = []
    alive_enemy_list: list[Enemy] = []
    
    # amount of non-full hp sprites
    damage_states: int = 3
    sprite_list: list[pygame.Surface] = atlas.main_atlas.get_sprite_strip([10, 20, 10, 10], 4, 2)
    spawn_hint: pygame.Surface = atlas.main_atlas.get_sprite([0, 20, 10, 10], 2)
    
    starting_wave = 0
    
    def __init__(self, pos: vec2, hp_multiplier:int = 1):
        self.is_player = False
        self.pos = pos
        self.vel = vec2(0, 0)
        self.dir = vec2(0, 0)
        self.acc = vec2(0.2, 0.2)
        self.drag = 1.01
        self.hit_radius: int = 10
        self.alive = True
        self.dead_despawn_timer = 300
        
        self.hp_multiplier = hp_multiplier
        self.base_hp: float = 60.0
        self.start_hp: float = self.base_hp * hp_multiplier
        self.hp: float = self.start_hp
        
        self.dropped_fuel = 8
        self.score_given = 240
        self.mass = 1.8
        
        Enemy.enemy_list.append(self)
        Enemy.alive_enemy_list.append(self)
        
        
    def get_spawn_amount(wave: int):
        return round(wave**0.8 * enemy_multiplier + 1)
        

    def draw_on(self, draw_surface: pygame.Surface):
        if self.hp > self.start_hp:
            drawn_sprite: pygame.Surface = self.__class__.sprite_list[0]
            
        elif self.hp > 0:
            drawn_sprite: pygame.Surface = self.__class__.sprite_list[int(-self.hp / self.start_hp * self.__class__.damage_states + self.__class__.damage_states)]
            
        else:
            drawn_sprite: pygame.Surface = self.__class__.sprite_list[-1]
            
        draw_surface.blit(drawn_sprite, self.pos.elementwise() - self.hit_radius)
            
        if debug_mode and not self.is_player:
            self.hp_text = font.render(str(round(self.hp, 1)), False, (255, 100, 0))
            draw_surface.blit(self.hp_text, self.pos + vec2(-20, -30))


    def update_speed(self, player: Enemy):
        self.dir = (player.pos - self.pos).normalize()
        self.vel += self.dir.elementwise() * self.acc
        

    def update_pos(self, game_speed: float):
        self.vel /= self.drag
        self.pos += self.vel * game_speed


    def edge_collision(self, width: int, height: int):
        # >| right
        if self.pos.x > width - self.hit_radius:
            self.pos.x = width - self.hit_radius
            self.vel.x *= -0.9

        # |< left
        if self.pos.x < self.hit_radius:
            self.pos.x = self.hit_radius
            self.vel.x *= -0.9

        # ‾^‾ top
        if self.pos.y < self.hit_radius:
            self.pos.y = self.hit_radius
            self.vel.y *= -0.9

        # _v_ bottom
        if self.pos.y > height - self.hit_radius:
            self.pos.y = height - self.hit_radius
            self.vel.y *= -0.9


    def update(self, target: Enemy, win_width: int, win_height: int, game_speed: float):
        if self.hp <= 0 and self.alive:
            self.alive = False
            random.choice(sound_groups["enemy_die"]).play()
            Particle.spawn_particle_burst_round(self.pos, vec2(4, 4), "#dd4411", damp=1.03, size=5)
            Enemy.alive_enemy_list.remove(self)
            
        if self.alive:
            self.update_speed(target)
            
        self.update_pos(game_speed)
        self.edge_collision(win_width, win_height)
        
        
        if not self.alive:
            self.dead_despawn_timer -= 1 * game_speed
            if self.dead_despawn_timer <= 0:
                Enemy.enemy_list.remove(self)
                del self
                