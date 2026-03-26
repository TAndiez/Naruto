import os
import pygame
import config

from abc import abstractmethod
from pygame import mixer
from abc import ABC
from Data.Game.map import Map


try:
    if not mixer.get_init():
        mixer.init()
except pygame.error:
    pass


class Animation:
    def __init__(self, screen, frames_dict: dict[str, list[pygame.Surface]], sound: dict[str, mixer.Sound], volume: int):
        self.screen = screen
        self.frames_dict = frames_dict
        self.flipped_frames_dict = {
            state: [pygame.transform.flip(frame, True, False) for frame in frames]
            for state, frames in frames_dict.items()
        }
        self.sound = sound
        self.volume = volume
        self.state = list(frames_dict.keys())[0]
        self.last_state = self.state
        self.frames = frames_dict[self.state]
        self.current_frames = {state: 0 for state in self.frames_dict.keys()}
        self.last_update = 0
        self.state_delay = {
            "attack": 100,
            "run": 50,
            "move": 60,
            "stand": 50,
            "defend": 20,
            "hurt": 0,
            "katon": 20,
            "chibaku": 20
        }

    def stop(self):
        if self.sound.get(self.state):
            self.sound[self.state].stop()

    def set_state(self, state, current_time):
        if state in self.frames_dict:
            if self.state != state:
                if self.sound.get(self.state):
                    self.sound[self.state].stop()
                self.last_state = self.state
                self.state = state
                self.frames = self.frames_dict[state]
                self.last_update = current_time
                if self.sound.get(self.state):
                    self.sound[self.state].set_volume(self.volume)
                    self.sound[self.state].play(-1)

    def update(self, current_time):
        delay = self.state_delay.get(self.state)
        if current_time - self.last_update > delay:
            self.last_update = current_time
            self.current_frames[self.state] = (self.current_frames[self.state] + 1) % len(self.frames)

    def draw(self, pos, id, direct: tuple[int, int] | int | bool):
        x, y = pos
        self.screen.blit(self.frames_dict.get("player")[id], (x, y - 2 * round(config.HEIGHT * 1 / 30)))
        frame_idx = self.current_frames[self.state]
        if direct:
            self.screen.blit(self.frames[frame_idx], pos)
        else:
            self.screen.blit(self.flipped_frames_dict[self.state][frame_idx], pos)


class Value:
    def __init__(self, value, limit):
        self._value = value
        self.limit = limit

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = max(0, min(val, self.limit))


class Character(ABC):
    def __init__(self,
                 screen: pygame.Surface,
                 name: str,
                 level=1,
                 health=100,
                 power=200,
                 chakra=100,
                 map: Map = None,
                 pos: tuple = (0, 0),
                 animation: Animation = None,
                 direct: bool = True,
                 ):
        self.screen = screen
        self.name = name
        self.level = level
        self.hp = Value(health, health)
        self.pw = Value(power, power)
        self.chakra = Value(0, chakra)
        self.max_hp = health
        self.max_pw = power
        self.rate_hp = max(1, round(health / 100))
        self.rate_pw = max(1, round(power / 100))
        self.map = map

        self.x = pos[0]
        self.y = pos[1]

        self.animation = animation
        self.direct = direct

        self.size_x = round(config.WIDTH / 40) * 2
        self.size_y = round(config.HEIGHT / 30) * 4
        self.gravity = 1
        self.velocity_y = 0
        self.max_fall_speed = 20
        self.delay = 0
        self.last_time_delay = 0
        self.state = None
        self.get_atk_dir = None
        self.step_atk_x = 0
    
    def destroy(self):
        self.animation.stop()

    def level_up(self):
        self.level += 1
        self.hp.value += 20
        self.pw.value += 20

    def take_damage(self, amount: int, get_atk_dir: bool, step_atk_x: int, delay: int = 0):
        if hasattr(self, "god_mode") and self.god_mode:
            self.god_mode = False
        if self.animation.state == "defend" and get_atk_dir == self.direct:
            self.hp.value -= amount // 5
            self.step_atk_x = step_atk_x // 2
        else:
            self.hp.value -= amount
            self.step_atk_x = step_atk_x 
            self.animation.set_state("hurt", self.last_time_delay)
        self.get_atk_dir = get_atk_dir
        self.delay = delay
        self.last_time_delay = pygame.time.get_ticks()

    def is_alive(self):
        return self.hp.value > 0
    
    def update_power(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_power_up_time >= 1000 and self.pw.value < self.max_pw:
            self.pw.value += 5
            self.last_power_up_time = current_time

    @abstractmethod
    def update():
        pass
