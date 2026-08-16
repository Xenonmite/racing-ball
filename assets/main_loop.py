import pygame, math, random, os, traceback
from pygame.math import Vector2 as vec2
import assets.atlas as atlas
from assets.enemy import Enemy
from assets.more_enemies import Smart_enemy, Tough_enemy, Shooter_enemy, Smart_shooter_enemy, Boss
from assets.player import Player
from assets.particle import Particle
from assets.projectile import Projectile
from assets.eventboard_text import Eventboard_text
from assets.pickup import Pickup
from assets.global_vars import sounds, font, big_font, debug_mode, clamp
from assets.weapon import gun, minigun, shotgun, electrogun
from colorama import Fore
from assets.music_player import Music_player

pygame.mixer.init()

def init_game(win_width: int, win_height: int):
    global player, font, bg_tile_list, fg_corners, background, sprites, game_vars, score, score_table, highscore, prerendered_texts, weapon_list, enemy_list, fuel_drop_list, music_player, max_score
    
    game_vars = {
        "drawn_bg": 1,
        "wave": 0,
        "wave_done": False,
        "wave_cooldown": 0,
        "projectile_cooldown": 0,
        "hint_pos_list": [],
        "used_weapon": 0,
        "default_game_speed": 1.0,
        "game_speed": 1.0,
        "paused": False,
        "player_death_once": False
    }

    sprites = {
        "spr_crosshair": atlas.main_atlas.get_sprite([70, 30, 23, 23], 1),
        "fuel_sprites": atlas.main_atlas.get_sprite_strip((70, 20, 5, 5), 4, 2),
        "weapon_select": atlas.main_atlas.get_sprite([110, 0, 30, 30], 2)
    }
    
    weapon_list = [gun, shotgun, minigun, electrogun]
    enemy_list = [Enemy, Tough_enemy, Smart_enemy, Shooter_enemy, Smart_shooter_enemy]
    fuel_drop_list = (1, 3, 7)
        
    fg_corners = atlas.Atlas("assets/spr/fg_corners.png").get_sprite_strip([0, 0, 16, 16], 4)

    prerendered_texts = {
        "eventboard": font.render("=[ Eventboard ]=", False, (200, 200, 200)),
        "respawn": big_font.render("DEAD, press r to respawn", True, (200, 200, 200)),
        "paused": big_font.render("PRESS [ ESC ] TO UNPAUSE", True, (200, 200, 200)),
        "wave_clear": big_font.render("WAVE CLEARED", True, (200, 200, 255))
    }
    
    bg_tile_list = [pygame.image.load("assets/spr/bg_0.png").convert(), 
                    pygame.image.load("assets/spr/bg_1.png").convert()]
    
    background = create_background(win_width, win_height)
    
    player = Player(vec2(500, 300))
    
    score = 0
    highscore = read_score()
    
    score_table = {
        "enemy_hit": 10,
        "enemy_killed": 240,
        "player_hit": -150,
        "player_hit_bullet": -50,
    }
       
    music_folder = "music/"
    music_player = Music_player(music_folder)
    
    music_player.play_random()


    
def do_main_loop(draw_surface: pygame.Surface, win_width: int, win_height: int, resize_flag: bool, music_end_flag: bool):
    global background, game_vars, sprites, score, score_table, highscore, prerendered_texts, weapon_list, music_player
    
    if resize_flag:
        background = create_background(win_width, win_height)
        
    if music_end_flag:
        music_player.play_random()
        
        
    draw_surface.blit(background)
    mouse_pos = vec2(pygame.mouse.get_pos())
    
    if not game_vars["paused"]:
        handle_waves(win_width, win_height)
    
    if not game_vars["paused"]:
        handle_weapons(mouse_pos)


    keys = pygame.key.get_just_pressed()

    if keys[pygame.K_t]:
        game_vars["drawn_bg"] = int(not(bool(game_vars["drawn_bg"])))
        background = create_background(win_width, win_height)
        
    if keys[pygame.K_r] and (player.fuel <= 0 or player.has_died):
        respawn()
        
    if keys[pygame.K_ESCAPE] and player.hp > 0:
        game_vars["paused"] = not game_vars["paused"]
        
    if keys[pygame.K_k]:
        music_player.play_random()
        
    if keys[pygame.K_m]:
        if music_player.is_paused:
            music_player.resume()
        else:
            music_player.pause()
            
    if keys[pygame.K_COMMA]:
        music_player.volume = min(music_player.volume + 0.1, 1.0)
        music_player.update_volume()
        
    if keys[pygame.K_PERIOD]:
        music_player.volume = max(music_player.volume - 0.1, 0.0)
        music_player.update_volume()
        

    hold_keys = pygame.key.get_pressed()
    
    if hold_keys[pygame.K_h] and debug_mode:
        player.hp += 5
        
    if hold_keys[pygame.K_f] and debug_mode:
        player.fuel += 5
        
    if not game_vars["paused"]:
        player.update(win_width, win_height, game_vars["game_speed"])
    

    if not game_vars["paused"]:
        for enemy in Enemy.enemy_list:
            enemy.update(player, win_width, win_height, game_vars["game_speed"])

            if enemy.pos.distance_to(player.pos) < (player.hit_radius + enemy.hit_radius) and player.inv_frames <= 0 and enemy.hp > 0 and not player.has_died:
                player.hp -= 5.5
                sounds["player_hit"].play()
                player.inv_frames += 12 / game_vars["game_speed"]

                t = player.vel.copy()
                player.vel += enemy.vel/1.5
                enemy.vel += -t * 1.5 / enemy.mass

                score += score_table["player_hit"]
                Particle.spawn_particle_burst_round(player.pos.elementwise() + player.hit_radius, vec2(8, 5), "#c8c8c8", 40, 5, 1.04, 12)
                Eventboard_text(f"DAMAGED {score_table["player_hit"]}", 160, "#6E1F48")


    if not game_vars["paused"]:
        for projectile in Projectile.projectile_list:
            projectile.update(draw_surface, game_vars["game_speed"])

            # right >|
            if projectile.pos.x > win_width: 
                projectile.kill()
                continue
            
            # left |<
            if projectile.pos.x < 0: 
                projectile.kill()
                continue
            
            # down _v_
            if projectile.pos.y > win_height: 
                projectile.kill() 
                continue
            
            # up ‾^‾
            if projectile.pos.y < 0: 
                projectile.kill()
                continue
            
            if projectile.is_played_launched:

                for enemy in Enemy.alive_enemy_list:
                
                    if projectile.pos.distance_to(enemy.pos) < (projectile.size + enemy.hit_radius) and enemy.hp > 0.0 :
                        enemy.hp -= projectile.damage
                        sounds["enemy_hit"].play()
                        score += score_table['enemy_hit']

                        if enemy.hp <= 0.0 and enemy.alive:
                            score += int(enemy.score_given*enemy.hp_multiplier)
                            Eventboard_text(f"KILL {int(enemy.score_given*enemy.hp_multiplier)}", color="#e56c6c")

                            generate_dropped_fuel(enemy.pos, enemy.dropped_fuel)

                        enemy.vel += projectile.vel/enemy.mass
                        Particle.spawn_particle_burst_directed(projectile.pos, vec2(projectile.vel.length(), 0), -projectile.angle, 20, "#c81e00", 70, 4, 1.02, 3)
                        projectile.kill()
                        break
                    
            if not projectile.is_played_launched and not player.has_died:

                if projectile.pos.distance_to(player.pos) <= (player.hit_radius + projectile.size) and player.hp > 0:
                    player.hp -= projectile.damage
                    player.inv_frames += 10 / game_vars["game_speed"]
                    player.vel += projectile.vel / (10 * player.mass)

                    projectile.kill()
                    sounds["player_hit"].play()

                    score -= score_table["player_hit_bullet"]
                    Particle.spawn_particle_burst_round(player.pos.elementwise() + player.hit_radius, vec2(8, 5), "#c8c8c8", 40, 5, 1.04, 12)
                    Particle.spawn_particle_burst_round(player.pos, vec2(7, 7), "#c8c8c8", 120, 5, 1.01, 6)
                    Eventboard_text(f"UNDODGED {score_table["player_hit_bullet"]}")
                
    if not game_vars["paused"]:
        for pickup in Pickup.pickup_list:

            is_collected = pickup.update(player, game_vars["game_speed"])
            if is_collected and player.hp > 0:
                if pickup.thing == "fuel":
                    player.fuel = max(player.fuel + pickup.amount, 0)

                pickup.kill()
                continue
            
            pickup.draw_on(draw_surface)
                
            
    for hint in game_vars["hint_pos_list"]:
        draw_surface.blit(hint["type"].spawn_hint, hint["pos"].elementwise() - (10 if hint["type"] is not Boss else 20))
            
    player.draw_on(draw_surface)
    
    for enemy in Enemy.enemy_list:
        enemy.draw_on(draw_surface)
        
    if not game_vars["paused"]:
        Particle.update_all_particles(draw_surface, game_vars["game_speed"])
    
    if player.has_died and not game_vars["player_death_once"]:
        game_vars["player_death_once"] = True
        if score > highscore:
            highscore = score
            Eventboard_text("New highscore!", color="#ffff00")
            write_score(highscore)
    
    wave_text = font.render(f"Wave {game_vars["wave"]}", False, "#b6e988")
    player_stat_text = font.render(f"Fuel {round(player.fuel, 1)} | HP {round(player.hp, 1)}", False, "#e4e258" if player.hp > 0 and player.fuel > 0 else "#ee5555")
    
    if highscore <= 0:
        score_text = font.render(f"Score {score}", False, "#56e7c3" if player.hp > 0 else "#ee5555")
    else:
        score_text = font.render(f"Score {score} [{highscore} max]", False, "#56e7c3" if player.hp > 0 else "#ee5555")
    
    side_text = [
        font.render(f"|| pos [{round(player.pos.x)} | {round(player.pos.y)}]", False, "#777777"),
        font.render(f"|| vel [{round(player.vel.x)} | {round(player.vel.y)}]", False, "#777777"),
        font.render(f"|| ene [{len(Enemy.alive_enemy_list)} / {len(Enemy.enemy_list)}]", False, "#777777"),
        font.render(f"|| prj [{len(Projectile.projectile_list)}]", False, "#777777"),
        font.render(f"|| par [{len(Particle.particle_list)}]", False, "#777777"),
        font.render(f"|| pck [{len(Pickup.pickup_list)}]", False, "#777777"),
    ]
    
    draw_surface.blit(wave_text, ((win_width - wave_text.width)/2, 30))
    draw_surface.blit(player_stat_text, ((win_width - player_stat_text.width)/2, 60))
    draw_surface.blit(score_text, ((win_width - score_text.width)/2, 90))
    
    for num, line in enumerate(side_text):
        draw_surface.blit(line, (20, 20 + 20*num))
        
        
    draw_surface.blit(prerendered_texts["eventboard"], (win_width - 220, 70))
    Eventboard_text.update_all(game_vars["game_speed"])
    for num, line in enumerate(Eventboard_text.eventboard_text_list):
        x = line.duration - line.age
        draw_surface.blit(line.sprite, (win_width - 200 + (x-110)**4/500000, 90 + 25*num))
        
    if player.has_died:
        draw_surface.blit(prerendered_texts["respawn"], ((win_width - prerendered_texts["respawn"].width)/2, (win_height - prerendered_texts["respawn"].height)/2))
        if game_vars["game_speed"] > 0.005: game_vars["game_speed"] /= 1.03
        
    if game_vars["paused"]:
        draw_surface.blit(prerendered_texts["paused"], ((win_width - prerendered_texts["paused"].width)/2, (win_height - prerendered_texts["paused"].height)/2 + 50))
        
    if game_vars["wave_done"] and game_vars["wave"] > 0:
            draw_surface.blit(prerendered_texts["wave_clear"], ((win_width - prerendered_texts["wave_clear"].width)/2 + (300 - game_vars["wave_cooldown"] - 110)**4/200_000, (win_height - prerendered_texts["wave_clear"].height)/2 - 50))
         
    if player.fuel <= 0:
        dying_timer_text = font.render(f"DEATH IN {round(player.dying_timer, 1)}s", False, (255, 100, 100))
        draw_surface.blit(dying_timer_text, ((win_width - dying_timer_text.width)/2, (win_height - dying_timer_text.height)/2))
        
    
    # ===========<[ OUTLINE ]>============ #
    
    draw_surface.blit(fg_corners[0], (0, 0))
    draw_surface.blit(fg_corners[1], (0, win_height - fg_corners[0].height))
    draw_surface.blit(fg_corners[2], (win_width - fg_corners[2].width, win_height - fg_corners[2].height))
    draw_surface.blit(fg_corners[3], (win_width - fg_corners[3].width, 0))
    
    pygame.draw.rect(draw_surface, "#edf5f9", (0, 0, win_width, 6))
    pygame.draw.rect(draw_surface, "#edf5f9", (0, win_height - 6, win_width, 6))
    pygame.draw.rect(draw_surface, "#edf5f9", (0, 0, 6, win_height))
    pygame.draw.rect(draw_surface, "#edf5f9", (win_width - 6, 0, 6, win_height))
    
    # ==================================== #
        
    for num, gun in enumerate(weapon_list):
        draw_surface.blit(gun.sprite, (40 + 60*num, win_height - 100))
        
    draw_surface.blit(sprites["weapon_select"], (40 + 60*game_vars["used_weapon"], win_height - 100))
        
    draw_surface.blit(sprites["spr_crosshair"], [v - 11.5 for v in mouse_pos])
    
    pygame.display.flip()
        
        
def create_background(win_width: int, win_height: int):
    global bg_tile_list, game_vars
    
    bg = pygame.Surface((win_width, win_height))
    tile = bg_tile_list[game_vars["drawn_bg"]]
    
    for row in range( math.ceil(win_height / tile.height) ):
        for col in range( math.ceil(win_width / tile.width) ):
            bg.blit(tile, (col * tile.width, row * tile.height))
            
    return bg


def handle_waves(win_width: int, win_height: int):
    if len(Enemy.alive_enemy_list) == 0 and not game_vars["wave_done"]:
        
        game_vars["wave_done"] = True
        game_vars["wave_cooldown"] = 300
        
        for p in Pickup.pickup_list:
            p.pickup_range *= 1.5
        
        if (game_vars["wave"] + 1) % 10 != 0: # non-boss waves
            for enemy_type in enemy_list:
                if game_vars["wave"] >= enemy_type.starting_wave:
                    for _ in range(enemy_type.get_spawn_amount(game_vars["wave"])):
                        game_vars["hint_pos_list"].append(
                            {
                                "pos": vec2(random.randint(0, win_width), random.randint(0, win_height)),
                                "type": enemy_type
                            }
                        )
                
        # boss waves
        else:
            for _ in range(round(game_vars["wave"] / 10)):
                game_vars["hint_pos_list"].append(
                    {
                        "pos": vec2(random.randint(0, win_width), random.randint(0, win_height)),
                        "type": Boss
                    }
                )
        
    if game_vars["wave_cooldown"] > 0:
        game_vars["wave_cooldown"] -= 1
        
    if game_vars["wave_cooldown"] <= 0 and game_vars["wave_done"]:
        game_vars["wave_done"] = False
        game_vars["wave"] += 1
        

        for hint in game_vars["hint_pos_list"]:
            hint["type"](hint["pos"], game_vars["wave"] ** 0.2 - 0.5)
            Particle.spawn_particle_burst_round(hint["pos"], vec2(6, 6), "#696969", 30, 7)
                
        game_vars["hint_pos_list"] = []
     
        
def respawn():
    global score
    game_vars["projectile_cooldown"] = 0
    game_vars["wave"] = 0
    game_vars["wave_done"] = False
    game_vars["wave_cooldown"] = 0
    game_vars["hint_pos_list"] = []
    game_vars["player_death_once"] = False
    Enemy.enemy_list = []
    Enemy.alive_enemy_list = []
    Projectile.projectile_list = []
    Particle.particle_list = []
    Pickup.pickup_list = []
    player.hp = 50.0
    player.fuel = 40.0
    player.alive = True
    player.has_died = False
    score = 0
    
    game_vars["game_speed"] = game_vars["default_game_speed"]
    
    #print(starting_enemy_pool_chances)
    
    
def handle_weapons(mouse_pos):
    global game_vars, weapon_list, player
    
    keys = pygame.key.get_just_pressed()
    if keys[pygame.K_1]:
        game_vars["used_weapon"] = 0
    if keys[pygame.K_2]:
        game_vars["used_weapon"] = 1
    if keys[pygame.K_3]:
        game_vars["used_weapon"] = 2
    if keys[pygame.K_4]:
        game_vars["used_weapon"] = 3
            
    if game_vars["projectile_cooldown"] > 0:
        game_vars["projectile_cooldown"] -= 1
    
    if pygame.mouse.get_pressed()[0] and game_vars["projectile_cooldown"] <= 0 and player.fuel > 0 and player.hp > 0:
        angle = (mouse_pos - player.pos).angle
        wep = weapon_list[game_vars["used_weapon"]]
        wep.fire(player.pos, angle)
        game_vars["projectile_cooldown"] = wep.cooldown / game_vars["game_speed"]
        player.fuel -= wep.fuel_cost
        player.vel -= vec2(1, 0).rotate(angle) * wep.knockback
        sounds["fire"].play()
        

def generate_dropped_fuel(pos, amount):
    global fuel_drop_list
    
    while amount > 0:
        drop_i = random.randint(0, len(fuel_drop_list)-1)
        dropped_amount = fuel_drop_list[drop_i]
        Pickup(pos, vec2(random.randint(-20, 20)/10, random.randint(-20, 20)/10), sprites["fuel_sprites"][drop_i], random.randint(80, 240), amount=dropped_amount)
        amount -= dropped_amount


def write_score(score: int):
    save_image = pygame.Surface((64, 64))
    save_image.fill("#000000")
    
    subtracted_score = 0
    
    for row in range(64):
        for col in range(64):
            subtracted_score = 0
            if score > 255:
                subtracted_score = 255
            elif score > 0:
                subtracted_score = score
                
            save_image.set_at((col, row), (subtracted_score, 0, 0))
            score -= subtracted_score
                
    pygame.image.save(save_image, "assets/save.png")
    
    
def read_score():
    try:
        img = pygame.image.load("assets/save.png")
        
    except FileNotFoundError:
        return 0
    
    else:
        score_sum = 0
        for row in range(64):
            for col in range(64):
                score_sum += img.get_at((col, row))[0]
                
        return score_sum