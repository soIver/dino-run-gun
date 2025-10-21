import pygame
from config import GROUND_LEVEL, GRAVITY, JUMP_STRENGTH, DUCKING_GRAVITY_MULTIPLIER, FIREBALL_COOLDOWN
from entities.animation import Animation
from entities.fireball import Fireball
from assets.config import ANIMATION_CONFIG

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
        self.was_ducking = False
        self.is_running = True
        self.is_alive = True
        self.is_duck_key_pressed = False

        # анимации разных частей тела
        self.animations: dict[str, Animation] = {}
        self.current_head_anim = None
        self.current_body_anim = None
        self.current_legs_anim = None
        self.is_shooting = False
        self.duck_animation_frame = 0
        self.shoot_delay_timer = 0
        self.shoot_delay_active = False

        # хитбоксы для разных состояний
        self.normal_rect = pygame.Rect(x, y, 40, 60)
        self.ducking_rect = pygame.Rect(x, y+20, 40, 30)

    def load_animations(self, animation_config: dict[str, dict[str, str | int]]):
        for anim_name, config in animation_config.items():
            self.animations[anim_name] = Animation(
                config['path'],
                config['frame_count'],
                config['frame_duration'],
                config.get('loop', True),
                scale=3.0
            )
        
        # установка начальных анимаций
        self.current_body_anim = self.animations['dino_body_run']
        self.current_head_anim = self.animations['dino_head_run']
        self.current_legs_anim = self.animations['dino_legs_run']

    @property
    def rect(self):
        return self.ducking_rect if self.is_ducking else self.normal_rect

    def jump(self):
        if not self.is_jumping:
            # мгновенно меняем состояние хитбокса при прыжке
            if self.is_ducking:
                self.is_ducking = False
                self.current_body_anim = self.animations['dino_body_run']
                self.current_head_anim = self.animations['dino_head_run']
            
            self.velocity_y = -JUMP_STRENGTH
            self.is_jumping = True

    def duck(self):
        self.is_duck_key_pressed = True
        if not self.is_jumping and not self.is_ducking:
            # запуск анимации приседания
            self.is_ducking = True
            self.animations['dino_body_duck'].reset(forward=False)
            self.current_body_anim = self.animations['dino_body_duck']
            self.current_head_anim = None

    def stand_up(self):
        self.is_duck_key_pressed = False
        if self.is_ducking and not self.is_jumping:
            # запуск быстрой анимации вставания
            duck_anim = self.animations['dino_body_duck']
            duck_anim.reset(forward=True)

    def shoot(self, game_speed):
        if not self.is_ducking and self.can_shoot and not self.shoot_delay_active:
            current_time = pygame.time.get_ticks()
            self.can_shoot = False
            self.cooldown_timer = current_time + FIREBALL_COOLDOWN
            # Запуск анимации выстрела
            self.is_shooting = True
            self.current_head_anim = self.animations['dino_head_shoot']
            self.animations['dino_head_shoot'].reset(forward=True)
            # Задержка перед появлением снаряда
            self.shoot_delay_active = True
            self.shoot_delay_timer = current_time + 200  # 200ms задержка перед появлением снаряда

    def update(self, dt, game_speed):
        current_time = pygame.time.get_ticks()
        # проверка кулдауна на выстрел
        if not self.can_shoot and current_time >= self.cooldown_timer:
            self.can_shoot = True
        
        # проверка задержки перед созданием снаряда
        if self.shoot_delay_active and current_time >= self.shoot_delay_timer:
            self.shoot_delay_active = False
            fireball = Fireball(self.x + 50, self.y + 15, game_speed)
            # загружаем анимации для снаряда
            fireball.load_animations(ANIMATION_CONFIG)
            return fireball

        # множитель скорости для анимаций на основании скорости игры
        speed_multiplier = game_speed / 10.0

        # обновление анимации ног всегда, кроме прыжка
        if self.current_legs_anim and not self.is_jumping:
            self.current_legs_anim.update(dt, speed_multiplier)

        duck_anim = self.animations['dino_body_duck']
        if self.current_body_anim == duck_anim:
            duck_anim.update(dt)
            
            # завершение анимации вставания
            if duck_anim.forward and duck_anim.is_complete():
                self.is_ducking = False
                self.current_body_anim = self.animations['dino_body_run']
                self.current_head_anim = self.animations['dino_head_run']
            
            # завершение анимации приседания
            elif not duck_anim.forward and duck_anim.is_complete():
                self.is_ducking = True
                self.duck_animation_frame = duck_anim.current_frame
        
        # обновление анимации головы кроме случаев приседания
        if self.current_head_anim and self.current_body_anim != duck_anim:
            self.current_head_anim.update(dt)
            
            # возврат к бегущей анимации головы после завершения стрельбы
            if (self.is_shooting and 
                self.current_head_anim == self.animations['dino_head_shoot'] and
                self.current_head_anim.is_complete()):
                self.is_shooting = False
                self.current_head_anim = self.animations['dino_head_run']
        
        # обновление анимации тела, если не в присяде
        if (self.current_body_anim and 
            self.current_body_anim != duck_anim and 
            not self.is_jumping):
            self.current_body_anim.update(dt, speed_multiplier)
        elif self.is_ducking:
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
                    self.animations['dino_body_duck'].reset(forward=False)
                    self.current_body_anim = self.animations['dino_body_duck']
                    self.current_head_anim = None

    def draw(self, screen):
        body_y = self.y
        if self.is_ducking and self.current_body_anim == self.animations['dino_body_duck']:
            # отрисовка присевшего динозавра (тело + голова)
            duck_frame = self.current_body_anim.get_current_frame()
            screen.blit(duck_frame, (self.x - 45, body_y - 20))
            
            if self.current_legs_anim:
                legs_frame = self.current_legs_anim.get_current_frame()
                screen.blit(legs_frame, (self.x - 45, body_y - 23))
            
        else:
            # отрисовка динозавра по частям, если он не сидит
            
            # ноги
            if self.current_legs_anim:
                legs_frame = self.current_legs_anim.get_current_frame()
                screen.blit(legs_frame, (self.x - 45, body_y - 23))
            
            # тело
            if self.current_body_anim:
                body_frame = self.current_body_anim.get_current_frame()
                screen.blit(body_frame, (self.x - 45, body_y - 20))
            
            # голова
            if self.current_head_anim:
                head_frame = self.current_head_anim.get_current_frame()
                screen.blit(head_frame, (self.x - 45, body_y - 17))
        