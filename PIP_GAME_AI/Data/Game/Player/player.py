import pygame
import config

from abc import abstractmethod
from Data.Game.character import Character


class Player(Character):
    def __init__(self, screen, name, level, health, power, chakra, map, pos, animation, skills, direct, key_map):
        super().__init__(screen, name, level, health, power, chakra, map, pos, animation)
        self.skills = skills
        self.ATTACK_RANGE = round(config.WIDTH * (30 / 800))
        self.direct = direct
        self.key_map = key_map
        self.jumping = False
        self.in_air = False
        self.check_at = False
        self.counter = 6
        self.last_power_up_time = pygame.time.get_ticks()
        self.last_attack_times = pygame.time.get_ticks()
        self.skill_lock = None   # None nghĩa là không bị khóa animation


    @abstractmethod
    def rescreen(self):
        pass

    def destroy(self):
        self.animation.stop()

    def get_chakra(self):
        return self.chakra.value
    
    def set_chakra(self, new_chakra):
        self.chakra.value = new_chakra

    def get_power(self):
        return self.pw.value

    def set_power(self, new_power):
        self.pw.value = new_power

    def update_power(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_power_up_time >= 1000 and self.pw.value < self.max_pw:
            self.pw.value += 5
            self.last_power_up_time = current_time

    def draw_attribute(self, id: int):
        if id == 0:
            self.screen.blit(self.animation.frames_dict.get("attribute")[0], (0, 0))

            sub_hp = min(self.max_hp - self.hp.value, self.max_hp)
            if sub_hp > 0:
                for i in range(1, (sub_hp + 1) // self.rate_hp):
                    self.screen.blit(
                        self.animation.frames_dict["attribute"][2],
                        (round(config.WIDTH * (154 / 800)) - i, round(config.HEIGHT * (17 / 600)))
                    )

            sub_power = min(self.max_pw - self.pw.value, self.max_pw)
            if sub_power > 0:
                for i in range(1, (sub_power + 1) // self.rate_pw):
                    self.screen.blit(
                        self.animation.frames_dict["attribute"][2],
                        (round(config.WIDTH * (149 / 800)) - i, round(config.HEIGHT * (33 / 600)))
                    )

            for i in range(1, self.chakra.value + 1):
                self.screen.blit(
                    self.animation.frames_dict["attribute"][3],
                    (round(config.WIDTH * (42 / 800)) + i, round(config.HEIGHT * (49 / 600)))
                )

        else:
            self.screen.blit(
                self.animation.frames_dict.get("attribute")[1],
                (round(config.WIDTH * 0.75), 0)
            )

            sub_hp = min(self.max_hp - self.hp.value, self.max_hp)
            if sub_hp > 0:
                for i in range(1, (sub_hp + 1) // self.rate_hp):
                    self.screen.blit(
                        self.animation.frames_dict["attribute"][2],
                        (round(config.WIDTH * (645 / 800)) + i, round(config.HEIGHT * (17 / 600)))
                    )

            sub_power = min(self.max_pw - self.pw.value, self.max_pw)
            if sub_power > 0:
                for i in range(1, (sub_power + 1) // self.rate_pw):
                    self.screen.blit(
                        self.animation.frames_dict["attribute"][2],
                        (round(config.WIDTH * (650 / 800)) + i, round(config.HEIGHT * (33 / 600)))
                    )

            for i in range(1, self.chakra.value + 1):
                self.screen.blit(
                    self.animation.frames_dict["attribute"][3],
                    (round(config.WIDTH * (757 / 800)) - i, round(config.HEIGHT * (49 / 600)))
                )

    def can_attack(self, enemy: "Player"):
        self.ATTACK_RANGE = round(config.WIDTH * (30 / 800))
        left1 = self.x
        right1 = self.x + self.size_x
        top1 = self.y
        bottom1 = self.y + self.size_y

        left2 = enemy.x
        right2 = enemy.x + enemy.size_x
        top2 = enemy.y
        bottom2 = enemy.y + enemy.size_y

        if self.direct:
            attack_left = right1
            attack_right = right1 + self.ATTACK_RANGE
        else:
            attack_left = left1 - self.ATTACK_RANGE
            attack_right = left1

        attack_top = top1
        attack_bottom = bottom1

        overlap_x = not (attack_right <= left2 or attack_left >= right2)
        overlap_y = not (attack_bottom <= top2 or attack_top >= bottom2)

        return overlap_x and overlap_y
    @abstractmethod
    def update_attack(self, enemy):
        pass

    def attack(self, enemy: "Player", keys, current_time):
        self.update_attack(enemy)
        if self.skill_lock is not None:
            return False
        if keys[self.key_map['attack1']]:
            if self.can_attack(enemy) and current_time - self.last_attack_times > 150:
                enemy.take_damage(5, self.x - enemy.x >= 0, 2, 100)
                self.last_attack_times = current_time
            self.animation.set_state("attack", current_time)
            return True

        if keys[self.key_map['skill1']] and not self.skills[0].active and self.skills[0].can_shoot(self):
            self.skills[0].shoot(self, (self.x, self.y), self.direct)
            self.animation.set_state("attack", current_time)

        if self.key_map.get('skill2') and keys[self.key_map['skill2']] and self.skills[1].can_shoot(self):
            self.skills[1].shoot(self, (self.x, self.y), self.direct)
            self.animation.set_state("attack", current_time)

        if self.key_map.get('skill3') and keys[self.key_map['skill3']] and self.skills[2].can_shoot(self):
            self.skills[2].shoot(self, (self.x, self.y), self.direct)
            self.animation.set_state("attack", current_time)

        if self.key_map.get('skill4') and keys[self.key_map['skill4']] and self.skills[3].can_shoot(self):
            self.skills[3].shoot(self, (self.x, self.y), self.direct)
            self.animation.set_state(self.skills[3].name, current_time)
            self.skill_lock = self.skills[3].name

        if self.key_map.get('skill5') and keys[self.key_map['skill5']] and self.skills[4].can_shoot(self):
            self.skills[4].shoot(self)
            self.animation.set_state(self.skills[4].name, current_time)
            self.skill_lock = self.skills[4].name

        return False

    def handle_move(self, keys, current_time: int, atk_act: bool):
        dx = 0
        L_shift = False
        if self.skill_lock is not None:
            return dx, L_shift
        if keys[self.key_map.get('down', -1)] and self.pw.value > 10:
            L_shift = True
            if keys[self.key_map['left']]:
                dx = -10
                self.direct = False
                self.pw.value -= 1
                if not atk_act:
                    self.animation.set_state("run", current_time)
            elif keys[self.key_map['right']]:
                dx = 10
                self.direct = True
                self.pw.value -= 1
                if not atk_act:
                    self.animation.set_state("run", current_time)
            else:
                if not atk_act:
                    self.animation.set_state("defend", current_time)
                    self.pw.value -= 1
        else:
            if keys[self.key_map['left']]:
                dx = -5
                self.direct = False
                if not atk_act:
                    self.animation.set_state("move", current_time)
            elif keys[self.key_map['right']]:
                dx = 5
                self.direct = True
                if not atk_act:
                    self.animation.set_state("move", current_time)
            else:
                if not atk_act:
                    self.animation.set_state("stand", current_time)

        return dx, L_shift


    def handle_jump(self, keys, current_time, L_shift):
        dy = 0
        if self.skill_lock is not None:
            return dy
        if keys[self.key_map['up']] and not self.in_air:
            self.jumping = True
            self.animation.set_state("stand", current_time)

        if self.jumping:
            if self.counter > 0:
                dy -= 15 if L_shift else 10
                self.pw.value -= 1 if L_shift else 0
                self.counter -= 1
            else:
                self.jumping = False
                self.counter = 10
        return dy

    def handle_gravity(self):
        if self.in_air:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed
        else:
            self.velocity_y = 0
        return self.velocity_y

    def handle_collision(self, dx, dy):
        step_x = 1 if dx > 0 else -1
        remaining_x = abs(dx)
        while remaining_x > 0:
            tentative_rect = pygame.Rect(self.x + step_x, self.y, self.size_x, self.size_y)
            if self.map.rect_collides(tentative_rect):
                break
            self.x += step_x
            remaining_x -= 1

        step_y = 1 if dy > 0 else -1
        remaining_y = abs(dy)
        collided_vertically = False
        while remaining_y > 0:
            tentative_rect = pygame.Rect(self.x, self.y + step_y, self.size_x, self.size_y)
            if self.map.rect_collides(tentative_rect):
                collided_vertically = True
                break
            self.y += step_y
            remaining_y -= 1
        left_foot  = self.map.is_solid_at_pixel(self.x + 2, self.y + self.size_y + 1)
        right_foot = self.map.is_solid_at_pixel(self.x + self.size_x - 2, self.y + self.size_y + 1)
        self.in_air = not (left_foot or right_foot)

        if collided_vertically and dy > 0:
            bottom = self.y + self.size_y
            snapped_bottom = round(bottom / 20) * 20
            self.y = snapped_bottom - self.size_y

    def update(self, enemy: Character, attribute_id: int):
        current_time = pygame.time.get_ticks()
        dx, dy = 0, 0
        atk_act = False
        if current_time - self.last_time_delay > self.delay:
            keys = pygame.key.get_pressed()
            atk_act = self.attack(enemy, keys, current_time)
            dx, L_shift = self.handle_move(keys, current_time, atk_act)
            dy = self.handle_jump(keys, current_time, L_shift)
            if self.skill_lock is None:
                if not any(keys):
                    self.animation.set_state("stand", current_time)
            
        else:
            if self.skill_lock:
                self.skill_lock = None
            self.update_attack(enemy)
            dx -= self.step_atk_x if self.get_atk_dir else -self.step_atk_x

        dy += self.handle_gravity()
        self.handle_collision(dx, dy)   
        self.update_power()
        self.draw_attribute(attribute_id)
        self.animation.update(current_time)
        self.animation.draw((round(self.x*(config.WIDTH / 800)), round(self.y * (config.HEIGHT / 600))), attribute_id, self.direct)
