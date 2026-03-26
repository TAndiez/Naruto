import os
import pygame
import config

from Data.Game.character import Character
from abc import ABC, abstractmethod
from pygame import mixer


PATH_SKILL = "Data/Image/Skill/"
PATH_MUSIC = "Data/Image/Skill/Music/"
try:
    if not mixer.get_init():
        mixer.init()
except pygame.error:
    pass

class Animation:
    def __init__(self, screen, frames, delay):
        self.screen = screen
        self.frames = frames
        self.delay = delay
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.flipped_frames = [pygame.transform.flip(frame, True, False) for frame in frames]

    def update_frame(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def draw(self, pos, direct: tuple[int, int] | bool, angle: float = 0):
        '''draw at top_left with optional rotation'''
        frame = self.frames[self.current_frame] if direct else self.flipped_frames[self.current_frame]
        
        if angle != 0:
            rotated_frame = pygame.transform.rotate(frame, angle)
            rect = rotated_frame.get_rect(center=frame.get_rect(center=pos).center)
            self.screen.blit(rotated_frame, rect)
        else:
            self.screen.blit(frame, pos)

class Skill(ABC):
    def __init__(self, name: str, animation: Animation, sound: mixer.Sound,
                size: tuple[int, int], range: int, damage: int, delay: int,
                mana: int, cooldown: int, chakra: int, effect: int, volume: int):
        self.name = name
        self.animation = animation
        self.sound = sound
        self.size = size
        self.damage = damage
        self.range = range
        self.delay = delay
        self.mana = mana
        self.cooldown = cooldown * 1000
        self.chakra = chakra
        self.effect = effect
        self.volume = volume
        self.pos = None
        self.last_update = pygame.time.get_ticks()
        self.last_used = pygame.time.get_ticks()
        self.first_use = True
        self.active = False
        self.finished = False
        self.hit = False

    def can_shoot(self, player):
        current_time = pygame.time.get_ticks()
        if self.name == "chibaku":
            if player.chakra.value == 100:
                if current_time - self.last_used >= self.cooldown or self.first_use:
                    return True
                else:
                    return False
            else:
                return False
        if not self.active and current_time - self.last_used >= self.cooldown and player.pw.value >= self.mana:
            return True
        elif self.first_use and player.pw.value >= self.mana:
            return True
        else:
            return False
    def get_size(self):
        return self.size
    
    def take_damage(self):
        return self.damage
    
    def stop_sound(self):
        self.sound.stop()

    def play_sound(self):
        self.sound.set_volume(self.volume)
        self.sound.play(0)

    @abstractmethod
    def shoot(self):
        pass
    
    def can_attack(self, pos: tuple[int, int], enemy: Character, direct: bool):
        left1 = pos[0]
        right1 = pos[0] + self.size[0]
        top1 = pos[1]
        bottom1 = pos[1] + self.size[1]

        left2 = enemy.x
        right2 = enemy.x + enemy.size_x
        top2 = enemy.y
        bottom2 = enemy.y + enemy.size_y

        attack_right = right1
        attack_left = left1

        attack_top = top1
        attack_bottom = bottom1
        
        overlap_x = not (attack_right <= left2 or attack_left >= right2)
        overlap_y = not (attack_bottom <= top2 or attack_top >= bottom2)
        return overlap_x and overlap_y
    
class Shuriken(Skill):
    def __init__(self, screen, volume):
        sound = mixer.Sound(os.path.join(PATH_MUSIC, "shuriken.mp3"))
        skill_animation = [
            pygame.transform.scale(
                pygame.image.load(PATH_SKILL + f"shuriken{i}.png").convert_alpha(),
                ((config.WIDTH // 40), (config.HEIGHT // 30)*4)
            )
            for i in range(1, 5)
        ]
        animation = Animation(screen=screen, frames=skill_animation, delay = 100)
        super().__init__(name="shuriken", animation=animation, sound=sound, size=((config.WIDTH // 40), (config.HEIGHT // 30)*4),
                         range = 30, damage = 20, delay = 10, mana = 10, cooldown = 2, chakra = 3, effect = 200, volume = volume)
        self.current_index = 0

    def shoot(self, player: Character, pos, direct):
        if self.can_shoot(player):
            self.finished = False
            self.first_use = False
            self.play_sound()
            self.last_used = pygame.time.get_ticks()
            self.last_update = pygame.time.get_ticks()
            self.active = True
            self.pos = pos
            self.direct = direct
            self.current_index = 0 
            self.first_shoot = True
            player.set_power(player.get_power() - self.mana)
            player.set_chakra(player.get_chakra() + self.chakra)

    def update(self, player: Character, enemy: Character):
        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= self.delay:
                if self.direct:
                    if self.first_shoot:
                        new_pos = (self.pos[0] + player.size_x, self.pos[1])
                        self.first_shoot = False
                    else:
                        new_pos = (self.pos[0] + round(config.WIDTH*15 / 800), self.pos[1])
                else:
                    if self.first_shoot:
                        new_pos = (self.pos[0] - self.size[0], self.pos[1])
                        self.first_shoot = False
                    else:
                        new_pos = (self.pos[0] - round(config.WIDTH*15 / 800), self.pos[1])
                self.pos = new_pos
                self.animation.update_frame()
                self.animation.draw(self.pos, self.direct)
                self.current_index += 1
                self.last_update = current_time
            if self.can_attack(self.pos, enemy, self.direct):
                enemy.take_damage(self.take_damage(), self.pos[0] - enemy.x >= 0, 10, self.effect)
                self.active = False
                self.finished = True
                self.hit = True
                self.stop_sound()
            if self.current_index > self.range:
                self.active = False
                self.finished = True
                self.stop_sound()
class Kunai(Skill):
    def __init__(self, screen, volume):  
        sound = mixer.Sound(os.path.join(PATH_MUSIC, "kunai.mp3"))
        skill_animation = [
            pygame.transform.rotate(
                pygame.transform.scale(
                    pygame.image.load(PATH_SKILL + f"kunai{i}.png").convert_alpha(),
                    ((config.WIDTH // 40) * 3, (config.HEIGHT // 30))
                ),
                90
            )
            for i in range(1, 5)
        ]
        animation = Animation(screen=screen, frames=skill_animation, delay = 10)
        super().__init__(name="kunai", animation=animation, sound=sound, size=((config.WIDTH // 40), (config.HEIGHT // 30)*3),
                        range = 20, damage = 30, delay = 10, mana = 20, cooldown = 3, chakra = 5, effect = 300, volume = volume)
        self.current_index = 0
        
    def shoot(self, player: Character, pos, direct):
        if self.can_shoot(player):
            self.finished = False
            self.first_use = False
            self.play_sound()
            self.last_used = pygame.time.get_ticks()
            self.last_update = pygame.time.get_ticks()
            self.active = True 
            self.pos = pos  
            self.direct = direct
            self.current_index = 0 
            self.first_shoot = True
            player.set_power(player.get_power() - self.mana)
            player.set_chakra(player.get_chakra() + self.chakra)

    def update(self, player: Character, enemy: Character):
        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= self.delay:
                if self.direct:
                    if self.first_shoot:
                        new_pos = (self.pos[0] + player.size_x, self.pos[1] - player.size_y / 2)
                        self.first_shoot = False
                    else:
                        new_pos = (self.pos[0], self.pos[1] - round(config.HEIGHT*20 / 600))
                else:
                    if self.first_shoot:
                        new_pos = (self.pos[0] - player.size_x / 2, self.pos[1] - player.size_y / 2)
                        self.first_shoot = False
                    else:
                        new_pos = (self.pos[0], self.pos[1] - round(config.HEIGHT*20 / 600))
                self.pos = new_pos
                self.animation.update_frame()
                self.animation.draw(new_pos, True)
                self.current_index += 1
                self.last_update = current_time
            if self.can_attack(self.pos, enemy, self.direct):
                enemy.take_damage(self.take_damage(), self.pos[0] - enemy.x >= 0, 10, self.effect)
                self.active = False
                self.finished = True
                self.hit = True
                self.stop_sound()
            if self.current_index > self.range:
                self.active = False
                self.finished = True
                self.stop_sound()


class Rasengan(Skill):
    def __init__(self, screen, volume):
        sound = mixer.Sound(os.path.join(PATH_MUSIC, "rasengan.mp3"))
        skill_animation = [
            pygame.transform.scale(
                pygame.image.load(PATH_SKILL + f"rasengan{i}.png").convert_alpha(),
                ((config.WIDTH // 40)*4, (config.HEIGHT // 30)*4)
            )
            for i in range(1, 10)
        ]
        animation = Animation(screen=screen, frames=skill_animation, delay = 50)
        super().__init__(name="rasengan", animation=animation, sound=sound, size=((config.WIDTH // 40)*2, (config.HEIGHT // 30)*2),
                         range = 30, damage = 80, delay = 50, mana = 50, cooldown = 5, chakra = 10, effect = 300, volume = volume)
        self.current_index = 0

    def shoot(self, player: Character, pos, direct):
        if self.can_shoot(player):
            self.finished = False
            self.first_use = False
            self.play_sound()
            self.last_used = pygame.time.get_ticks()
            self.last_update = pygame.time.get_ticks()
            self.active = True
            self.pos = pos  
            self.direct = direct
            self.first_shoot = True
            self.current_index = 0 
            player.set_power(player.get_power() - self.mana)
            player.set_chakra(player.get_chakra() + self.chakra)

    def update(self, player: Character, enemy: Character):
        if self.active and self.current_index < self.range:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= self.delay:
                if self.direct:
                    if self.first_shoot:
                        new_pos = (self.pos[0] + player.size_x, self.pos[1])
                        self.first_shoot = False
                    else:
                        new_pos = (self.pos[0] + round(config.WIDTH*25 / 800) + (self.current_index)**2 // 4, self.pos[1])
                else:
                    if self.first_shoot:
                        new_pos = (self.pos[0] - self.size[0], self.pos[1])
                        self.first_shoot = False
                    else:
                        new_pos = (self.pos[0] - round(config.WIDTH*25 / 800) - (self.current_index)**2 // 4, self.pos[1])
                self.pos = new_pos
                self.animation.update_frame()
                self.animation.draw(new_pos, self.direct)
                self.current_index += 1
                self.last_update = current_time
            if self.can_attack(self.pos, enemy, self.direct):
                enemy.take_damage(self.take_damage(), self.pos[0] - enemy.x >= 0, 10, self.effect)
                self.active = False
                self.finished = True
                self.hit = True
                self.stop_sound()
            if self.current_index >= self.range:
                self.active = False
                self.finished = True
                self.stop_sound()

class Katon(Skill):
    def __init__(self, screen, volume): 
        self.first_use = False
        sound = mixer.Sound(os.path.join(PATH_MUSIC, "katon.mp3"))
        skill_animation = [
            pygame.transform.scale(
                pygame.image.load(PATH_SKILL + f"katon{i}.png").convert_alpha(),
                ((config.WIDTH // 40)*8, (config.HEIGHT // 30)*8)
            )
            for i in range(1, 4)
        ]
        animation = Animation(screen=screen, frames=skill_animation, delay = 10)
        super().__init__(name="katon", animation=animation, sound=sound, size=((config.WIDTH // 40)*8, (config.HEIGHT // 30)*6),
                         range = 150, damage = 1, delay = 15, mana = 100, cooldown = 30, chakra = 20, effect = 50, volume = volume)
        self.current_index = 0

    def shoot(self, player: Character, pos: tuple[int, int], direct: bool):
        if self.can_shoot(player):
            self.play_sound()
            self.last_used = pygame.time.get_ticks()
            self.last_update = pygame.time.get_ticks()
            self.active = True 
            self.pos = pos  
            self.direct = direct
            self.current_index = 0 
            player.set_power(player.get_power() - self.mana)
            player.set_chakra(player.get_chakra() + self.chakra)

    def update(self, enemy: Character, pos: tuple[int, int]):
        self.pos = pos
        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= self.delay:
                if self.direct:
                    new_pos = (self.pos[0] - 10, self.pos[1] - 60)
                else:
                    new_pos = (self.pos[0] - 190, self.pos[1] - 60)
                if self.can_attack(new_pos, enemy, self.direct):
                    enemy.animation.set_state("stand", current_time)
                    enemy.take_damage(self.take_damage(), pos[0] - enemy.x >= 0, 1, self.effect)
                    self.hit = True
                self.animation.update_frame()
                self.animation.draw(new_pos, self.direct)
                self.current_index += 1
                self.last_update = current_time
            if self.current_index >= self.range:
                self.active = False
                self.stop_sound()

class Chibaku(Skill):
    def __init__(self, screen, volume):
        sound = mixer.Sound(os.path.join(PATH_MUSIC, "chibaku.mp3"))
        skill_animation = [
            pygame.transform.scale(
                pygame.image.load(PATH_SKILL + f"chibaku_x.png").convert_alpha(),
                ((config.WIDTH // 40)*8, (config.HEIGHT // 30)*8))
        ]
        animation = Animation(screen=screen, frames=skill_animation, delay = 100)
        super().__init__(name="chibaku", animation=animation, sound=sound, size=((config.WIDTH // 40)*40, (config.HEIGHT // 30)*30),
                         range = None, damage = 2, delay = 100, mana = 200, cooldown = 60, chakra = 0, effect = 0, volume=volume)
        self.rotation_speed = 5
        self.rotation_duration = 8000 
        self.direct = True

    def shoot(self, player):
        if self.can_shoot(player):
            self.first_use = False
            self.play_sound()
            self.start_time = pygame.time.get_ticks()
            self.active = True
            self.start_pos = (round(config.WIDTH / 2), round(config.HEIGHT / 4))
            self.direct = player.direct
            self.angle = 0
            self.end = False
            self.current_index = 1
            player.set_chakra(0)

    def update(self, enemy: Character):
        if self.active:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time
            if elapsed_time < self.rotation_duration:
                self.angle = (elapsed_time / self.rotation_duration) * 720 + self.rotation_speed*self.current_index
                self.current_index += 1
            else:
                self.end = True
            self.animation.update_frame()
            self.animation.draw(self.start_pos, self.direct, self.angle)
            (enemy.x, enemy.y) = (round(config.WIDTH / 2 - enemy.size_x / 2), round(config.HEIGHT / 4 - enemy.size_y / 2))
            enemy.animation.set_state("stand", current_time)
            enemy.take_damage(self.take_damage(), True, 0, self.effect)
            self.last_update = current_time
            if self.end:
                self.active = False
