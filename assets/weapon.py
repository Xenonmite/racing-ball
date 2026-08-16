import pygame, assets.projectile as projectile, assets.particle as particle, random
from pygame.math import Vector2 as vec2
from assets.atlas import main_atlas
import assets.enemy 
from assets.global_vars import lerp


class Gun:
    def __init__(self):
        self.name = "Gun"
        self.proj_per_shot = 1
        self.spread_angle = 0
        self.fuel_cost = 0.1
        self.cooldown = 12
        self.bullet_vel = 20
        self.bullet_damage = 15
        self.knockback = 1
        self.sprite = main_atlas.get_sprite([140, 0, 30, 30], 2)
        
    def fire(self, pos: vec2, angle: float):
        for _ in range(self.proj_per_shot):
            rand_angle = (random.random()*2 - 1) * self.spread_angle
            projectile.Projectile(pos, vec2(1, 0).rotate(angle + rand_angle) * self.bullet_vel, 10, True, self.bullet_damage)
            
        particle.Particle.spawn_particle_burst_directed(pos, vec2(5, 5), angle, 35, "#ddaa77", 15, 6, 1.07, 4)
            

class Minigun(Gun):
    def __init__(self):
        self.name = "Minigun"
        self.proj_per_shot = 1
        self.spread_angle = 4
        self.fuel_cost = 0.4
        self.cooldown = 2
        self.bullet_vel = 20
        self.bullet_damage = 13
        self.knockback = 1.414
        self.sprite = main_atlas.get_sprite([170, 0, 30, 30], 2)
            

class Shotgun(Gun):
    def __init__(self):
        self.name = "Shotgun"
        self.proj_per_shot = 10
        self.spread_angle = 15
        self.fuel_cost = 2.5
        self.cooldown = 40
        self.bullet_vel = 20
        self.bullet_damage = 12.5
        self.knockback = 11
        self.sprite = main_atlas.get_sprite([140, 30, 30, 30], 2)
        

class Electrogun(Gun):
    def __init__(self):
        self.name = "Electrogun"
        self.proj_per_shot = 1
        self.spread_angle = 30
        self.fuel_cost = 2
        self.cooldown = 15
        self.bullet_vel = 20
        self.bullet_damage = 20
        self.knockback = 0
        self.sprite = main_atlas.get_sprite([170, 30, 30, 30], 2)
        self.damaged_list = []
        self.max_chain_length = 6
        self.damage_decay = 0.9
        self.max_chain_distance = 400
        
    def fire(self, pos: vec2, angle: float):
        self.damaged_list = []
        current_damage = self.bullet_damage
        current_max_distance = self.max_chain_distance
        last_shocked_pos = pos
        
            
        for foe in assets.enemy.Enemy.alive_enemy_list:
            if (foe.pos.distance_to(last_shocked_pos) <= current_max_distance) and (foe not in self.damaged_list):
                foe.hp -= current_damage
                if foe.hp <= 0:
                    particle.Particle.spawn_particle_burst_round(foe.pos, vec2(2, 2), "#dd4411", damp=1.05, size=9)
                    particle.Particle.spawn_particle_burst_round(foe.pos, vec2(2, 2), "#bedd11", damp=1.05, size=9)
                
                current_damage *= self.damage_decay
                current_max_distance *= self.damage_decay**2
                self.damaged_list.append(foe)
                particle.Particle.spawn_particle_line(last_shocked_pos, foe.pos, vec2(0.25, 0.25), "#5cafd8", 30, 5, amount=int(foe.pos.distance_to(last_shocked_pos)*0.1))
                last_shocked_pos = foe.pos
                #print("enemy success")

            elif foe in self.damaged_list:
                #print("enemy already hit")
                continue
            
            if len(self.damaged_list) >= len(assets.enemy.Enemy.alive_enemy_list) or len(self.damaged_list) > self.max_chain_length:
                #print("loop broken")
                break
            
        else:
            if last_shocked_pos == pos:
                particle.Particle.spawn_particle_burst_round(pos, vec2(8, 8), "#5cafd8", damp=1.01, size=4)
                #print("loop exited with no enemies damanged")
            
                
                    
                
    
        
        
gun = Gun()
minigun = Minigun()
shotgun = Shotgun()
electrogun = Electrogun()