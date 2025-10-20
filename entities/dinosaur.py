import pygame
from config import GROUND_LEVEL, GRAVITY, JUMP_STRENGTH, DUCKING_GRAVITY_MULTIPLIER, FIREBALL_COOLDOWN


class Dinosaur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 3
        self.velocity_y = 0
        self.cooldown = FIREBALL_COOLDOWN
        self.can_shoot = True
        self.is_jumping = False
        self.is_ducking = False
        self.is_running = True
        self.is_alive = True
        self.is_duck_key_pressed = False

        # хитбоксы для разных состояний
        self.normal_rect = pygame.Rect(x, y, 40, 60)
        self.ducking_rect = pygame.Rect(x, GROUND_LEVEL - 30, 40, 30)

    @property
    def rect(self):
        return self.ducking_rect if self.is_ducking else self.normal_rect

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.velocity_y = -JUMP_STRENGTH
            self.is_jumping = True

    def duck(self):
        self.is_duck_key_pressed = True
        if not self.is_jumping:
            self.is_ducking = True

    def stand_up(self):
        self.is_duck_key_pressed = False
        if not self.is_jumping:
            self.is_ducking = False

    def shoot(self, game_speed):
        if not self.is_ducking and self.can_shoot:
            current_time = pygame.time.get_ticks()
            self.can_shoot = False
            self.cooldown_timer = current_time + FIREBALL_COOLDOWN
            from entities.fireball import Fireball
            return Fireball(self.x + 50, self.y + 20, game_speed)
        return None

    def update(self):
        current_time = pygame.time.get_ticks()
        # првоерка кулдауна на выстрел
        if not self.can_shoot and current_time >= self.cooldown_timer:
            self.can_shoot = True

        if self.is_ducking:
            self.ducking_rect.x = self.x
            self.ducking_rect.y = GROUND_LEVEL - 30
        else:
            self.normal_rect.x = self.x
            self.normal_rect.y = self.y

        if self.is_jumping:
            current_gravity = GRAVITY
            if self.is_duck_key_pressed:
                current_gravity = GRAVITY * DUCKING_GRAVITY_MULTIPLIER
            self.velocity_y += current_gravity
            self.y += self.velocity_y
            # приземление
            if self.y >= GROUND_LEVEL - 60:
                self.y = GROUND_LEVEL - 60
                self.is_jumping = False
                self.velocity_y = 0

                # переходим в приседание если клавиша все еще нажата
                if self.is_duck_key_pressed:
                    self.is_ducking = True