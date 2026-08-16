import pygame, math
from pygame.math import Vector2 as vec2
import assets.atlas as atlas
import random
from assets.enemy import Enemy
from assets.player import Player
from assets.projectile import Projectile
from assets.global_vars import sounds, font, debug_mode, enemy_multiplier, sound_groups
from assets.particle import Particle

class Smart_enemy(Enemy):   # tries to intercept the player
    damage_states = 3
    sprite_list: list[pygame.Surface] = atlas.main_atlas.get_sprite_strip([10, 30, 10, 10], 4, 2)
    spawn_hint: pygame.Surface = atlas.main_atlas.get_sprite([0, 30, 10, 10], 2)
    
    starting_wave = 5
    
    def __init__(self, pos: vec2, hp_multiplier:int = 1):
        super().__init__(pos, hp_multiplier)
        self.base_hp = 40
        self.start_hp = self.base_hp * hp_multiplier
        self.hp = self.start_hp
        self.acc = vec2(0.4, 0.4)
        self.drag = 1.025
        self.dropped_fuel = 7
        
        
    def get_spawn_amount( wave):
        return round((wave - __class__.starting_wave + 2) ** 0.6 + math.sin(wave) * enemy_multiplier)
        
        
    def update_speed(self, player: Player):
        # math is hard
        intercept_time_est: float = (player.pos - self.pos).length() / ((self.vel + self.acc.elementwise() * self.dir).length() + 0.001) 
        player_pos_next: vec2 = player.pos + player.vel * intercept_time_est + player.acc.elementwise() * player.dir * intercept_time_est**2 
        
        self.dir = (player_pos_next - self.pos).normalize()
            
        self.player_pos_next = player_pos_next
            
        self.vel += self.dir.elementwise() * self.acc
        
        
    def draw_on(self, draw_surface):
        super().draw_on(draw_surface)
        if debug_mode: #position it thinks the player will be once reached, assuming no player speed changes
            pygame.draw.circle(draw_surface, (0, 255, 100), self.player_pos_next, 5, 3)
        
      
        
class Tough_enemy(Enemy):
    damage_states = 4
    sprite_list: list[pygame.Surface] = atlas.main_atlas.get_sprite_strip([10, 40, 10, 10], 5, 2)
    spawn_hint: pygame.Surface = atlas.main_atlas.get_sprite([0, 40, 10, 10], 2)
    
    starting_wave = 3
    
    def __init__(self, pos: vec2, hp_multiplier:int = 1):
        super().__init__(pos, hp_multiplier)
        self.base_hp = 120
        self.start_hp = self.base_hp * hp_multiplier
        self.hp = self.start_hp
        self.acc = vec2(0.35, 0.35)
        
        self.drag = 1.06
        
        self.mass = 2.8
        
        self.dropped_fuel = 14
           
    
    def get_spawn_amount(wave):
        return round(math.sqrt(wave - __class__.starting_wave + 1)*enemy_multiplier)



class Shooter_enemy(Enemy):
    damage_states = 3
    sprite_list: list[pygame.Surface] = atlas.main_atlas.get_sprite_strip([10, 50, 10, 10], 4, 2)
    spawn_hint: pygame.Surface = atlas.main_atlas.get_sprite([0, 50, 10, 10], 2)
    
    starting_wave = 8
    
    def __init__(self, pos: vec2, hp_multiplier:int = 1):
        super().__init__(pos, hp_multiplier)
        self.acc = vec2(0.3, 0.3)
        self.base_hp = 60
        self.start_hp = self.base_hp * hp_multiplier
        self.hp = self.start_hp
        
        self.drag = 1.03
        
        self.dropped_fuel = 5
        
        self.proj_max_vel = 10
        
    
    def get_spawn_amount(wave):
        return 2*round( ( (wave - __class__.starting_wave + 1) ** (math.cos(5* wave)) )**0.5 * enemy_multiplier)
        
        
    def update(self, target, win_width, win_height, game_speed):
        super().update(target, win_width, win_height, game_speed)
        
        if random.randint(0, int(80/game_speed)) == 0 and self.alive:
            a = Projectile(self.pos, (target.pos - self.pos).normalize() * self.proj_max_vel, 6, False)
            self.vel -= a.vel / 8
            sounds["enemy_shoot"].play()
            
            
    def update_speed(self, player):
        if self.pos.distance_to(player.pos) < 300:
            self.dir = (self.pos - player.pos).normalize()
            
        else:
            self.dir = (player.pos - self.pos).normalize()
            
        self.vel += self.dir.elementwise() * self.acc
        
 
    
class Smart_shooter_enemy(Enemy):
    damage_states = 3
    sprite_list: list[pygame.Surface] = atlas.main_atlas.get_sprite_strip([10, 60, 10, 10], 4, 2)
    spawn_hint: pygame.Surface = atlas.main_atlas.get_sprite([0, 60, 10, 10], 2)
    
    starting_wave = 12
    
    def __init__(self, pos: vec2, hp_multiplier:int = 1):
        super().__init__(pos, hp_multiplier)
        self.acc = vec2(0.4, 0.4)
        
        self.base_hp = 40
        self.start_hp = self.base_hp * hp_multiplier
        self.hp = self.start_hp
        
        self.drag = 1.05
        
        self.dropped_fuel = 6
        
        self.proj_max_vel = 16
        
        
    def get_spawn_amount(wave):
        return 2*round((wave - __class__.starting_wave) * 0.2 * enemy_multiplier + 0.8)
        
        
    def update(self, target, win_width, win_height, game_speed):
        super().update(target, win_width, win_height, game_speed)
        
        time = self.pos.distance_to(target.pos) / self.proj_max_vel
            
        next_pos = target.pos + target.vel * time + target.dir.elementwise() * target.acc * time**2 / 2
            
        self.next_pos = next_pos
            
        if random.randint(0, int(150/game_speed)) == 0 and self.alive:
            a = Projectile(self.pos, (next_pos - self.pos).normalize() * self.proj_max_vel, 7, False)
            self.vel -= a.vel / 6
            sounds["enemy_shoot"].play()
            
            
    def update_speed(self, player):
        if self.pos.distance_to(player.pos) < 450:
            self.dir = (self.pos - player.pos).normalize()
            
        else:
            self.dir = (player.pos - self.pos).normalize()
            
        self.vel += self.dir.elementwise() * self.acc
        
        
    def draw_on(self, draw_surface):
        super().draw_on(draw_surface)
        if debug_mode:
            pygame.draw.rect(draw_surface, (255, 0, 100), (self.next_pos - vec2(6, 6), (12, 12)), 3)

    
        
class Boss(Enemy):
    damage_states = 5
    sprite_list: list[pygame.Surface] = atlas.main_atlas.get_sprite_strip([20, 100, 20, 20], 6, 2)
    spawn_hint: pygame.Surface = atlas.main_atlas.get_sprite([0, 100, 20, 20], 2)
    
    def __init__(self, pos, hp_multiplier = 1):
        super().__init__(pos, hp_multiplier)
        
        self.hit_radius = 20
        self.acc = vec2(0.025, 0.025)
        self.drag = 1.01
        self.after_death_timer = 1000
        self.dropped_fuel = 100
        
        self.base_hp = 1500
        self.start_hp = self.base_hp * hp_multiplier
        self.hp = self.start_hp
        
        self.move = 0
        self.score_given = 3600
        self.mass = 100
        
        self.burst_interbullet_timer = 0
        self.inter_burst_timer = 0
        self.burst_counter = 0
        self.bullet_counter = 0
        
        self.enemies_spawned = 0
        self.enemy_timer = 0
        
        self.inter_move_timer = 100
        
    
    def update_speed(self, player):
        if self.pos.distance_to(player.pos) < 450:
            self.dir = (self.pos - player.pos).normalize()
            
        else:
            self.dir = (player.pos - self.pos).normalize()
            
        self.vel += self.dir.elementwise() * self.acc
        
        
    def update(self, target, win_width, win_height, game_speed):
        if self.hp <= 0 and self.alive:
            self.alive = False
            random.choice(sound_groups["enemy_die"]).play()
            Particle.spawn_particle_burst_round(self.pos, vec2(6, 6), "#dd4411", damp=1.02, size=8, amount=30, max_age=200)
            Particle.spawn_particle_burst_round(self.pos, vec2(6, 6), "#c81e00", damp=1.01, size=8, amount=30, max_age=200)
            Enemy.alive_enemy_list.remove(self)
            
        if self.alive:
            self.update_speed(target)
        self.update_pos(game_speed)
        self.edge_collision(win_width, win_height)
        
        #print(self.hp)
        
        
        if not self.alive:
            self.after_death_timer -= 1
            if self.after_death_timer <= 0:
                Enemy.enemy_list.remove(self)
                del self
                return 0
                
                
        if self.move == 0 and self.alive and self.inter_move_timer <= 0:
            if self.inter_burst_timer > 0:
                self.inter_burst_timer -= 1
            else:
                
                if self.burst_interbullet_timer > 0:
                    self.burst_interbullet_timer -= 1
                else:
                    
                    if self.bullet_counter < 5:
                        time = self.pos.distance_to(target.pos) / 12
            
                        next_pos = target.pos + target.vel
                        Projectile(self.pos, (next_pos - self.pos).normalize()*12, 10, False, 2)
                        Projectile(self.pos, (next_pos - self.pos).normalize().rotate(30)*12, 10, False, 2)
                        Projectile(self.pos, (next_pos - self.pos).normalize().rotate(-30)*12, 10, False, 2)
                        
                        self.bullet_counter += 1 
                        sounds["enemy_shoot"].play()
                        self.burst_interbullet_timer = 5 / game_speed
                        
                    else: 
                        self.burst_counter += 1
                        self.bullet_counter = 0
                        self.inter_burst_timer = 20 / game_speed
                        
                        if self.burst_counter > 5:
                            self.move = 1
                            self.burst_counter = 0
                            self.bullet_counter = 0
                            self.inter_burst_timer = 0
                            self.burst_interbullet_timer = 0
                            self.inter_move_timer = 100 / game_speed
                            
                            
        if self.move == 1 and self.alive and self.inter_move_timer <= 0:
            if self.enemies_spawned < 4 and self.enemy_timer <= 0:
                a = Enemy(self.pos.copy(), 0.5)
                a.vel = vec2(random.randint(-2, 2), random.randint(-2, 2))
                a.dropped_fuel /= 2
                
                b = Tough_enemy(self.pos.copy(), 0.5)
                b.vel = vec2(random.randint(-2, 2), random.randint(-2, 2))
                b.dropped_fuel /= 2
                self.enemies_spawned += 1
                self.enemy_timer = 170
                
            if self.enemies_spawned >= 4:
                self.inter_move_timer = 240
                self.move = 0
                self.enemies_spawned = 0
                self.enemy_timer = 0
                    
        self.enemy_timer -= 1
        self.inter_move_timer -= 1
        
        