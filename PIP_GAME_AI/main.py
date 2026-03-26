from PIL import Image
import pygame
from API.Interface.interface import Interface
import config   # ✅ import nguyên module


def load_video(path: str):
    frames: list[pygame.Surface] = []
    with Image.open(path) as gif:
        i = 0
        try:
            while True:
                gif.seek(i)
                frame = gif.convert("RGBA")
                pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                frames.append(pygame_image)
                i += 1
        except EOFError:
            pass
    return frames


def setup():
    pygame.init()
    pygame.display.set_caption("The All-Knowing")
    pygame.display.set_icon(pygame.image.load("API\\Images\\logo.jpg"))
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)

    FRAMES = load_video("API\\Images\\background.gif")
    clock = pygame.time.Clock()
    frame_index = 0
    BG_FRAME_DELAY = 250
    last_bg_update = pygame.time.get_ticks()
    MAX_FRAME_INDEX = len(FRAMES) - 1

    interface = Interface(screen, "API\\Images", "API\\Music")
    fullscreen = False
    signal = False
    while True:
        screen.blit(pygame.transform.scale(FRAMES[frame_index], (config.WIDTH, config.HEIGHT)), (0, 0))
        interface.draw(signal)
        if signal:
            signal = False  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            # Resize cửa sổ
            if event.type == pygame.VIDEORESIZE:
                config.WIDTH, config.HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)
                interface.resize_ui()
                signal = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    config.WIDTH, config.HEIGHT = screen.get_size()
                else:
                    config.WIDTH, config.HEIGHT = config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT
                    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if interface.react_to_click(event.pos):
                    return
            else:
                interface.react_to_gameover()
        current_time = pygame.time.get_ticks()
        if current_time - last_bg_update >= BG_FRAME_DELAY:
            frame_index = (frame_index + 1) % (MAX_FRAME_INDEX + 1)
            last_bg_update = current_time

        pygame.display.flip()
        clock.tick(config.FPS)


if __name__ == "__main__":
    setup()
