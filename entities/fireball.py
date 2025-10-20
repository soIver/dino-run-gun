import pygame
from config import SCREEN_WIDTH, FIREBALL_SPEED
from entities.animation import Animation


class Fireball:
    def __init__(self, x, y, game_speed):
        self.x = x
        self.y = y
        self.speed = game_speed + FIREBALL_SPEED
        self.game_speed = game_speed  # сохранение скорости игры для движения взрыва
        self.active = True
        self.rect = pygame.Rect(x, y, 20, 20)
        
        # анимации
        self.animations = {}
        self.current_animation = None
        self.is_exploding = False
        self.explosion_complete = False

    def load_animations(self, animation_config):
        for anim_name, config in animation_config.items():
            if anim_name.startswith('fireball_'):
                self.animations[anim_name] = Animation(
                    config['path'],
                    config['frame_count'],
                    config['frame_duration'],
                    config.get('loop', True),
                    scale=3.0
                )
        
        # установка начальной анимации полёта
        self.current_animation = self.animations['fireball_fly']

    def explode(self):
        if not self.is_exploding:
            self.is_exploding = True
            self.current_animation = self.animations['fireball_explode']
            self.current_animation.reset(forward=True)
            self.speed = -self.game_speed

    def update(self):
        if not self.active:
            return
            
        # обновление анимации
        if self.current_animation:
            self.current_animation.update(16)
            
            # если анимация взрыва завершена, деактивируем снаряд
            if self.is_exploding and self.current_animation.is_complete():
                self.active = False
                self.explosion_complete = True
                return
        
        self.x += self.speed
        self.rect.x = self.x
        
        # деактивация при выходе за экран
        if self.x > SCREEN_WIDTH or self.x < -100:
            self.active = False

    def check_collision(self, obstacle):
        # проверка столкновения с препятствием
        if not self.is_exploding and self.rect.colliderect(obstacle.rect):
            self.explode()
            return True
        return False

    def draw(self, screen):
        if self.current_animation and self.active:
            frame = self.current_animation.get_current_frame()
            screen.blit(frame, (self.x-10, self.y-10))