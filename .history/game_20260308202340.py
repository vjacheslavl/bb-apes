import pygame
import sys
import math
import random
import struct
import wave
import os
from collections import deque

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


def generate_sound(filename, frequency, duration, volume=0.5, sound_type="sine"):
    if os.path.exists(filename):
        return
    sample_rate = 22050
    num_samples = int(sample_rate * duration)
    
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        if sound_type == "sine":
            value = math.sin(2 * math.pi * frequency * t)
        elif sound_type == "noise":
            value = random.uniform(-1, 1)
        elif sound_type == "square":
            value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
        elif sound_type == "sawtooth":
            value = 2 * (t * frequency - math.floor(t * frequency + 0.5))
        
        fade = 1.0
        fade_samples = int(num_samples * 0.1)
        if i < fade_samples:
            fade = i / fade_samples
        elif i > num_samples - fade_samples:
            fade = (num_samples - i) / fade_samples
        
        value = int(value * volume * fade * 32767)
        samples.append(struct.pack('<h', max(-32768, min(32767, value))))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(samples))


def generate_music(filename):
    if os.path.exists(filename):
        return
    sample_rate = 22050
    duration = 10.0
    num_samples = int(sample_rate * duration)
    
    samples = []
    base_freqs = [55, 58.27, 51.91, 55]
    
    for i in range(num_samples):
        t = i / sample_rate
        section = int(t / 2.5) % 4
        freq = base_freqs[section]
        
        value = 0
        value += 0.3 * math.sin(2 * math.pi * freq * t)
        value += 0.2 * math.sin(2 * math.pi * freq * 1.5 * t)
        value += 0.1 * math.sin(2 * math.pi * freq * 2 * t + math.sin(t * 0.5) * 0.5)
        value += 0.05 * random.uniform(-1, 1)
        
        pulse = 0.7 + 0.3 * math.sin(2 * math.pi * 0.5 * t)
        value *= pulse * 0.4
        
        value = int(value * 32767)
        samples.append(struct.pack('<h', max(-32768, min(32767, value))))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(samples))


generate_sound("shoot.wav", 800, 0.1, 0.15, "square")
generate_sound("damage.wav", 200, 0.15, 0.4, "sawtooth")
generate_sound("growl.wav", 80, 0.3, 0.5, "sawtooth")
generate_sound("door_break.wav", 80, 0.35, 0.7, "noise")
generate_sound("exit.wav", 600, 0.25, 0.4, "sine")
generate_music("music.wav")

shoot_sound = pygame.mixer.Sound("shoot.wav")
damage_sound = pygame.mixer.Sound("damage.wav")
growl_sound = pygame.mixer.Sound("growl.wav")
door_break_sound = pygame.mixer.Sound("door_break.wav")
exit_sound = pygame.mixer.Sound("exit.wav")

pygame.mixer.music.load("music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLUE = (50, 100, 200)
GRAY_LIGHT = (60, 60, 80)
GRAY_DARK = (40, 40, 60)
WALL_COLOR = (40, 35, 30)
TILE_SIZE = 50
PLAYER_SPEED = 3
BULLET_SPEED = 10
BULLET_COLOR = (255, 220, 50)
MAX_HP = 3
MEDKIT_COLOR = (255, 100, 100)
AMMO_COLOR = (100, 200, 100)
EXIT_COLOR = (100, 200, 255)
ZOMBIE_COLOR = (100, 150, 80)
ZOMBIE_SPEED = 0.7
ZOMBIE_HP = 2
ZOMBIE_SIZE = 40

font = None

LEVEL_DATA = [
    {
        "points_to_exit": 4,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 4, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 5, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 5, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 3, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 6, 6, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 5, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 3, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
    {
        "points_to_exit": 5,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 3, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 5, 0, 1, 1, 0, 0, 6, 0, 0, 1, 6, 6, 1, 0, 0, 0, 0, 0, 1, 5, 0, 1, 1],
            [1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 5, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 2, 3, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 5, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 6, 6, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 3, 0, 0, 0, 4, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
    {
        "points_to_exit": 7,
        "map": [
             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 6, 0, 0, 0, 1, 3, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 3, 1, 1],
            [1, 0, 5, 6, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 5, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 6, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 5, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 3, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 6, 3, 0, 0, 0, 0, 1, 1, 5, 0, 1],
            [1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 6, 6, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 1, 0, 5, 1, 0, 0, 1, 5, 5, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 1, 4, 0, 0, 1, 0, 0, 1, 0, 0, 1, 2, 3, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
]

def get_current_level_data(level):
    idx = min(level - 1, len(LEVEL_DATA) - 1)
    return LEVEL_DATA[idx]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WASD Movement Game")
clock = pygame.time.Clock()


def draw_floor(surface):
    for row in range(SCREEN_HEIGHT // TILE_SIZE + 1):
        for col in range(SCREEN_WIDTH // TILE_SIZE + 1):
            color = GRAY_LIGHT if (row + col) % 2 == 0 else GRAY_DARK
            pygame.draw.rect(surface, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))


class Particle:
    def __init__(self, x, y, color_type="red", direction=None):
        self.x = x
        self.y = y
        if direction:
            self.vx = direction[0] + random.uniform(-1, 1)
            self.vy = direction[1] + random.uniform(-1, 1)
        else:
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        self.size = random.randint(3, 6)
        if color_type == "red":
            self.color = (random.randint(180, 255), random.randint(0, 50), random.randint(0, 50))
        elif color_type == "yellow":
            self.color = (random.randint(200, 255), random.randint(180, 220), random.randint(0, 50))
        elif color_type == "gray":
            val = random.randint(150, 200)
            self.color = (val, val, val + 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


def spawn_particles(x, y, count, color_type="red", direction=None):
    return [Particle(x, y, color_type, direction) for _ in range(count)]


class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, WALL_COLOR, self.rect)
        
        brick_color = (55, 45, 40)
        mortar_color = (30, 25, 20)
        
        brick_h = 12
        brick_w = 24
        
        for row in range(self.rect.height // brick_h + 1):
            offset = (brick_w // 2) if row % 2 else 0
            y = self.rect.top + row * brick_h
            if y >= self.rect.bottom:
                break
            pygame.draw.line(surface, mortar_color, (self.rect.left, y), (self.rect.right, y), 1)
            
            for col in range(-1, self.rect.width // brick_w + 2):
                x = self.rect.left + col * brick_w + offset
                if self.rect.left <= x <= self.rect.right:
                    pygame.draw.line(surface, mortar_color, (x, y), (x, min(y + brick_h, self.rect.bottom)), 1)
        
        pygame.draw.rect(surface, (60, 50, 45), self.rect, 2)


class Medkit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 10, y + 10, 30, 30)
        self.alive = True

    def draw(self, surface):
        pygame.draw.rect(surface, MEDKIT_COLOR, self.rect)
        pygame.draw.rect(surface, WHITE, (self.rect.centerx - 8, self.rect.centery - 2, 16, 4))
        pygame.draw.rect(surface, WHITE, (self.rect.centerx - 2, self.rect.centery - 8, 4, 16))


class AmmoPack:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 10, y + 10, 30, 30)
        self.alive = True

    def draw(self, surface):
        pygame.draw.rect(surface, AMMO_COLOR, self.rect)
        pygame.draw.rect(surface, (50, 50, 50), (self.rect.centerx - 6, self.rect.centery - 8, 12, 16))


class Exit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, surface, player_has_enough_points):
        if player_has_enough_points:
            door_color = (180, 50, 50)
            border_color = (140, 35, 35)
            line_color = (120, 30, 30)
        else:
            door_color = (100, 40, 40)
            border_color = (70, 25, 25)
            line_color = (55, 20, 20)
        pygame.draw.rect(surface, door_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 3)
        pygame.draw.line(surface, line_color, (self.rect.left + 8, self.rect.top), (self.rect.left + 8, self.rect.bottom), 2)
        pygame.draw.line(surface, line_color, (self.rect.right - 8, self.rect.top), (self.rect.right - 8, self.rect.bottom), 2)
        pygame.draw.line(surface, line_color, (self.rect.centerx, self.rect.top), (self.rect.centerx, self.rect.bottom), 2)
        handle_color = (220, 180, 50) if player_has_enough_points else (80, 65, 30)
        pygame.draw.circle(surface, handle_color, (self.rect.right - 12, self.rect.centery), 4)


class Door:
    def __init__(self, x, y, row, col):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.row = row
        self.col = col
        self.alive = True

    def draw(self, surface):
        if not self.alive:
            return
        pygame.draw.rect(surface, (180, 180, 185), self.rect)
        pygame.draw.rect(surface, (140, 140, 145), self.rect, 3)
        pygame.draw.line(surface, (120, 120, 125), (self.rect.left + 8, self.rect.top), (self.rect.left + 8, self.rect.bottom), 2)
        pygame.draw.line(surface, (120, 120, 125), (self.rect.right - 8, self.rect.top), (self.rect.right - 8, self.rect.bottom), 2)
        pygame.draw.line(surface, (120, 120, 125), (self.rect.centerx, self.rect.top), (self.rect.centerx, self.rect.bottom), 2)
        pygame.draw.circle(surface, (90, 90, 95), (self.rect.right - 12, self.rect.centery), 4)


def find_path(start_x, start_y, target_x, target_y, level_map, doors=None):
    start_col = int(start_x // TILE_SIZE)
    start_row = int(start_y // TILE_SIZE)
    target_col = int(target_x // TILE_SIZE)
    target_row = int(target_y // TILE_SIZE)

    blocked_doors = set()
    if doors:
        for door in doors:
            if door.alive:
                blocked_doors.add((door.row, door.col))

    rows = len(level_map)
    cols = len(level_map[0])

    if start_row < 0 or start_row >= rows or start_col < 0 or start_col >= cols:
        return None
    if target_row < 0 or target_row >= rows or target_col < 0 or target_col >= cols:
        return None

    if (start_row, start_col) == (target_row, target_col):
        return None

    queue = deque([(start_row, start_col, [])])
    visited = {(start_row, start_col)}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        row, col, path = queue.popleft()

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < rows and 0 <= new_col < cols:
                is_wall = level_map[new_row][new_col] == 1
                is_blocked_door = (new_row, new_col) in blocked_doors
                if (new_row, new_col) not in visited and not is_wall and not is_blocked_door:
                    new_path = path + [(new_row, new_col)]

                    if (new_row, new_col) == (target_row, target_col):
                        return new_path

                    visited.add((new_row, new_col))
                    queue.append((new_row, new_col, new_path))

    return None


class Zombie:
    def __init__(self, x, y):
        self.x = x + (TILE_SIZE - ZOMBIE_SIZE) // 2
        self.y = y + (TILE_SIZE - ZOMBIE_SIZE) // 2
        self.width = ZOMBIE_SIZE
        self.height = ZOMBIE_SIZE
        self.hp = ZOMBIE_HP
        self.alive = True
        self.damage_cooldown = 0
        self.path_update_timer = 0
        self.speed_multiplier = 1.0
        self.angle = 0
        
        zombie_img = pygame.image.load("zombie.png").convert_alpha()
        self.original_surface = pygame.transform.scale(zombie_img, (self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, player, walls, level_map, doors):
        if not self.alive:
            return

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        zombie_cx = self.x + self.width // 2
        zombie_cy = self.y + self.height // 2
        player_cx = player.x + player.width // 2
        player_cy = player.y + player.height // 2

        look_dx = player_cx - zombie_cx
        look_dy = player_cy - zombie_cy
        self.angle = -math.degrees(math.atan2(look_dy, look_dx))

        path = find_path(zombie_cx, zombie_cy, player_cx, player_cy, level_map, doors)

        if path and len(path) > 0:
            next_row, next_col = path[0]
            target_x = next_col * TILE_SIZE + TILE_SIZE // 2
            target_y = next_row * TILE_SIZE + TILE_SIZE // 2

            dx = target_x - zombie_cx
            dy = target_y - zombie_cy
        else:
            dx = player_cx - zombie_cx
            dy = player_cy - zombie_cy

        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            dx /= dist
            dy /= dist

        old_x, old_y = self.x, self.y
        current_speed = ZOMBIE_SPEED * self.speed_multiplier
        self.x += dx * current_speed
        self.y += dy * current_speed

        zombie_rect = self.get_rect()
        for wall in walls:
            if zombie_rect.colliderect(wall.rect):
                self.x, self.y = old_x, old_y
                break
        else:
            for door in doors:
                if door.alive and zombie_rect.colliderect(door.rect):
                    self.x, self.y = old_x, old_y
                    break

    def take_damage(self):
        self.hp -= 1
        self.speed_multiplier += 0.5
        growl_sound.play()
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        if not self.alive:
            return
        rotated = pygame.transform.rotate(self.original_surface, self.angle)
        rect = rotated.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(rotated, rect.topleft)


def create_walls(level_map):
    walls = []
    for row_idx, row in enumerate(level_map):
        for col_idx, cell in enumerate(row):
            if cell == 1:
                walls.append(Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return walls


def create_pickups(level_map):
    medkits = []
    ammo_packs = []
    exits = []
    zombies = []
    doors = []
    for row_idx, row in enumerate(level_map):
        for col_idx, cell in enumerate(row):
            if cell == 2:
                medkits.append(Medkit(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            elif cell == 3:
                ammo_packs.append(AmmoPack(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            elif cell == 4:
                exits.append(Exit(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            elif cell == 5:
                zombies.append(Zombie(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            elif cell == 6:
                doors.append(Door(col_idx * TILE_SIZE, row_idx * TILE_SIZE, row_idx, col_idx))
    return medkits, ammo_packs, exits, zombies, doors


def break_connected_doors(door, doors):
    to_break = [door]
    broken = set()
    
    while to_break:
        current = to_break.pop()
        if current in broken:
            continue
        current.alive = False
        broken.add(current)
        
        for other in doors:
            if other.alive and other not in broken:
                if abs(other.row - current.row) + abs(other.col - current.col) == 1:
                    to_break.append(other)
    
    return list(broken)


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.radius = 5
        angle_rad = math.radians(-angle)
        self.vx = math.cos(angle_rad) * BULLET_SPEED
        self.vy = math.sin(angle_rad) * BULLET_SPEED
        self.alive = True

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy
        
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.alive = False
            return
        
        for wall in walls:
            if wall.rect.collidepoint(self.x, self.y):
                self.alive = False
                return

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 45
        self.height = 45
        self.speed = PLAYER_SPEED
        self.angle = 0
        self.hp = 3
        self.ammo = 2
        self.points = 0
        
        player_img = pygame.image.load("player.png").convert_alpha()
        self.original_surface = pygame.transform.scale(player_img, (self.width, self.height))

    def shoot(self, walls):
        if self.ammo > 0:
            self.ammo -= 1
            shoot_sound.play()
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            angle_rad = math.radians(-self.angle)
            recoil = 5
            old_x, old_y = self.x, self.y
            self.x -= math.cos(angle_rad) * recoil
            self.y -= math.sin(angle_rad) * recoil
            
            self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
            self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
            for wall in walls:
                if self.get_rect().colliderect(wall.rect):
                    self.x, self.y = old_x, old_y
                    break
            
            return Bullet(center_x, center_y, self.angle)
        return None

    def heal(self, amount):
        self.hp = min(self.hp + amount, MAX_HP)

    def add_ammo(self, amount):
        self.ammo += amount

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def handle_input(self, keys, walls, doors):
        old_x, old_y = self.x, self.y

        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

        player_rect = self.get_rect()
        for wall in walls:
            if player_rect.colliderect(wall.rect):
                self.x, self.y = old_x, old_y
                break
        else:
            for door in doors:
                if door.alive and player_rect.colliderect(door.rect):
                    self.x, self.y = old_x, old_y
                    break

    def look_at_mouse(self, mouse_pos):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        dx = mouse_pos[0] - center_x
        dy = mouse_pos[1] - center_y
        self.angle = -math.degrees(math.atan2(dy, dx))

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.original_surface, self.angle)
        rect = rotated.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(rotated, rect.topleft)


def draw_ui(surface, player, level, points_to_exit):
    global font
    if font is None:
        font = pygame.font.Font(None, 36)
    
    hp_text = font.render(f"HP: {player.hp}", True, (255, 80, 80))
    ammo_text = font.render(f"Ammo: {player.ammo}", True, (255, 220, 50))
    points_text = font.render(f"Points: {player.points}/{points_to_exit}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    location_text = font.render("Police station", True, (180, 180, 180))
    
    surface.blit(hp_text, (10, 10))
    surface.blit(ammo_text, (10, 45))
    surface.blit(points_text, (SCREEN_WIDTH - points_text.get_width() - 10, 10))
    surface.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 45))
    surface.blit(location_text, (SCREEN_WIDTH - location_text.get_width() - 10, 80))


def main():
    level = 1
    level_data = get_current_level_data(level)
    current_map = level_data["map"]
    points_to_exit = level_data["points_to_exit"]
    
    player = Player(50, SCREEN_HEIGHT - 100)
    walls = create_walls(current_map)
    medkits, ammo_packs, exits, zombies, doors = create_pickups(current_map)
    bullets = []
    particles = []
    damage_cooldown = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    bullet = player.shoot(walls)
                    if bullet:
                        bullets.append(bullet)
                        angle_rad = math.radians(-player.angle)
                        muzzle_x = player.x + player.width // 2 + math.cos(angle_rad) * 25
                        muzzle_y = player.y + player.height // 2 + math.sin(angle_rad) * 25
                        particles.extend(spawn_particles(muzzle_x, muzzle_y, 6, "yellow", (math.cos(angle_rad) * 3, math.sin(angle_rad) * 3)))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bullet = player.shoot(walls)
                    if bullet:
                        bullets.append(bullet)
                        angle_rad = math.radians(-player.angle)
                        muzzle_x = player.x + player.width // 2 + math.cos(angle_rad) * 25
                        muzzle_y = player.y + player.height // 2 + math.sin(angle_rad) * 25
                        particles.extend(spawn_particles(muzzle_x, muzzle_y, 6, "yellow", (math.cos(angle_rad) * 3, math.sin(angle_rad) * 3)))

        keys = pygame.key.get_pressed()
        player.handle_input(keys, walls, doors)
        
        mouse_pos = pygame.mouse.get_pos()
        player.look_at_mouse(mouse_pos)

        for zombie in zombies:
            zombie.update(player, walls, current_map, doors)

        for bullet in bullets:
            bullet.update(walls)
        bullets = [b for b in bullets if b.alive]

        for bullet in bullets:
            for zombie in zombies:
                if zombie.alive and zombie.get_rect().collidepoint(bullet.x, bullet.y):
                    bullet.alive = False
                    damage_sound.play()
                    
                    knockback = 15
                    dist = math.sqrt(bullet.vx * bullet.vx + bullet.vy * bullet.vy)
                    if dist > 0:
                        old_x, old_y = zombie.x, zombie.y
                        zombie.x += (bullet.vx / dist) * knockback
                        zombie.y += (bullet.vy / dist) * knockback
                        for wall in walls:
                            if zombie.get_rect().colliderect(wall.rect):
                                zombie.x, zombie.y = old_x, old_y
                                break
                    
                    zombie_cx = zombie.x + zombie.width // 2
                    zombie_cy = zombie.y + zombie.height // 2
                    particles.extend(spawn_particles(zombie_cx, zombie_cy, 8))
                    if zombie.take_damage():
                        particles.extend(spawn_particles(zombie_cx, zombie_cy, 25))
                        player.points += 1
                    break
        bullets = [b for b in bullets if b.alive]

        for bullet in bullets:
            for door in doors:
                if door.alive and door.rect.collidepoint(bullet.x, bullet.y):
                    bullet.alive = False
                    broken_doors = break_connected_doors(door, doors)
                    door_break_sound.play()
                    for broken_door in broken_doors:
                        door_cx = broken_door.rect.centerx
                        door_cy = broken_door.rect.centery
                        particles.extend(spawn_particles(door_cx, door_cy, 20, "gray"))
                    break
        bullets = [b for b in bullets if b.alive]

        if damage_cooldown > 0:
            damage_cooldown -= 1

        player_rect = player.get_rect()
        for zombie in zombies:
            if zombie.alive and player_rect.colliderect(zombie.get_rect()):
                if damage_cooldown == 0:
                    player.hp -= 1
                    damage_cooldown = 60
                    damage_sound.play()
                    growl_sound.play()
                    player_cx = player.x + player.width // 2
                    player_cy = player.y + player.height // 2
                    particles.extend(spawn_particles(player_cx, player_cy, 10))
                    if player.hp <= 0:
                        particles.extend(spawn_particles(player_cx, player_cy, 30))
                        player.hp = MAX_HP
                        player.ammo = 2
                        player.x = 50
                        player.y = SCREEN_HEIGHT - 100
                        player.points = 0
                        medkits, ammo_packs, exits, zombies, doors = create_pickups(current_map)
                        bullets = []
                break

        for medkit in medkits:
            if medkit.alive and player_rect.colliderect(medkit.rect):
                player.heal(1)
                medkit.alive = False
        for ammo_pack in ammo_packs:
            if ammo_pack.alive and player_rect.colliderect(ammo_pack.rect):
                player.add_ammo(3)
                ammo_pack.alive = False

        if player.points >= points_to_exit:
            for exit_tile in exits:
                if player_rect.colliderect(exit_tile.rect):
                    exit_sound.play()
                    level += 1
                    level_data = get_current_level_data(level)
                    current_map = level_data["map"]
                    points_to_exit = level_data["points_to_exit"]
                    player.x = 50
                    player.y = SCREEN_HEIGHT - 100
                    player.points = 0
                    player.ammo = 2
                    walls = create_walls(current_map)
                    medkits, ammo_packs, exits, zombies, doors = create_pickups(current_map)
                    bullets = []
                    break

        has_enough_points = player.points >= points_to_exit

        for particle in particles:
            particle.update()
        particles = [p for p in particles if p.lifetime > 0]

        draw_floor(screen)
        for exit_tile in exits:
            exit_tile.draw(screen, has_enough_points)
        for wall in walls:
            wall.draw(screen)
        for door in doors:
            door.draw(screen)
        for medkit in medkits:
            if medkit.alive:
                medkit.draw(screen)
        for ammo_pack in ammo_packs:
            if ammo_pack.alive:
                ammo_pack.draw(screen)
        for zombie in zombies:
            zombie.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for particle in particles:
            particle.draw(screen)
        player.draw(screen)
        draw_ui(screen, player, level, points_to_exit)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
