import os
import random
import pygame
import config


def create_map(filename: str):
    width = 40
    height = 30
    cloud_size = 4 
    cloud_chance = 0.5

    map_data = [[0 for _ in range(width)] for _ in range(height)]

    for j in range(height):
        for i in range(width):
            if j >= height - 5: 
                map_data[j][i] = 1
            elif j == height - 6:  
                map_data[j][i] = 2
            else:
                map_data[j][i] = 0

    for j in range(0, 10, cloud_size):
        for i in range(0, height - cloud_size, cloud_size):
            if random.random() < cloud_chance:
                map_data[j][i] = 3
    with open(filename, "w") as f:
        for row in map_data:
            f.write(" ".join(map(str, row)) + "\n")
class Map:
    def __init__(self, screen: pygame.surface, PATH: str, PATH_MAP: str, name_map: str, PATH_MAP_IMAGE: str):
        self.screen = screen
        self.PATH = PATH
        self.PATH_MAP = PATH_MAP
        self.PATH_MAP_IMAGE = PATH_MAP_IMAGE
        self.name_map = name_map
        self.viewport_width = 40
        self.viewport_height = 30
        self.BLOCK_SIZE_X = round(config.WIDTH / 40)
        self.BLOCK_SIZE_Y = round(config.HEIGHT / 30)

        with open(os.path.join(self.PATH_MAP, self.name_map), "r") as f:
            self.map_data = [list(map(int, line.split())) for line in f.readlines()]

    def draw_map_solo(self):
        self.BLOCK_SIZE_X = round(config.WIDTH / 40)
        self.BLOCK_SIZE_Y = round(config.HEIGHT / 30)
        images = pygame.transform.scale(pygame.image.load(os.path.join(self.PATH_MAP_IMAGE)).convert_alpha(), (config.WIDTH, config.HEIGHT))
        self.screen.blit(images, (0,0))

    def draw_map_adventure(self):
        drawn_blocks = set()  
        for value in sorted(self.images.keys()):  # [0,1,2,3,4,5]
            for y in range(self.viewport_height):
                for x in range(self.viewport_width):
                    map_x = x
                    map_y = y

                    if 0 <= map_y < len(self.map_data) and 0 <= map_x < len(self.map_data[0]):
                        tile_value = self.map_data[map_y][map_x]
                        if tile_value != value:
                            continue

                        img = self.images.get(tile_value, self.images[1])
                        pixel_x = x * self.BLOCK_SIZE_X
                        pixel_y = y * self.BLOCK_SIZE_Y

                        self.screen.blit(img, (pixel_x, pixel_y))
                        if tile_value == 4:
                            for dx in range(4):
                                for dy in range(4):
                                    drawn_blocks.add((map_x + dx, map_y + dy))
                        elif tile_value == 5:
                            for dx in range(6):
                                for dy in range(8):
                                    drawn_blocks.add((map_x + dx, map_y + dy))
                        elif tile_value == 6:
                            for dx in range(2):
                                for dy in range(2):
                                    drawn_blocks.add((map_x + dx, map_y + dy))
                        elif tile_value == 7:
                            for dx in range(4):
                                for dy in range(4):
                                    drawn_blocks.add((map_x + dx, map_y + dy))

    # New collision helpers with clear semantics
    def is_solid_tile_value(self, value: int) -> bool:
        return value == 1

    def is_solid_at_pixel(self, x: int, y: int) -> bool:
        cell_x = x // self.BLOCK_SIZE_X
        cell_y = y // self.BLOCK_SIZE_Y
        if cell_x < 0 or cell_y < 0:
            return True
        if cell_y >= len(self.map_data) or cell_x >= len(self.map_data[0]):
            return True
        return self.is_solid_tile_value(self.map_data[cell_y][cell_x])

    def rect_collides(self, rect: pygame.Rect) -> bool:
    # Nếu rect nằm ngoài map -> coi như va chạm
        if rect.left < 0 or rect.top < 0:
            return True
        if rect.right > len(self.map_data[0]) * self.BLOCK_SIZE_X:
            return True
        if rect.bottom > len(self.map_data) * self.BLOCK_SIZE_Y:
            return True

        left_cell = rect.left // self.BLOCK_SIZE_X
        right_cell = (rect.right - 1) // self.BLOCK_SIZE_X
        top_cell = rect.top // self.BLOCK_SIZE_Y
        bottom_cell = (rect.bottom - 1) // self.BLOCK_SIZE_Y

        for cy in range(top_cell, bottom_cell + 1):
            for cx in range(left_cell, right_cell + 1):
                if self.is_solid_tile_value(self.map_data[cy][cx]):
                    return True
        return False


