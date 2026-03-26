import pygame
import os
from pygame import mixer
from API.Interface.option import OptionManager
from Data.Game.game import Game, load_game
import config 


class Button:
    def __init__(self, x: int, y: int, image: pygame.Surface, align: str = "center"):
        self.image = image
        if align == "center":
            self.rect = self.image.get_rect(center=(x, y))
        elif align == "topleft":
            self.rect = self.image.get_rect(topleft=(x, y))
        else:
            raise ValueError("Invalid alignment. Use 'center' or 'topleft'.")

    def is_clicked(self, pos: tuple[int, int]):
        return self.rect.collidepoint(pos)


class Interface:
    def __init__(self, screen: pygame.Surface, image_path: str, music_path: str):
        self.screen = screen
        self.PATH_IMAGES = image_path
        self.PATH_MUSIC = music_path
        self.game_mode: Game = None
        self.game_over = False
        self.current_state = "main"

        mixer.init()
        self.bg_music = mixer.Sound(os.path.join(self.PATH_MUSIC, "music.mp3"))
        self.bg_music.set_volume(1)
        self.bg_music.play(-1)
        self.click_sound = mixer.Sound(os.path.join(self.PATH_MUSIC, "click.mp3"))
        self.click_sound.set_volume(1)

        # Load ảnh gốc (chưa scale)
        self.BUTTON_IMAGES = {
            'setting': pygame.image.load(os.path.join(self.PATH_IMAGES, "setting_button.png")),
            'exit': pygame.image.load(os.path.join(self.PATH_IMAGES, "exit_button.png")),
            'help': pygame.image.load(os.path.join(self.PATH_IMAGES, "help_button.png")),
            'volume': pygame.image.load(os.path.join(self.PATH_IMAGES, "button_vol.png")),
            'yes_exit': pygame.image.load(os.path.join(self.PATH_IMAGES, "yes_button.png")),
            'no_exit': pygame.image.load(os.path.join(self.PATH_IMAGES, "no_button.png")),
            'x': pygame.image.load(os.path.join(self.PATH_IMAGES, "x.png")),
            'play': pygame.image.load(os.path.join(self.PATH_IMAGES, "play_button.png")),
        }

        # Gọi resize_ui() lần đầu
        self.resize_ui()

    def resize_ui(self):
        """Scale và set vị trí nút theo config.WIDTH, config.HEIGHT hiện tại"""
        SCALED_BUTTON_IMAGES = {
            'setting': pygame.transform.scale(self.BUTTON_IMAGES['setting'], (int(config.WIDTH * 0.11), int(config.HEIGHT * 0.15))),
            'exit': pygame.transform.scale(self.BUTTON_IMAGES['exit'], (int(config.WIDTH * 0.1), int(config.HEIGHT * 0.13))),
            'help': pygame.transform.scale(self.BUTTON_IMAGES['help'], (int(config.WIDTH * 0.1), int(config.HEIGHT * 0.13))),
            'volume': pygame.transform.scale(self.BUTTON_IMAGES['volume'], (int(config.WIDTH * 0.05), int(config.HEIGHT * 0.06))),
            'yes_exit': pygame.transform.scale(self.BUTTON_IMAGES['yes_exit'], (int(config.WIDTH * 0.1), int(config.HEIGHT * 0.08))),
            'no_exit': pygame.transform.scale(self.BUTTON_IMAGES['no_exit'], (int(config.WIDTH * 0.1), int(config.HEIGHT * 0.08))),
            'x': pygame.transform.scale(self.BUTTON_IMAGES['x'], (int(config.WIDTH * 0.04), int(config.HEIGHT * 0.05))),
            'play': pygame.transform.scale(self.BUTTON_IMAGES['play'], (int(config.WIDTH * 0.25), int(config.HEIGHT * 0.33))),
        }

        # Khởi tạo lại các button theo size mới
        self.setting_button = Button(int(config.WIDTH * 0.5), int(config.HEIGHT * 0.98), SCALED_BUTTON_IMAGES['setting'])
        self.exit_button = Button(int(config.WIDTH * 0.97), int(config.HEIGHT * 0.98), SCALED_BUTTON_IMAGES['exit'])
        self.help_button = Button(int(config.WIDTH * 0.03), int(config.HEIGHT * 0.98), SCALED_BUTTON_IMAGES['help'])
        self.vol_music_button = Button(int(config.WIDTH * 0.625), int(config.HEIGHT * 0.43), SCALED_BUTTON_IMAGES['volume'])
        self.vol_sound_button = Button(int(config.WIDTH * 0.625), int(config.HEIGHT * 0.65), SCALED_BUTTON_IMAGES['volume'])
        self.yes_button = Button(int(config.WIDTH * 0.37), int(config.HEIGHT * 0.5), SCALED_BUTTON_IMAGES['yes_exit'], align="topleft")
        self.no_button = Button(int(config.WIDTH * 0.52), int(config.HEIGHT * 0.5), SCALED_BUTTON_IMAGES['no_exit'], align="topleft")
        self.x_button = Button(int(config.WIDTH * 0.73), int(config.HEIGHT * 0.18), SCALED_BUTTON_IMAGES['x'])
        self.play_button = Button(int(config.WIDTH * 0.5), int(config.HEIGHT * 0.66), SCALED_BUTTON_IMAGES['play'])

        # Update option manager
        self.option_manager = OptionManager(
            self.screen, self.PATH_IMAGES, self.PATH_MUSIC,
            self.bg_music, self.click_sound,
            self.vol_music_button, self.vol_sound_button,
            self.setting_button, self.exit_button,
            self.yes_button, self.no_button, self.x_button
        )


    def __set_game_mode(self, game_mode: str):
        self.game_mode = load_game(self.screen, self.option_manager, GameMode=game_mode)

    def __draw_select(self):
        GAME_MODE_BG = pygame.image.load(os.path.join(self.PATH_IMAGES, "game_mode.png"))
        SCALED_GAME_MODE_BG = pygame.transform.scale(GAME_MODE_BG, (config.WIDTH, config.HEIGHT))
        self.screen.blit(SCALED_GAME_MODE_BG, (0, 0))

    def __draw_setting(self):
        self.option_manager.draw_setting()

    def __draw_exit(self):
        self.option_manager.draw_exit()

    def __draw_help(self):
        HELP_BG_IMG = pygame.image.load(os.path.join(self.PATH_IMAGES, "help_bg.png"))
        SCALED_HELP_BG_IMG = pygame.transform.scale(HELP_BG_IMG, (int(config.WIDTH * 0.5), int(config.HEIGHT * 0.66)))
        self.screen.blit(SCALED_HELP_BG_IMG, (int(config.WIDTH * 0.25), int(config.HEIGHT * 0.16)))

        HELP_HIGHLIGHT = pygame.image.load(os.path.join(self.PATH_IMAGES, "help_button_highlight.png"))
        TEMP = self.help_button.image
        self.help_button.image = pygame.transform.scale(HELP_HIGHLIGHT, (int(config.WIDTH * 0.1), int(config.HEIGHT * 0.13)))
        for button in (self.help_button, self.x_button):
            self.screen.blit(button.image, button.rect)
        self.help_button.image = TEMP

    def draw(self, signal):
        title = pygame.image.load(os.path.join(self.PATH_IMAGES, "title.png"))
        title = pygame.transform.scale(title, (config.WIDTH, int(config.HEIGHT * 0.33)))
        self.screen.blit(title, (0, 0))
        for button in (self.setting_button, self.exit_button, self.help_button, self.play_button):
            self.screen.blit(button.image, button.rect)
        if self.current_state == "select":
            self.__draw_select()
        elif self.current_state == "play":
            self.game_over = self.game_mode.run(signal)
        elif self.current_state == "setting":
            self.__draw_setting()
        elif self.current_state == "exit":
            self.__draw_exit()
        elif self.current_state == "help":
            self.__draw_help()
        for button in (self.setting_button, self.exit_button, self.help_button):
            self.screen.blit(button.image, button.rect)

    def __music(self, type: str):
        TEMP = self.bg_music.get_volume()
        self.bg_music.stop()
        if type == "select":
            self.bg_music = mixer.Sound(os.path.join(self.PATH_MUSIC, "select.mp3"))
        elif type == "solo":
            self.bg_music = mixer.Sound(os.path.join(self.PATH_MUSIC, "solo.mp3"))
        else:
            self.bg_music = mixer.Sound(os.path.join(self.PATH_MUSIC, "music.mp3"))  # type == "main"
        self.bg_music.set_volume(TEMP)
        self.bg_music.play(-1)
        # Update OptionManager's bg_music reference
        self.option_manager.bg_music = self.bg_music

    def react_to_click(self, pos: tuple[int, int]):
        """ Return `True` if exit button is clicked, else `False` """
        if self.current_state == "main":
            if self.setting_button.is_clicked(pos):
                self.click_sound.play()
                self.current_state = "setting"
            elif self.exit_button.is_clicked(pos):
                self.click_sound.play()
                self.current_state = "exit"
            elif self.help_button.is_clicked(pos):
                self.click_sound.play()
                self.current_state = "help"
            elif self.play_button.is_clicked(pos):
                self.click_sound.play()
                self.current_state = "select"
                self.__music("select")
        elif self.current_state == "setting":
            result = self.option_manager.handle_setting_click(pos)
            if result == "main":
                self.current_state = "main"
        elif self.current_state == "help":
            if self.x_button.is_clicked(pos):
                self.click_sound.play()
                self.current_state = "main"
        elif self.current_state == "exit":
            result = self.option_manager.handle_exit_click(pos)
            if result is True:
                return True
            elif result == "main":
                self.current_state = "main"
        elif self.current_state == "select":
            if pygame.Rect(int(config.WIDTH * 0.45), int(config.HEIGHT * 0.34), int(config.WIDTH * 0.1), int(config.HEIGHT * 0.1)).collidepoint(pos):
                self.pos = pos
                self.__music("solo")
                self.current_state = "play"
                self.__set_game_mode("Solo")
        return False

    def react_to_gameover(self):
        if self.game_over:
            self.__music("main")
            self.game_over = False
            self.current_state = "main"
