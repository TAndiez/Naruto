import pygame
import os
import config   # ✅ import nguyên module thay vì import WIDTH, HEIGHT

class OptionManager:
    """
    Handles the logic and drawing for Setting and Exit options.
    Can be used independently from Interface for modularity.
    """
    def __init__(self, screen, image_path, music_path, 
                 bg_music, click_sound,
                 vol_music_button, vol_sound_button,
                 setting_button, exit_button,
                 yes_button, no_button, x_button):

        self.screen = screen
        self.PATH_IMAGES = image_path
        self.PATH_MUSIC = music_path
        self.bg_music = bg_music
        self.click_sound = click_sound
        self.vol_music_button = vol_music_button
        self.vol_sound_button = vol_sound_button
        self.setting_button = setting_button
        self.exit_button = exit_button
        self.yes_button = yes_button
        self.no_button = no_button
        self.x_button = x_button
        self.dragging_vol_music = False
        self.dragging_vol_sound = False

    def draw_setting(self):
        # background setting box ~ 50% W, 66% H
        SETTING_IMG = pygame.image.load(os.path.join(self.PATH_IMAGES, "setting.png"))
        SCALED_SETTING_IMG = pygame.transform.scale(
            SETTING_IMG, (int(config.WIDTH * 0.5), int(config.HEIGHT * 0.66))
        )
        self.screen.blit(SCALED_SETTING_IMG, (config.WIDTH * 0.25, config.HEIGHT * 0.16))

        # thanh bar âm nhạc
        BAR_IMG = pygame.image.load(os.path.join(self.PATH_IMAGES, "scroll_bar.png"))
        SCALED_BAR_IMG = pygame.transform.scale(BAR_IMG, (int(config.WIDTH * 0.3), int(config.HEIGHT * 0.03)))
        self.screen.blit(SCALED_BAR_IMG, (config.WIDTH * 0.35, config.HEIGHT * 0.42))
        self.screen.blit(SCALED_BAR_IMG, (config.WIDTH * 0.35, config.HEIGHT * 0.63))

        # highlight setting
        SETTING_HIGHLIGHT = pygame.image.load(os.path.join(self.PATH_IMAGES, "setting_button_highlight.png"))
        TEMP = self.setting_button.image
        self.setting_button.image = pygame.transform.scale(
            SETTING_HIGHLIGHT, (int(config.WIDTH * 0.11), int(config.HEIGHT * 0.15))
        )
        for button in (self.setting_button, self.vol_music_button, self.vol_sound_button, self.x_button):
            self.screen.blit(button.image, button.rect)
        self.setting_button.image = TEMP

        # xử lý kéo thả volume
        MOUSE_POS = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:  # left click
            if self.vol_music_button.is_clicked(MOUSE_POS) or self.dragging_vol_music:
                self.dragging_vol_music = True
                new_x = max(int(config.WIDTH * 0.375), min(MOUSE_POS[0], int(config.WIDTH * 0.625)))
                self.vol_music_button.rect.centerx = new_x
                self.bg_music.set_volume((new_x - config.WIDTH * 0.375) / (config.WIDTH * 0.25))
            elif self.vol_sound_button.is_clicked(MOUSE_POS) or self.dragging_vol_sound:
                self.dragging_vol_sound = True
                new_x = max(int(config.WIDTH * 0.375), min(MOUSE_POS[0], int(config.WIDTH * 0.625)))
                self.vol_sound_button.rect.centerx = new_x
                self.click_sound.set_volume((new_x - config.WIDTH * 0.375) / (config.WIDTH * 0.25))
        else:
            self.dragging_vol_music = False
            self.dragging_vol_sound = False

    def draw_exit(self):
        EXIT_BG_IMG = pygame.image.load(os.path.join(self.PATH_IMAGES, "exit_bg.png"))
        SCALED_EXIT_BG_IMG = pygame.transform.scale(
            EXIT_BG_IMG, (int(config.WIDTH * 0.5), int(config.HEIGHT * 0.66))
        )
        self.screen.blit(SCALED_EXIT_BG_IMG, (config.WIDTH * 0.25, config.HEIGHT * 0.16))

        EXIT_HIGHLIGHT = pygame.image.load(os.path.join(self.PATH_IMAGES, "exit_button_highlight.png"))
        TEMP = self.exit_button.image
        self.exit_button.image = pygame.transform.scale(
            EXIT_HIGHLIGHT, (int(config.WIDTH * 0.1), int(config.HEIGHT * 0.13))
        )
        for button in (self.exit_button, self.yes_button, self.no_button):
            self.screen.blit(button.image, button.rect)
        self.exit_button.image = TEMP

    def handle_setting_click(self, pos):
        if self.x_button.is_clicked(pos):
            self.click_sound.play()
            return "main"
        return None

    def handle_exit_click(self, pos):
        if self.yes_button.is_clicked(pos):
            return True
        elif self.no_button.is_clicked(pos):
            self.click_sound.play()
            return "main"
        return None
