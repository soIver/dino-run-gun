import pygame
from config import SCREEN_WIDTH, GROUND_LEVEL


class Obstacle:
    """базовый класс для всех препятствий"""
    def __init__(self, x, y, width, height, color, is_destructible, obstacle_type, is_flying=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.destroyed = False
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_destructible = is_destructible
        self.obstacle_type = obstacle_type
        self.is_flying = is_flying
        self.health = 1 if is_destructible else 0

    def update(self, game_speed):
        # движение препятствия
        self.x -= game_speed
        self.rect.x = self.x

    def check_collision(self, dinosaur):
        # проверка столкновения с дино
        return self.rect.colliderect(dinosaur.rect)

    def is_off_screen(self):
        # ушло ли за экран
        return self.x + self.width < 0

    def handle_fireball_collision(self, fireball):
        """обработка столкновения с огненным шаром"""
        if self.is_destructible:
            self.health -= 1
            if self.health <= 0:
                self.destroyed = True
        return True



class GroundObstacle(Obstacle):
    # наземные препятствия
    def __init__(self, x, y, width, height, color, is_destructible, obstacle_type):
        ground_y = GROUND_LEVEL - height
        super().__init__(x, ground_y, width, height, color, is_destructible, obstacle_type, is_flying=False)


class FlyingObstacle(Obstacle):
    # летающие препятствия
    def __init__(self, x, y, width, height, color, is_destructible):
        min_y = GROUND_LEVEL - height - 15
        if y > min_y:
            y = min_y
        super().__init__(x, y, width, height, color, is_destructible, 'flying', is_flying=True)