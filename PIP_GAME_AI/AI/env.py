import numpy as np
import pygame
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import config
from Data.Game.Bot.action import A
from Data.Game.map import Map
from Data.Game.Bot.NarutoAI import NarutoAIBot
from Data.Game.Bot.NarutoRB import NarutoRuleBasedBot

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Thư mục gốc Naruto/
PATH = os.path.join(BASE_DIR, "Data", "Image")
PATH_MAP = os.path.join(BASE_DIR, "Data", "Map")
name_map_1="map1.txt"
name_map_2="map2.txt"

SKILL_ENUMS = [
    A.SKILL_1,
    A.SKILL_2,
    A.SKILL_3,
    A.SKILL_4,
    A.SKILL_5,
]

class Environment:
    def __init__(self, render_mode=True, volume=1):
        self.render_mode = render_mode
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        self.game_map_1 = Map(self.screen, PATH, PATH_MAP, name_map_1, "Data/Map/Map_Solo/map_solo_1.png")
        self.game_map_2 = Map(self.screen, PATH, PATH_MAP, name_map_2, "Data/Map/Map_Solo/map_solo_2.png")
        self.clock = pygame.time.Clock()
        self.volume = volume
        self.reset()

    def reset(self, phase = 1):
        pos = (0, 0)
        enemy_pw = 0
        self.game_map = self.game_map_1 if phase in [1, 2] else self.game_map_2
        if phase == 1:
            pos = (100, int(config.HEIGHT*(415 / 600)))
            enemy_pw = 20000
        elif phase == 2:
            pos = (200, int(config.HEIGHT*(415 / 600)))
            enemy_pw = 200
        else:
            pos = (int(config.WIDTH*(760 / 800)), int(config.HEIGHT*(415 / 800)))
            enemy_pw = 200
        self.player = NarutoAIBot(
            screen=self.screen,
            level=1,
            health=500,
            power=200,
            chakra=100,
            map=self.game_map, 
            pos=(0, int(config.HEIGHT*(415 / 600))),
            direct=True,
            volume=self.volume
        )
        self.enemy = NarutoRuleBasedBot(
            screen=self.screen,
            level=1,
            health=500,
            power=enemy_pw,
            chakra=100,
            map=self.game_map,
            pos=pos,
            direct=False,
            volume=self.volume
        )
        self.done = False
        self.prev_player_hp = self.player.hp.value
        self.prev_enemy_hp = self.enemy.hp.value
        self.prev_enemy_pw = self.enemy.pw.value
        self.prev_player_pw = self.player.pw.value
        self.prev_player_x = self.player.x
        self.prev_player_y = self.player.y
        # PHASE 4 #
        self.god_mode = True
        self.cont_atk = pygame.time.get_ticks()
        self.god_mode_atk = pygame.time.get_ticks()
        self.prev_enemy_hp_p4 = self.enemy.hp.value
        self.count_atk = 1
        self.ATK_RG = 30
        return self.get_state(phase=phase)
    
    def get_state(self, phase:int = 1):
        return self.player.get_state(self.enemy, phase)
    
    def game_over(self):
        return not self.player.is_alive() or not self.enemy.is_alive()

    def valid_actions(self, actions: list[A]):
        valid_action = []
        current_actions = [None] * 5
        self.enemy_attacks = [None] * 5

        for i, skill in enumerate(self.player.skills):
            if skill.finished:
                current_actions[i] = SKILL_ENUMS[i]
            else:
                current_actions[i] = None    

        for i, skill in enumerate(self.enemy.skills):
            if skill.finished:
                self.enemy_attacks[i] = SKILL_ENUMS[i]
            else:
                self.enemy_attacks[i] = None       
   
        total_action = [a for a in current_actions if a is not None]
        if self.player.skills[3].active:
            valid_action = [SKILL_ENUMS[3]]

        elif self.player.skills[4].active:
            valid_action = [SKILL_ENUMS[4]]

        else:
            for a in actions:
                # RUN, HIGH_JUMP, DEFEND need pw >= 1
                if a.name.startswith("RUN") or a == A.HIGH_JUMP or a == A.DEFEND:
                    if self.player.pw.value >= 1:
                        valid_action.append(a)

                elif a == A.SKILL_1:
                    if self.player.skills[0].can_shoot(self.player):
                        valid_action.append(a)

                elif a == A.SKILL_2:
                    if self.player.skills[1].can_shoot(self.player):
                        valid_action.append(a)

                elif a == A.SKILL_3:
                    if self.player.skills[2].can_shoot(self.player):
                        valid_action.append(a)

                elif a == A.SKILL_4:
                    if self.player.skills[3].can_shoot(self.player):
                        valid_action.append(a)

                elif a == A.SKILL_5:
                    if self.player.skills[4].can_shoot(self.player):
                        valid_action.append(a)
                else:
                    valid_action.append(a)
        
        if not valid_action:
            valid_action = [A.STAND]
        
        total_action.extend(valid_action)

        return valid_action, total_action
    def reset_skill_states(self, char):
        for skill in char.skills:
            skill.hit = False
            skill.finished = False  

    def reset_all_skill_states(self):
        self.reset_skill_states(self.player)
        self.reset_skill_states(self.enemy)

    def end_step(self, phase: int = 1):
        reward = 0
        self.done = True
        if phase == 1:
            reward += (self.player.hp.value - self.enemy.hp.value) * 0.01
        elif phase == 2:
            reward += (self.player.hp.value - self.enemy.hp.value) * 0.05
        elif phase == 3:
            if self.enemy.hp.value == 0:
                reward += 100
            elif self.player.hp.value == 0:
                reward -= 50
            else:
                reward += (self.player.hp.value - self.enemy.hp.value) * 0.05
        return self.get_state(phase=phase), reward, self.done, 0
    
    def step(self, actions, phase: int = 1):
        self.reset_all_skill_states()
        valid, action = self.valid_actions(actions)
        current_time = pygame.time.get_ticks()
        self.game_map.draw_map_solo()
        self.player.train_update(valid, self.enemy, current_time)
        self.enemy.train_update(self.player, current_time, phase=phase)
        self.render(current_time)
        reward = 0
        
        cur_player_hp = self.player.hp.value
        cur_enemy_hp = self.enemy.hp.value
        cur_player_pw = self.player.pw.value
        cur_player_x = self.player.x
        cur_player_y = self.player.y
        cur_enemy_x = self.enemy.x
        cur_enemy_y = self.enemy.y
        damage_to_self = self.prev_player_hp - cur_player_hp
        damage_to_enemy = self.prev_enemy_hp - cur_enemy_hp 
        dist_x = abs(cur_player_x - cur_enemy_x)
        dist_y = abs(cur_player_y - cur_enemy_y)
        # =============================== #
        # PHASE 1: EASY LEARNING         #
        # =============================== #
        if phase == 1:
            # ===============================
            # 1. Use ATTACK and SKILL 4 correctly
            # ===============================
            
            if A.SKILL_4 in action:
                if damage_to_enemy >= 1:
                    reward += round(damage_to_enemy * 0.02 * ((80 - dist_x) / 40), 2)
                else:
                    reward -= 0.01

            if A.ATTACK in action and damage_to_enemy >= 1:
                reward += 0.5
            
            # ===============================
            # 2. Penalty for using wrong skills
            # ===============================
            group = [A.SKILL_1, A.SKILL_2, A.SKILL_3]
            count = len([a for a in action if a in group])
            if count > 0 and damage_to_enemy == 0:
                reward -= count * 0.02 * abs(cur_player_pw - self.prev_player_pw)

            # ===============================
            # 3. Encourage to close the enemy
            # ===============================

            prev_dist = abs(self.prev_player_x - cur_enemy_x)

            # Go away: penalty
            if dist_x > prev_dist:
                if action in [A.MOVE_LEFT, A.MOVE_RIGHT]:
                    reward -= round(0.001 * (dist_x - prev_dist), 2)

                if action in [A.RUN_LEFT, A.RUN_RIGHT]:
                    reward -= round(0.002 * (dist_x - prev_dist), 2)

            # Go closer: reward
            elif dist_x < prev_dist:
                if action in [A.MOVE_LEFT, A.MOVE_RIGHT]:
                    reward += round(0.002 * (prev_dist - dist_x), 2)
                if action in [A.RUN_LEFT, A.RUN_RIGHT]:
                    reward += round(0.004 * (prev_dist - dist_x), 2)

            # ===============================
            # 4. Move to "Combat range" (70 -> 130)
            # ===============================
            ATK_RG = 60
            if cur_enemy_x - ATK_RG <= cur_player_x <= cur_enemy_x + ATK_RG:
                reward += 0.01
            else:
                reward -= 0.01  

        # =============================== #
        # PHASE 2: NORMAL LEARNING        #
        # =============================== #
        elif phase == 2:
            if A.SKILL_4 in action:
                if damage_to_enemy >= 1:
                    reward += round(damage_to_enemy * 0.03 * ((80 - dist_x) / 40), 2)
                else:
                    reward -= 0.04
                    
            if A.ATTACK in action and damage_to_enemy >= 1:
                reward += 0.1

            skill_actions = [A.SKILL_1, A.SKILL_2, A.SKILL_3]
            for idx, skill_action in enumerate(skill_actions):
                if skill_action in action:
                    skill = self.player.skills[idx]

                    if skill.finished:
                        if skill.hit: 
                            if damage_to_enemy > skill.damage // 5: 
                                reward += damage_to_enemy * 0.04
                            else:
                                reward += damage_to_enemy * 0.02
                        else: #miss
                            reward -= skill.damage * 0.02
            
            for idx, skill_action in enumerate(skill_actions):
                if skill_action in self.enemy_attacks:
                    skill = self.enemy.skills[idx]

                    if skill.finished and skill.hit:
                        if damage_to_self > skill.damage // 5: 
                                reward -= damage_to_self * 0.04
                        else:
                            reward += damage_to_self * 0.06
                    elif skill.finished and not skill.hit:
                        reward += skill.damage * 0.02
                        
            prev_dist = abs(self.prev_player_x - cur_enemy_x)

            # Go away: penalty
            if dist_x > prev_dist:
                if action in [A.MOVE_LEFT, A.MOVE_RIGHT]:
                    reward -= round(0.003 * (dist_x - prev_dist), 2)

                if action in [A.RUN_LEFT, A.RUN_RIGHT]:
                    reward -= round(0.006 * (dist_x - prev_dist), 2)

            # Go closer: reward
            elif dist_x < prev_dist:
                if action in [A.MOVE_LEFT, A.MOVE_RIGHT]:
                    reward += round(0.001 * (prev_dist - dist_x), 2)
                if action in [A.RUN_LEFT, A.RUN_RIGHT]:
                    reward += round(0.002 * (prev_dist - dist_x), 2)

            ATK_RG = 200
            if dist_x <= ATK_RG:
                reward += 0.01
            else:
                reward -= 0.05 * dist_x / ATK_RG  

        # =============================== #
        # PHASE 3: ADVANCED LEARNING      #
        # =============================== #
        else:
            if current_time - self.cont_atk >= 5000:
                self.cont_atk = current_time
                if self.prev_enemy_hp_p4 - cur_enemy_hp > 0:
                    reward += self.count_atk * 0.5
                    self.prev_enemy_hp_p4 = cur_enemy_hp
                    self.count_atk += 1
                else:
                    self.count_atk = 1
                    
            if (40000 >= current_time - self.god_mode_atk >= 30000 or 70000 >= current_time - self.god_mode_atk >= 60000) and self.god_mode:
                if damage_to_enemy > 0:
                    reward += 10
                    self.god_mode = False

            if A.SKILL_5 in action:
                reward += 0.05

            if A.SKILL_4 in action:
                if damage_to_enemy >= 1:
                    reward += round(damage_to_enemy * 0.03 * ((80 - dist_x) / 40), 2)
                else:
                    reward -= 0.04
                    
            if A.ATTACK in action and damage_to_enemy >= 1:
                reward += 0.1

            skill_actions = [A.SKILL_1, A.SKILL_2, A.SKILL_3]
            for idx, skill_action in enumerate(skill_actions):
                if skill_action in action:
                    skill = self.player.skills[idx]

                    if skill.finished:
                        if skill.hit: 
                            if damage_to_enemy > skill.damage // 5: 
                                reward += damage_to_enemy * 0.02
                            else:
                                reward += damage_to_enemy * 0.01
                        else: #miss
                            reward -= skill.damage * 0.04

            if self.enemy.skills[4].active:
                reward -= 0.05

            if self.enemy.skills[3].active:
                if damage_to_self >= 1:
                    reward -= round(damage_to_enemy * 0.03 * ((80 - dist_x) / 40), 2)
                else:
                    reward += 0.04

            for idx, skill_action in enumerate(skill_actions):
                if skill_action in self.enemy_attacks:
                    skill = self.enemy.skills[idx]

                    if skill.finished and skill.hit:
                        if damage_to_self > skill.damage // 5: 
                                reward -= damage_to_self * 0.08
                        else:
                            reward += damage_to_self * 0.06
                    elif skill.finished and not skill.hit:
                        reward += skill.damage * 0.04
                        
            DISTANCE = 100
            if dist_x < DISTANCE or dist_y < DISTANCE:
                reward += 0.01
            else:
                reward -= 0.01             

        self.prev_player_hp = cur_player_hp
        self.prev_enemy_hp = cur_enemy_hp
        self.prev_player_pw = cur_player_pw
        self.prev_player_x = cur_player_x
        self.prev_player_y = cur_player_y
        return self.get_state(phase=phase), reward, self.done, valid
    
    def demo(self, action, phase: int = 1):
        current_time = pygame.time.get_ticks()
        self.game_map.draw_map_solo()
        self.player.update(action, self.enemy, current_time)
        self.enemy.update(self.player, current_time, phase=phase)
        self.render(current_time)

    def render(self, current_time):
        if self.render_mode:
            self.player.draw_attribute(0)
            self.player.animation.update(current_time)
            self.player.animation.draw((self.player.x, self.player.y), 0, self.player.direct)
            self.enemy.draw_attribute(1)
            self.enemy.animation.update(current_time)
            self.enemy.animation.draw((self.enemy.x, self.enemy.y), 1, self.enemy.direct)
            pygame.display.flip()

    def close(self):
        pygame.quit()
