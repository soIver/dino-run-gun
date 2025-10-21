import pygame
import random
import time
from config import *
from entities.dinosaur import Dinosaur
from entities.fireball import Fireball
from entities.obstacles import GroundObstacle, FlyingObstacle


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dino Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()
        self.show_controls = True
        self.controls_timer = pygame.time.get_ticks()

        from assets.config import ANIMATION_CONFIG
        self.dinosaur.load_animations(ANIMATION_CONFIG)

    def reset_game(self):
        self.dinosaur = Dinosaur(100, GROUND_LEVEL - 60)
        from assets.config import ANIMATION_CONFIG
        self.dinosaur.load_animations(ANIMATION_CONFIG)
        self.fireballs: list[Fireball] = []
        self.obstacles: list[GroundObstacle | FlyingObstacle] = []
        self.game_speed = BASE_GAME_SPEED
        self.score = 0
        self.last_obstacle_time = 0
        self.last_speed_increase = pygame.time.get_ticks()
        self.game_over = False
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.dinosaur.jump()
                    elif event.key == pygame.K_DOWN:
                        self.dinosaur.duck()
                    elif event.key == pygame.K_f:
                        self.dinosaur.shoot(self.game_speed)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.dinosaur.stand_up()

    def generate_obstacle(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_obstacle_time > random.randint(1000, 3000):
            x = SCREEN_WIDTH
            is_destructible = random.random() < 0.3
            is_flying = random.choice([True, False])
            if is_flying:
                width = random.randint(30, 50)
                height = random.randint(30, 50)
                min_flying_height = 50
                max_flying_height = 170
                y = GROUND_LEVEL - random.randint(min_flying_height, max_flying_height)
                color = (255, 255, 0) if is_destructible else (0, 0, 255)
                obstacle = FlyingObstacle(x, y, width, height, color, is_destructible)

            else:
                if is_destructible and random.random() < 0.5:
                    obstacle_type = 'wall'
                    height = random.randint(180, 200)
                    width = random.randint(30, 50)
                    color = (255, 0, 0)
                else:
                    obstacle_type = 'jump'
                    height = random.randint(20, 40)
                    width = random.randint(40, 60)
                    color = (255, 255, 0) if is_destructible else (0, 0, 255)

                obstacle = GroundObstacle(x, 0, width, height, color, is_destructible, obstacle_type)

            self.obstacles.append(obstacle)
            self.last_obstacle_time = current_time

    def update_speed(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_speed_increase > SPEED_INCREASE_INTERVAL:
            self.game_speed += SPEED_INCREMENT
            self.last_speed_increase = current_time

    def update_game_state(self, dt):
        if self.game_over:
            return

        # проверка создания снаряда после задержки
        fireball = self.dinosaur.update(dt, self.game_speed)
        if fireball:
            self.fireballs.append(fireball)

        for fireball in self.fireballs[:]:
            fireball.update(dt)
            if not fireball.active:
                self.fireballs.remove(fireball)

        for obstacle in self.obstacles[:]:
            obstacle.update(self.game_speed)
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                self.score += 1

        self.check_collisions()
        self.generate_obstacle()
        self.update_speed()

        if self.show_controls and pygame.time.get_ticks() - self.controls_timer > 3000:
            self.show_controls = False

    def check_collisions(self):
        for obstacle in self.obstacles[:]:
            if obstacle.check_collision(self.dinosaur):
                self.dinosaur.hp -= 1
                self.obstacles.remove(obstacle)
                self.game_speed = max(BASE_GAME_SPEED, self.game_speed - SPEED_DECREMENT_ON_HIT)
                if self.dinosaur.hp <= 0:
                    self.game_over = True
                return

            for fireball in self.fireballs[:]:
                if fireball.check_collision(obstacle):
                    obstacle.handle_fireball_collision(fireball)

                    # удаляем снаряд только если он не взрывается
                    if not fireball.is_exploding and fireball in self.fireballs:
                        self.fireballs.remove(fireball)

                    if obstacle.destroyed and obstacle in self.obstacles:
                        self.obstacles.remove(obstacle)
                        self.score += 2
                    break

    def draw(self):
        self.screen.fill((255, 255, 255))

        pygame.draw.line(self.screen, (0, 0, 0), (0, GROUND_LEVEL - 30),
                         (SCREEN_WIDTH, GROUND_LEVEL - 30), 2)

        self.dinosaur.draw(self.screen)

        for fireball in self.fireballs:
            fireball.draw(self.screen)

        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, obstacle.color, obstacle.rect)

        score_text = self.font.render(f'Счёт: {self.score}', True, (0, 0, 0))
        speed_text = self.font.render(f'Скорость: {self.game_speed}', True, (0, 0, 0))
        hp_text = self.font.render(f'Здоровье: {self.dinosaur.hp}', True, (0, 0, 0))

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(speed_text, (10, 50))
        self.screen.blit(hp_text, (10, 90))

        if self.show_controls:
            controls_text = self.small_font.render('Нажмите F чтобы стрелять', True, (0, 0, 0))
            self.screen.blit(controls_text,
                             (SCREEN_WIDTH // 2 - controls_text.get_width() // 2,
                              50))

        if self.game_over:
            game_over_text = self.big_font.render('Вы вымерли', True, (255, 0, 0))
            restart_text = self.font.render('Нажмите R чтобы начать заново', True, (0, 0, 0))
            self.screen.blit(game_over_text,
                             (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                              SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text,
                             (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                              SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.get_time()
            self.handle_events()
            self.update_game_state(dt)
            self.draw()
            self.clock.tick(60)

        pygame.quit()