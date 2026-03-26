import numpy as np
import pygame
import config
import os

from pygame import mixer
from Data.Game.character import Animation
from Data.Game.Bot.bot import Bot
from Data.Game.skill import Shuriken, Kunai, Rasengan, Katon, Chibaku

path = "Data/Image/Naruto/"
path_music = "Data/Image/Naruto/Music/"
class NarutoAIBot(Bot):
    def __init__(self, screen, level, health, power, chakra, map, pos, direct, volume, agent=None):
        self.current_actions = []
        self.action_lock = False
        self.screen = screen
        skills = [Shuriken(screen, volume), Kunai(screen, volume), Rasengan(screen, volume), Katon(screen, volume), Chibaku(screen, volume)]
        self.x = pos[0]
        self.y = pos[1]
        animation = self.rescreen(volume)
        super().__init__(screen, "Naruto", level, health, power, chakra, map, pos, animation, skills, direct)
        self.agent = agent  

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

    def get_local_map(self, enemy, radius_x=7, radius_y=5):
        tile_x = self.x // self.map.BLOCK_SIZE_X
        tile_y = self.y // self.map.BLOCK_SIZE_Y

        ex1 = enemy.x // self.map.BLOCK_SIZE_X
        ey1 = enemy.y // self.map.BLOCK_SIZE_Y
        ex2 = (enemy.x + 2 * self.map.BLOCK_SIZE_X) // self.map.BLOCK_SIZE_X
        ey2 = (enemy.y + 4 * self.map.BLOCK_SIZE_Y) // self.map.BLOCK_SIZE_Y

        local_patch = []

        for dy in range(-radius_y, radius_y + 1):
            for dx in range(-radius_x, radius_x + 1):

                nx = tile_x + dx
                ny = tile_y + dy
                if not (0 <= ny < len(self.map.map_data) and 0 <= nx < len(self.map.map_data[0])):
                    local_patch.append(1)
                    continue
                val = self.map.map_data[ny][nx]
                if ex1 <= nx <= ex2 and ey1 <= ny <= ey2:
                    val = 2  # mask enemy tile

                local_patch.append(val)
        return np.array(local_patch, dtype=np.float32)


    def get_state(self, enemy, phase=1):
        hp_ratio = self.hp.value / self.max_hp
        pw_ratio = self.pw.value / self.max_pw
        chakra_ratio = self.chakra.value / 100

        enemy_hp_ratio = enemy.hp.value / enemy.max_hp
        enemy_pw_ratio = enemy.pw.value / enemy.max_pw

        rel_x = (self.x - enemy.x) / config.WIDTH
        rel_y = (self.y - enemy.y) / config.HEIGHT

        can_attack_flag = int(self.can_attack(enemy))

        direction_self = int(self.direct)
        direction_enemy = int(enemy.direct)

        skill_availability = np.array(
            [int(skill.can_shoot(self)) for skill in self.skills],
            dtype=np.float32
        )

        local_map = self.get_local_map(enemy).flatten().astype(np.float32)

        # ----------------------------------------
        # FULL STATE 
        # ----------------------------------------
        full_state = np.concatenate((
            np.array([
                hp_ratio,          # 0
                pw_ratio,          # 1
                chakra_ratio,      # 2
                enemy_hp_ratio,    # 3
                enemy_pw_ratio,    # 4
                rel_x,             # 5
                rel_y,             # 6
                direction_self,    # 7
                direction_enemy,   # 8
                can_attack_flag    # 9
            ], dtype=np.float32),
            skill_availability,   # index 10 - 14
            local_map             # index 15 - 179
        ))

        # ----------------------------------------
        # MASK PER PHASE
        # ----------------------------------------
        mask = np.zeros_like(full_state)

        if phase == 1:
            important = [
                1,   # pw_ratio
                3,   # enemy_hp_ratio
                5,   # rel_x
                7,   # direction_self
                8,   # direction_enemy
                9,   # can_attack_flag
                13,  # SKILL_4
            ]

        elif phase == 2:
            important = [
                0,   # hp_ratio
                1,   # pw_ratio
                3,   # enemy_hp_ratio
                4,   # enemy_pw_ratio
                5,   # rel_x
                7,   # direction_self
                8,   # direction_enemy
                9,   # can_attack_flag
                10,  # SKILL_1
                11,  # SKILL_2
                12,  # SKILL_3
                13,  # SKILL_4
            ]
        else:
            important = list(range(len(full_state)))  # full

        mask[important] = 1
        masked_state = full_state.copy()
        masked_state[mask == 0] = -2.0
        return masked_state

    def train_update(self, action, enemy, current_time):
        dx, dy = 0, 0
        if current_time - self.last_time_delay > self.delay:
            dx, dy = self.do_action(action, enemy, current_time)
        else:
            if self.skill_lock:
                self.skill_lock = None
            self.update_attack(enemy)
            dx -= self.step_atk_x if self.get_atk_dir else -self.step_atk_x
            
        dy += self.handle_gravity()
        self.handle_collision(dx, dy)
        self.update_power()
        self.draw_attribute(0)
        self.animation.update(current_time)
        self.animation.draw(
            (round(self.x * (config.WIDTH / 800)), round(self.y * (config.HEIGHT / 600))),
            0, self.direct
        )

    def update(self, action, enemy, current_time):
        dx, dy = 0, 0
        if current_time - self.last_time_delay > self.delay:
            dx, dy = self.do_action(action, enemy, current_time)
        else:
            if self.skill_lock:
                self.skill_lock = None
            self.update_attack(enemy)
            dx -= self.step_atk_x if self.get_atk_dir else -self.step_atk_x
            
        dy += self.handle_gravity()
        self.handle_collision(dx, dy)
        self.update_power()
        self.draw_attribute(0)
        self.animation.update(current_time)
        self.animation.draw(
            (round(self.x * (config.WIDTH / 800)), round(self.y * (config.HEIGHT / 600))),
            0, self.direct
        )