import pygame

class Animation:
    def __init__(self, sprite_sheet_path, frame_count, frame_duration, loop=True, scale=1.0):
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_count = frame_count
        self.frame_width = self.sprite_sheet.get_width() // frame_count
        self.frame_height = self.sprite_sheet.get_height()
        self.frame_duration = frame_duration
        self.loop = loop
        self.scale = scale # пропорциональное увеличение спрайтов относительно исходного размера
        self.frames = []
        self._split_frames() # всегда делим лист на спрайты при инициализации
        self.current_frame = 0
        self.timer = 0
        self.active = True
        self.forward = True  # направление воспроизведения
    
    def _split_frames(self):
        for i in range(self.frame_count):
            frame_rect = pygame.Rect(
                i * self.frame_width, 0,
                self.frame_width, self.frame_height
            )
            frame = self.sprite_sheet.subsurface(frame_rect)
            if self.scale != 1.0:
                new_size = (int(self.frame_width * self.scale), int(self.frame_height * self.scale))
                frame = pygame.transform.scale(frame, new_size)
            self.frames.append(frame)
    
    def update(self, dt, speed_multiplier=1.0):
        if not self.active:
            return
            
        self.timer += dt
        adjusted_duration = self.frame_duration / max(0.1, speed_multiplier)  # защита от деления на 0
        
        if self.timer >= adjusted_duration:
            self.timer = 0
            
            if self.forward:
                self.current_frame += 1
                if self.current_frame >= self.frame_count:
                    if self.loop:
                        self.current_frame = 0
                    else:
                        self.current_frame = self.frame_count - 1
                        self.active = False
            else:
                self.current_frame -= 1
                if self.current_frame < 0:
                    if self.loop:
                        self.current_frame = self.frame_count - 1
                    else:
                        self.current_frame = 0
                        self.active = False
    
    def get_current_frame(self):
        return self.frames[self.current_frame]
    
    def reset(self, forward=True):
        self.current_frame = 0 if forward else self.frame_count - 1
        self.timer = 0
        self.active = True
        self.forward = forward
    
    def set_frame(self, frame_index):
        self.current_frame = max(0, min(frame_index, self.frame_count - 1))
    
    def is_complete(self) -> bool:
        '''проверка анимации на завершение'''
        if self.forward:
            return self.current_frame >= self.frame_count - 1 and not self.loop
        else:
            return self.current_frame <= 0 and not self.loop