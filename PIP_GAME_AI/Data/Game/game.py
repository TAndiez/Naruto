import pygame
import config   

from Data.Game.map import Map
from Data.Game.character import Character
from Data.Game.Player.player import Player
from API.Interface.option import OptionManager
from abc import ABC, abstractmethod
from Data.Game.Player.naruto import Naruto
from Data.Game.Bot.NarutoAI import NarutoAIBot
from Data.Game.Bot.NarutoRB import NarutoRuleBasedBot


class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, target_rect):
        return target_rect.move(-self.camera_rect.topleft)

    def update(self, target):
        x = -target.rect.centerx + config.WIDTH // 2
        y = -target.rect.centery + config.HEIGHT // 2

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - config.WIDTH), x)
        y = max(-(self.height - config.HEIGHT), y)

        self.camera_rect = pygame.Rect(x, y, self.width, self.height)

class Game(ABC):
    def __init__(self, screen: pygame.Surface,
                       option_manager: OptionManager,
                       map: Map,
                       ):
        self.screen = screen
        self.opt = option_manager
        self.map = map
    @abstractmethod
    def rescreen(self):
        pass
    @abstractmethod
    def run(self, signal):
        pass


class Solo(Game):
    def __init__(self, screen: pygame.Surface,
                       option_manager: OptionManager,
                       map: Map,
                       player1: Character,
                       player2: Character):
        super().__init__(screen, option_manager, map)
        self.player1 = player1
        self.player2 = player2

    def rescreen(self):
        self.player1.rescreen()
        self.player2.rescreen()

    def run(self, signal):
        current_time = pygame.time.get_ticks()
        if not self.player1.is_alive() or not self.player2.is_alive():
            self.player1.destroy()
            self.player2.destroy()
            return True
        if signal:
            self.rescreen()
        self.map.draw_map_solo()
        self.player1.update(self.player2, current_time, 0)
        self.player2.update(self.player1, current_time, 1)
        if current_time % 500 <= 250:
            self.player1.draw(0)
            self.player2.draw(1)
        else:
            self.player2.draw(1)
            self.player1.draw(0)
        pygame.display.flip()
        return False
    
def get_default_key_map(player_index):
    if player_index == 0:
        return {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'up': pygame.K_w,
            'down': pygame.K_s,
            'attack1': pygame.K_j,
            'skill1': pygame.K_y,
            'skill2': pygame.K_u,
            'skill3': pygame.K_i,
            'skill4': pygame.K_o,
            'skill5': pygame.K_p
        }
    elif player_index == 1:
        return {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'attack1': pygame.K_KP1,
            'skill1': pygame.K_KP4,
            'skill2': pygame.K_KP5,
            'skill3': pygame.K_KP6,
            'skill4': pygame.K_KP7,
            'skill5': pygame.K_KP8
        }

class Adventure(Game):
    def __init__(self, screen: pygame.Surface,
                       option_manager: OptionManager,
                       map: Map,
                       player: Player,
                       camera: Camera):
        super().__init__(screen, option_manager, map)
        self.player = player
        self.camera = camera

    def run(self):
        # TODO: logic phiêu lưu sau
        pass


def load_game(screen,
              option_manager: OptionManager,
              GameMode: str = "Solo",
              PATH="Data/Image/",
              PATH_MAP="Data/Map/",
              name_map="map2.txt"):
    
    if GameMode == "Solo":
        key_maps = [get_default_key_map(i) for i in range(2)]
        game_map = Map(screen, PATH, PATH_MAP, name_map, "Data/Map/Map_Solo/map_solo_2.png")
        player1 = Naruto(screen, 100, 500, 200, 100, game_map, (0, int(config.HEIGHT*(15 / 600))), True, key_maps[0], 1)
        player2 = NarutoRuleBasedBot(screen, 100, 500, 200, 100, game_map, (int(config.WIDTH*(700 / 800)), int(config.HEIGHT*(415 / 800))), False, 1)
        game = Solo(screen, option_manager, game_map, player1, player2)

    elif GameMode == "Adventure":
        pass

    return game
