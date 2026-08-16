import pygame
from pygame.math import Vector2 as vec2
from assets.enemy import Enemy
from assets.particle import Particle
import assets.atlas as atlas
from assets.global_vars import sounds, font

class Player(Enemy):
    damage_states = 7
    sprite_list: list[pygame.Surface] = atlas.main_atlas.get_sprite_strip([0, 0, 10, 10], 8, 2)
    
    def __init__(self, pos: vec2):
        self.pos = pos
        
        super().__init__(pos)
        self.enemy_list.remove(self)
        self.alive_enemy_list.remove(self)
        self.is_player = True
        
        self.acc = vec2(0.5, 0.5)
        
        self.hp: float = 50.0
        self.start_hp = self.hp
        self.fuel: float = 40.0
        self.dying_timer = 3.0
        self.has_died = False
        self.inv_frames: int = 0
        
        self.active: bool = False
        
        self.drag = 1.02
        
        self.heal_hold_frames_left: int = 70
        
        self.low_hp_alert = atlas.main_atlas.get_sprite([64, 64, 16, 16], 2)
        self.low_fuel_alert = atlas.main_atlas.get_sprite([80, 64, 16, 16], 2)
        
        
    def update_speed(self):
        self.active = False
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.dir.x = -1
            self.active = True
            
        elif keys[pygame.K_d]or keys[pygame.K_RIGHT]:
            self.dir.x = 1
            self.active = True
            
        else:
            self.dir.x = 0
            
        if keys[pygame.K_w]or keys[pygame.K_UP]:
            self.dir.y = -1
            self.active = True
            
        elif keys[pygame.K_s]or keys[pygame.K_DOWN]:
            self.dir.y = 1
            self.active = True
            
        else:
            self.dir.y = 0
            
        if keys[pygame.K_SPACE]:
            self.vel /= 2
            
        if keys[pygame.K_c] and self.hp > 0 and self.fuel > 0 and self.hp < 150:
            self.heal_hold_frames_left -= 1
            if self.heal_hold_frames_left <= 0:
                self.fuel -= 10
                self.hp += 15
                self.heal_hold_frames_left = 70
                sounds["heal"].play()
                Particle.spawn_particle_burst_round(self.pos, vec2(4, 2),"#11ff39", amount=20, size=7)
                
        else:
            self.heal_hold_frames_left = 70
            
        self.vel += self.dir.elementwise() * self.acc

    def draw_on(self, draw_surface):
        super().draw_on(draw_surface)
        
        if 0 < self.hp < 12 and not self.has_died:
            draw_surface.blit(self.low_hp_alert, self.pos + vec2(-16, -16))
            
        elif 0 < self.fuel < 15 and not self.has_died:
            draw_surface.blit(self.low_fuel_alert, self.pos + vec2(-16, -16))
            
        hp_text = font.render(str(round(self.hp, 1)), False, "#d4782d")
        draw_surface.blit(hp_text, self.pos + vec2(-20, 10))
        
        fuel_text = font.render(str(round(self.fuel, 1)), False, "#82db29")
        draw_surface.blit(fuel_text, self.pos + vec2(-20, -35))
        
        heal_progress = (70 - self.heal_hold_frames_left) / 70
        
        pygame.draw.circle(draw_surface, "#00ff00", self.pos, 15 * heal_progress)
        

    def update_pos(self, game_speed):
        self.vel /= self.drag
        
        self.pos += self.vel * game_speed
        
        
    def update(self, win_width: int, win_height: int, game_speed):
        if self.fuel > 0 and self.hp > 0:
            self.update_speed()
            self.dying_timer = 3.0
            
        if self.fuel > 150:
            self.fuel = 150
            
        self.update_pos(game_speed)
        self.edge_collision(win_width, win_height)
        
        if self.active and self.fuel > 0 and self.hp > 0:
            self.fuel -= 0.02 * game_speed
            
        elif self.fuel > 0 and self.hp > 0:
            self.fuel -= 0.005 * game_speed
        
        if self.hp <= 0 and not self.has_died:
            self.has_died = True
            sounds["player_die"].play()
            Particle.spawn_particle_burst_round(self.pos, vec2(7, 7), "#c8c8c8", 120, 7, 1.01, 12)
            
        if self.fuel <= 0:
            self.dying_timer -= 1/60 * game_speed
            
        if self.fuel <= 0 or self.hp <= 0:
            self.heal_hold_frames_left = 70
            
        if self.dying_timer <= 0 and not self.has_died:
            self.has_died = True
            sounds["player_die"].play()
            Particle.spawn_particle_burst_round(self.pos, vec2(7, 7), "#c8c8c8", 120, 7, 1.01, 12)
            
        if self.active and self.fuel > 0 and self.hp > 0:
            Particle(self.pos, vec2(0, 0), (255, 100, 0), 4, 70)
            
        if self.inv_frames > 0:
            self.inv_frames -= 1
            
        if self.heal_hold_frames_left > 0:
            self.heal_hold_frames_left -= 1