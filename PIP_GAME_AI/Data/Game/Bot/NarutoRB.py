import config
import pygame
import os
import random

from pygame import mixer
from Data.Game.character import Animation
from Data.Game.character import Character
from Data.Game.Bot.bot import Bot
from Data.Game.skill import Shuriken, Kunai, Rasengan, Katon, Chibaku
from Data.Game.Bot.action import A

path = "Data/Image/Naruto/"
path_music = "Data/Image/Naruto/Music/"

class NarutoRuleBasedBot(Bot):
    def __init__(self, screen, level, health, power, chakra, map, pos, direct, volume):
        self.atk_time = pygame.time.get_ticks()
        self.action_lock = False
        self.prev_hp = None
        self.god_mode = True
        self.step_add = 0
        self.screen = screen
        skills = [Shuriken(screen, volume), Kunai(screen, volume), Rasengan(screen, volume), Katon(screen, volume), Chibaku(screen, volume)]
        self.x = pos[0]
        self.y = pos[1]
        animation = self.rescreen(volume)
        super().__init__(screen, "Naruto", level, health, power, chakra, map, pos, animation, skills, direct)
        self.counter = 0
        self.move_lock = None
    def rescreen(self, volume):
        self.size_x = round(config.WIDTH / 40) * 2
        self.size_y = round(config.HEIGHT / 30) * 4

        Nar_animation = {state: [pygame.transform.scale(pygame.image.load(path + f"naruto_{state}{i}.png").convert_alpha(), ((config.WIDTH // 40)*2, (config.HEIGHT // 30)*4)) 
                            for i in range(1, count + 1)] for state, count in 
                    {"stand": 2, "defend": 1, "run": 6, "move": 7, "hurt": 1, "katon": 2, "chibaku": 2}.items()}
        Nar_animation["attack"] = [
            pygame.transform.scale(pygame.image.load(path + f"naruto_attack{i}.png").convert_alpha(), ((config.WIDTH // 40)*2, (config.HEIGHT // 30)*4))
            for i in range(1, 5)
        ]
        Nar_animation["attribute"] = [
            pygame.transform.scale(pygame.image.load(path + "attribute.png").convert_alpha(), (round(config.WIDTH / 40)*10, round(config.HEIGHT / 30)*3)),
            pygame.transform.flip(pygame.transform.scale(pygame.image.load(path + "attribute.png").convert_alpha(), (round(config.WIDTH / 40)*10, round(config.HEIGHT / 30)*3)), True, False),
            pygame.transform.scale(pygame.image.load(path + "subhp.png").convert_alpha(), (round(config.WIDTH * (1 / 800)), round(config.HEIGHT * (15 / 600)))),
            pygame.transform.scale(pygame.image.load(path + "subchakra.png").convert_alpha(), (round(config.WIDTH * (1 / 800)), (config.HEIGHT * (4 / 600)))),
        ]
        Nar_animation["player"] = [
            pygame.transform.scale(pygame.image.load(path + "player1.png").convert_alpha(), ((config.WIDTH // 40)*2, (config.HEIGHT // 30)*2)),
            pygame.transform.scale(pygame.image.load(path + "player2.png").convert_alpha(), ((config.WIDTH // 40)*2, (config.HEIGHT // 30)*2)),
        ]
        sound = {'attack': mixer.Sound(os.path.join(path_music, "attack.mp3")),
                 'hurt': mixer.Sound(os.path.join(path_music, "hurt.mp3")),
                 'run': mixer.Sound(os.path.join(path_music, "run.mp3")),
                 'move': mixer.Sound(os.path.join(path_music, "move.mp3"))}
        self.animation = Animation(self.screen, Nar_animation, sound, volume)
        return self.animation
    def update_attack(self, enemy):
        active_lock_found = False
        for skill in self.skills:
            if skill.name == "katon":
                if self.skill_lock == "katon" and skill.active:
                    active_lock_found = True
                    skill.update(enemy, (self.x + 2 * round(config.WIDTH * 1 / 40), self.y))
                else:
                    skill.active = False

            elif skill.name == "chibaku":
                if self.skill_lock == "chibaku" and skill.active:
                    active_lock_found = True
                    skill.update(enemy)
                else:
                    skill.active = False
            else:
                if skill.active:
                    active_lock_found = True
                    skill.update(self, enemy)
        if not active_lock_found:
            self.skill_lock = None

    def decide_action(self, enemy: Character, current_time, phase: int = 1):
        actions = []
        dist_x = abs(self.x - enemy.x)
        dist_y = abs(self.y - enemy.y)
        ATTACK_RANGE = self.ATTACK_RANGE
        # ====================================== #
        # PHASE 1: EASY LEARNING                 #
        # ====================================== #
        if phase == 1:
            if current_time - self.atk_time > 2000:
                self.atk_time = current_time
                if self.counter % 2 == 0:
                    self.counter +=1
                    return [A.MOVE_RIGHT]
                else:
                    self.counter += 1
                    return [A.MOVE_LEFT]
            else:
                return [A.DEFEND]
        
        # ====================================== #
        # PHASE 2: NORMAL LEARNING               #
        # ====================================== #
        elif phase == 2:
            COMBAT_RANGE = 100
            if self.counter > 0:
                self.counter -= 1
                return self.move_lock
            
            if self.skills[4].can_shoot(self) and self.chakra.value == 100:
                return [A.SKILL_5]

            if enemy.skills[0].active or enemy.skills[2].active: 
                return [A.DEFEND]
            
            if enemy.skills[3].active:
                return [A.STAND]
            
            if dist_x > COMBAT_RANGE:
                if self.x > enemy.x:
                    return [A.MOVE_LEFT]
                else:
                    return [A.MOVE_RIGHT]
            else:
                if dist_x < ATTACK_RANGE // 2 and current_time - self.atk_time >= 5000:
                    self.atk_time = current_time
                    self.counter = 10
                    if self.x > enemy.x:
                        self.move_lock = [A.RUN_RIGHT]
                    else:
                        self.move_lock = [A.RUN_LEFT]
                    return self.move_lock
                    
                elif ATTACK_RANGE // 2 <= dist_x <= ATTACK_RANGE:
                    if self.skills[3].can_shoot(self):
                        if self.x > enemy.x:
                            return [A.MOVE_LEFT, A.SKILL_4]
                        else:
                            return [A.MOVE_RIGHT, A.SKILL_4]
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.ATTACK]
                    else:
                        return [A.MOVE_RIGHT, A.ATTACK]
                        
                else:
                    if current_time - self.atk_time >= 5000 and self.pw.value >= self.max_pw // 2:
                        self.atk_time = current_time
                        if self.skills[0].can_shoot(self):
                            if self.x > enemy.x:
                                return [A.MOVE_LEFT, A.SKILL_1]
                            else:
                                return [A.MOVE_RIGHT, A.SKILL_1]
                        if self.skills[2].can_shoot(self):
                            if self.x > enemy.x:
                                return [A.MOVE_LEFT, A.SKILL_3]
                            else:
                                return [A.MOVE_RIGHT, A.SKILL_3]
                    else:
                        if self.x > enemy.x:
                            return [A.MOVE_LEFT, A.ATTACK]
                        else:
                            return [A.MOVE_RIGHT, A.ATTACK]
                        
        # ====================================== #
        # PHASE 3: ADVANCE LEARNING               #
        # ====================================== #
        else:   
            if (40000 >= current_time - self.atk_time >= 30000 or 70000 >= current_time - self.atk_time >= 60000) and self.god_mode:
                self.prev_hp = self.hp.value
                if current_time - self.atk_time <= 40000:
                    self.x, self.y = 180, 260
                else:
                    self.x, self.y = 580, 260
                if self.prev_hp == self.hp.value:
                    if current_time - self.atk_time > 30000 + self.step_add:
                        self.hp.value += 5
                        self.step_add += 1000
                else:
                    self.god_mode = False
                self.direct = False
                return [A.STAND]

            if self.action_lock:
                if self.jumping and self.in_air:
                    return self.current_actions  
                else:
                    self.action_lock = False
                    self.current_actions = []

            if self.skills[4].can_shoot(self):
                return [A.SKILL_5]

            if enemy.skills[0].active or enemy.skills[1].active:
                return [A.DEFEND]
            
            if enemy.skills[2].active:
                return [A.HIGH_JUMP]
            
            if enemy.skills[4].active:
                if self.skills[0].can_shoot(self):
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.SKILL_1]
                    else:
                        return [A.MOVE_RIGHT, A.SKILL_1]
                if self.skills[2].can_shoot(self):
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.SKILL_3]
                    else:
                        return [A.MOVE_RIGHT, A.SKILL_3]
                
            step_ahead_x = self.x + (self.size_x if self.direct else - (config.WIDTH // 40) if self.x >= (config.WIDTH // 40) else 0)
            step_ahead_y = self.y + (config.HEIGHT // 30) * 3

            if self.map.is_solid_at_pixel(step_ahead_x, step_ahead_y):
                if self.pw.value > self.max_pw // 2:
                    actions = [A.JUMP, A.RUN_RIGHT if self.direct else A.RUN_LEFT]
                else:
                    actions = [A.JUMP, A.MOVE_RIGHT if self.direct else A.MOVE_LEFT]
                self.action_lock = True
                self.current_actions = actions
                return actions

            if dist_x < self.ATTACK_RANGE and dist_y < 40:
                if self.skills[3].can_shoot(self):
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.SKILL_4]
                    else:
                        return [A.MOVE_RIGHT, A.SKILL_4]
                else:
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.ATTACK]
                    else:
                        return [A.MOVE_RIGHT, A.ATTACK]

            if dist_x < 250 and dist_y < 40:
                if self.skills[0].can_shoot(self):
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.SKILL_1]
                    else:
                        return [A.MOVE_RIGHT, A.SKILL_1]
                if self.skills[2].can_shoot(self):
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.SKILL_3]
                    else:
                        return [A.MOVE_RIGHT, A.SKILL_3]
            
            if dist_x < 50 and dist_y >= 40:
                if self.skills[1].can_shoot(self):
                    if self.x > enemy.x:
                        return [A.MOVE_LEFT, A.SKILL_2]
                    else:
                        return [A.MOVE_RIGHT, A.SKILL_2]
            SAFE_DISTANCE = 300  
            if self.hp.value >= self.max_hp // 8:
                if enemy.x + self.ATTACK_RANGE < self.x:
                    if self.pw.value > (self.max_pw // 4) * 3:
                        return [A.RUN_LEFT]
                    else:
                        return [A.MOVE_LEFT]
                elif enemy.x - self.ATTACK_RANGE > self.x:
                    if self.pw.value > (self.max_pw // 4) * 3:
                        return [A.RUN_RIGHT]
                    else:
                        return [A.MOVE_RIGHT]
            else:
                if dist_x < SAFE_DISTANCE:
                    if enemy.x < self.x:
                        if self.pw.value > (self.max_pw // 4) * 3:
                            return [A.RUN_RIGHT]
                        else:
                            return [A.MOVE_RIGHT]
                    else:
                        if self.pw.value > (self.max_pw // 4) * 3:
                            return [A.RUN_LEFT]
                        else:
                            return [A.MOVE_LEFT]
                else:
                    return [A.STAND]

            return [A.STAND]

    def train_update(self, enemy, current_time: int, phase: int):
        dx, dy = 0, 0
        if current_time - self.last_time_delay > self.delay:
            action = self.decide_action(enemy, current_time, phase=phase)
            dx, dy = self.do_action(action, enemy, current_time)
            dy += self.handle_gravity()
            self.handle_collision(dx, dy)
        else:
            if self.skill_lock:
                self.skill_lock = None
            self.update_attack(enemy)
            dx -= self.step_atk_x if self.get_atk_dir else -self.step_atk_x
            dy += self.handle_gravity()
            self.handle_collision(dx, dy)
        self.update_power()
        self.draw_attribute(1)
        self.animation.update(current_time)
        self.animation.draw(
            (round(self.x * (config.WIDTH / 800)), round(self.y * (config.HEIGHT / 600))),
            1, self.direct
        )

    def update(self, enemy, current_time: int, phase: int = 3):
        dx, dy = 0, 0
        if current_time - self.last_time_delay > self.delay:
            action = self.decide_action(enemy, current_time, phase=phase)
            dx, dy = self.do_action(action, enemy, current_time)
            dy += self.handle_gravity()
            self.handle_collision(dx, dy)
        else:
            if self.skill_lock:
                self.skill_lock = None
            self.update_attack(enemy)
            dx -= self.step_atk_x if self.get_atk_dir else -self.step_atk_x
            dy += self.handle_gravity()
            self.handle_collision(dx, dy)
        self.update_power()
        self.draw_attribute(1)
        self.animation.update(current_time)
        self.animation.draw(
            (round(self.x * (config.WIDTH / 800)), round(self.y * (config.HEIGHT / 600))),
            1, self.direct
        )
