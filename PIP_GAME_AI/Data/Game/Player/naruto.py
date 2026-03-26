import pygame
import config
import os

from pygame import mixer
from Data.Game.character import Animation
from Data.Game.Player.player import Player
from Data.Game.skill import Shuriken, Kunai, Rasengan, Katon, Chibaku

path = "Data/Image/Naruto/"
path_music = "Data/Image/Naruto/Music/"

class Naruto(Player):
    def __init__(self, screen, level, health, power, chakra, map, pos, direct, key_map, volume):
        self.screen = screen
        skills = [Shuriken(screen, volume), Kunai(screen, volume), Rasengan(screen, volume), Katon(screen, volume), Chibaku(screen, volume)]
        self.x = pos[0]
        self.y = pos[1]
        animation = self.rescreen(volume)
        super().__init__(screen, "Naruto", level, health, power, chakra, map, pos, animation, skills, direct, key_map)
   
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

            

