import pygame
from config import SCREEN_WIDTH, FIREBALL_SPEED


class Fireball:
    def __init__(self, x, y, game_speed):
        self.x = x
        self.y = y
        self.speed = game_speed + FIREBALL_SPEED
        self.active = True
        self.rect = pygame.Rect(x, y, 20, 10)

    def update(self):
        # движение шара
        self.x += self.speed
        self.rect.x = self.x
        # деактивация при выходе за экран
        if self.x > SCREEN_WIDTH:
            self.active = False

    def check_collision(self, obstacle):
        # проверка столкновения с препятствием
        return self.rect.colliderect(obstacle.rect)