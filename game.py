import pygame
import sys
import math
import random
import struct
import wave
import os
from collections import deque


def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

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


def generate_menu_music(filename):
    if os.path.exists(filename):
        return
    sample_rate = 22050
    duration = 16.0
    num_samples = int(sample_rate * duration)
    
    samples = []
    base_freqs = [55, 51.91, 49, 46.25]
    
    for i in range(num_samples):
        t = i / sample_rate
        section = int(t / 4.0) % 4
        freq = base_freqs[section]
        
        value = 0
        value += 0.2 * math.sin(2 * math.pi * freq * t)
        value += 0.1 * math.sin(2 * math.pi * freq * 2 * t) * math.sin(t * 0.1)
        
        square = 1 if math.sin(2 * math.pi * freq * 0.25 * t) > 0 else -1
        value += 0.08 * square
        
        drone = math.sin(2 * math.pi * 30 * t + math.sin(t * 0.3) * 2)
        value += 0.12 * drone
        
        beat_pos = (t * 0.8) % 1
        if beat_pos < 0.15:
            beat_env = 1 - (beat_pos / 0.15)
            beat_square = 1 if math.sin(2 * math.pi * 60 * t) > 0 else -1
            value += 0.15 * beat_square * beat_env
        
        value += 0.04 * random.uniform(-1, 1)
        
        pulse = 0.7 + 0.3 * math.sin(2 * math.pi * 0.1 * t)
        value *= pulse * 0.35
        
        value = int(value * 32767)
        samples.append(struct.pack('<h', max(-32768, min(32767, value))))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(samples))


generate_sound(get_resource_path("shoot.wav"), 800, 0.1, 0.05, "square")
generate_sound(get_resource_path("damage.wav"), 200, 0.15, 0.4, "sawtooth")
generate_sound(get_resource_path("growl.wav"), 80, 0.3, 0.5, "sawtooth")
generate_sound(get_resource_path("door_break.wav"), 80, 0.35, 0.7, "noise")
generate_sound(get_resource_path("exit.wav"), 600, 0.25, 0.4, "sine")
generate_sound(get_resource_path("pickup.wav"), 1000, 0.1, 0.25, "sine")
generate_music(get_resource_path("music.wav"))
generate_menu_music(get_resource_path("menu_music.wav"))

shoot_sound = pygame.mixer.Sound(get_resource_path("shoot.wav"))
damage_sound = pygame.mixer.Sound(get_resource_path("damage.wav"))
growl_sound = pygame.mixer.Sound(get_resource_path("growl.wav"))
pickup_sound = pygame.mixer.Sound(get_resource_path("pickup.wav"))
door_break_sound = pygame.mixer.Sound(get_resource_path("door_break.wav"))
exit_sound = pygame.mixer.Sound(get_resource_path("exit.wav"))


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLUE = (50, 100, 200)
GRAY_LIGHT = (60, 60, 80)
GRAY_DARK = (50, 50, 70)
WALL_COLOR = (40, 35, 30)
TILE_SIZE = 50
PLAYER_SPEED = 3
BULLET_SPEED = 18
BULLET_COLOR = (255, 220, 50)
MAX_HP = 3
MEDKIT_COLOR = (255, 100, 100)
AMMO_COLOR = (220, 200, 60)
EXIT_COLOR = (100, 200, 255)
ZOMBIE_COLOR = (100, 150, 80)
ZOMBIE_SPEED = 0.7
ZOMBIE_HP = 2
ZOMBIE_SIZE = 40
FLASHLIGHT_RADIUS = 350
FLASHLIGHT_CONE_ANGLE = 45

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
            [1, 0, 0, 1.1, 1.1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1.1, 1.1, 1, 0, 0, 0, 1, 0, 5, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 3, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 6, 6, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1.2, 1.2, 0, 0, 6, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 5, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1.2, 1.2, 0, 0, 1.2, 1.2, 0, 0, 1.2, 1.2, 0, 1, 0, 0, 3, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
    {
        "points_to_exit": 5,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 3, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 5, 0, 1.2, 1.2, 0, 0, 6, 0, 0, 1, 6, 6, 1, 0, 0, 0, 0, 0, 1.1, 5, 0, 1.1, 1],
            [1, 0, 0, 1.2, 1.2, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1.1, 0, 0, 1.1, 1],
            [1, 0, 0, 1.2, 1.2, 0, 0, 1, 0, 0, 1, 0, 5, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1.2, 1.2, 0, 0, 1, 0, 0, 1, 2, 3, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1.2, 1.2, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1.1, 1.1, 0, 0, 1],
            [1, 0, 0, 5, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 6, 6, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1.1, 1.1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1.1, 1.1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.1, 1.1, 1.1, 1.1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1.2, 1.2, 0, 0, 0, 0, 0, 0, 0, 0, 1.1, 1.1, 1.1, 1.1, 3, 0, 0, 0, 4, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
    {
        "points_to_exit": 7,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 6, 0, 0, 1.2, 1, 3, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 3, 1, 1],
            [1, 0, 5, 6, 0, 0, 1.2, 1, 0, 0, 1, 0, 0, 1, 0, 5, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 6, 0, 0, 1.2, 1, 0, 0, 1, 0, 0, 1, 6.1, 6.1, 1, 6,1, 6,1, 1, 0, 0, 1, 1],
            [1, 5, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 3, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 6.1, 3, 0, 0, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 6.1, 5, 0, 0, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1.2, 1, 0, 0, 1, 6.1, 6.1, 1, 6.1, 6.1, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 1, 0, 0, 1.2, 1, 0, 5, 1, 0, 0, 1, 5, 0, 1, 0, 0, 1, 0, 5, 1, 1],
            [1, 0, 0, 1, 4, 0, 1.2, 1, 0, 0, 1, 0, 0, 1, 2, 3, 1, 0, 0, 1, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
    {
        "points_to_exit": 1,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 0, 0, 6.1, 0, 0, 6.1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 5, 0, 6.1, 5, 0, 6.1, 0, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 2, 1, 1.2, 1.2, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1.2, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1.2, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1.2, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 1.2, 1.2, 1.2, 1.2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1, 0, 0, 1.2, 1.2, 1.2, 1.2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 4, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 1.2, 1.2, 1.2, 1.2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 6],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.2, 1.2, 1.2, 1.2, 1.2, 1, 0, 0, 6],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.3, 1, 1],
        ]
    },
    {
        "points_to_exit": 0,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
    {
        "points_to_exit": 0,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
    {
        "points_to_exit": 0,
        "map": [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    },
]

def get_current_level_data(level):
    idx = min(level - 1, len(LEVEL_DATA) - 1)
    return LEVEL_DATA[idx]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Evil Residents")
clock = pygame.time.Clock()


def draw_floor(surface):
    for row in range(SCREEN_HEIGHT // TILE_SIZE + 1):
        for col in range(SCREEN_WIDTH // TILE_SIZE + 1):
            color = GRAY_LIGHT if (row + col) % 2 == 0 else GRAY_DARK
            pygame.draw.rect(surface, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def draw_flashlight(surface, player, exits=None, has_enough_points=False, bullets=None, alarm_tiles=None):
    darkness = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    darkness.fill((0, 0, 0, 220))
    
    player_cx = int(player.x + player.width // 2)
    player_cy = int(player.y + player.height // 2)
    
    angle_rad = math.radians(-player.angle)
    
    cone_points = [(player_cx, player_cy)]
    num_points = 20
    half_angle = math.radians(FLASHLIGHT_CONE_ANGLE)
    
    for i in range(num_points + 1):
        point_angle = angle_rad - half_angle + (2 * half_angle * i / num_points)
        px = player_cx + math.cos(point_angle) * FLASHLIGHT_RADIUS
        py = player_cy + math.sin(point_angle) * FLASHLIGHT_RADIUS
        cone_points.append((int(px), int(py)))
    
    pygame.draw.polygon(darkness, (0, 0, 0, 0), cone_points)
    pygame.draw.circle(darkness, (0, 0, 0, 0), (player_cx, player_cy), 60)
    
    if exits and has_enough_points:
        for exit_tile in exits:
            exit_cx = exit_tile.rect.centerx
            exit_cy = exit_tile.rect.centery
            pygame.draw.circle(darkness, (0, 0, 0, 0), (exit_cx, exit_cy), 100)
    
    if bullets:
        for bullet in bullets:
            if bullet.alive:
                pygame.draw.circle(darkness, (0, 0, 0, 0), (int(bullet.x), int(bullet.y)), 40)
    
    if alarm_tiles:
        for alarm in alarm_tiles:
            if alarm.active:
                alarm_cx = alarm.rect.centerx
                alarm_cy = alarm.rect.centery
                pygame.draw.circle(darkness, (0, 0, 0, 0), (alarm_cx, alarm_cy), 120)
    
    surface.blit(darkness, (0, 0))
    
    if exits and has_enough_points:
        for exit_tile in exits:
            exit_cx = exit_tile.rect.centerx
            exit_cy = exit_tile.rect.centery
            glow_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (80, 20, 20, 40), (100, 100), 100)
            pygame.draw.circle(glow_surface, (100, 30, 30, 60), (100, 100), 70)
            pygame.draw.circle(glow_surface, (120, 40, 40, 80), (100, 100), 40)
            surface.blit(glow_surface, (exit_cx - 100, exit_cy - 100))
    
    if bullets:
        for bullet in bullets:
            if bullet.alive:
                glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 240, 150, 50), (30, 30), 30)
                pygame.draw.circle(glow_surface, (255, 250, 180, 80), (30, 30), 18)
                surface.blit(glow_surface, (int(bullet.x) - 30, int(bullet.y) - 30))
    
    if alarm_tiles:
        for alarm in alarm_tiles:
            if alarm.active:
                alarm_cx = alarm.rect.centerx
                alarm_cy = alarm.rect.centery
                glow_surface = pygame.Surface((240, 240), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (150, 20, 20, 30), (120, 120), 120)
                pygame.draw.circle(glow_surface, (180, 30, 30, 50), (120, 120), 80)
                pygame.draw.circle(glow_surface, (200, 40, 40, 70), (120, 120), 40)
                surface.blit(glow_surface, (alarm_cx - 120, alarm_cy - 120))


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


class Footprint:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.alpha = 180
        self.size = random.randint(6, 9)
        self.offset_x = random.randint(-3, 3)
        self.offset_y = random.randint(-3, 3)

    def update(self):
        self.alpha -= 0.5
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            foot_surface = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            color = (120, 20, 20, int(self.alpha))
            cx, cy = self.size * 1.5, self.size * 1.5
            pygame.draw.ellipse(foot_surface, color, (cx - self.size // 2 - 4, cy - self.size * 0.75, self.size, int(self.size * 1.5)))
            pygame.draw.ellipse(foot_surface, color, (cx - self.size // 2 + 4, cy - self.size * 0.75, self.size, int(self.size * 1.5)))
            rotated = pygame.transform.rotate(foot_surface, self.angle + 90)
            rect = rotated.get_rect(center=(self.x + self.offset_x, self.y + self.offset_y))
            surface.blit(rotated, rect.topleft)


class DustParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.2, 0.2)
        self.size = random.uniform(1.5, 3.5)
        self.alpha = random.randint(80, 150)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0

    def draw(self, surface):
        dust_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(dust_surface, (200, 180, 150, self.alpha), (int(self.size), int(self.size)), int(self.size))
        surface.blit(dust_surface, (int(self.x - self.size), int(self.y - self.size)))


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


class CleanMetal:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, (80, 85, 90), self.rect)


class AlarmTile:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.phase_timer = 0
        self.phase_duration = 42
        self.active = False
    
    def update(self):
        self.phase_timer += 1
        if self.phase_timer >= self.phase_duration:
            self.phase_timer = 0
            self.active = not self.active
    
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
        
        center = (self.rect.centerx, self.rect.centery)
        if self.active:
            pygame.draw.circle(surface, (200, 30, 30), center, 10)
            pygame.draw.circle(surface, (255, 80, 80), center, 6)
        else:
            pygame.draw.circle(surface, (20, 20, 20), center, 10)
            pygame.draw.circle(surface, (40, 40, 40), center, 6)


class MetalLocker:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        base_color = (90, 100, 110)
        pygame.draw.rect(surface, base_color, self.rect)
        door_color = (100, 110, 120)
        door_rect = pygame.Rect(self.rect.left + 4, self.rect.top + 4, self.rect.width - 8, self.rect.height - 8)
        pygame.draw.rect(surface, door_color, door_rect)
        vent_color = (60, 65, 75)
        vent_y_start = self.rect.top + 10
        for i in range(4):
            vent_y = vent_y_start + i * 6
            pygame.draw.line(surface, vent_color, (self.rect.left + 10, vent_y), (self.rect.right - 10, vent_y), 2)
        handle_color = (70, 75, 85)
        handle_rect = pygame.Rect(self.rect.right - 14, self.rect.centery - 8, 6, 16)
        pygame.draw.rect(surface, handle_color, handle_rect)
        pygame.draw.rect(surface, (75, 80, 90), door_rect, 2)
        pygame.draw.rect(surface, (70, 75, 85), self.rect, 2)


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


class PrisonBars:
    def __init__(self, x, y, row, col):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.row = row
        self.col = col
        self.alive = True

    def draw(self, surface):
        if not self.alive:
            return
        bar_color = (50, 55, 60)
        bar_highlight = (80, 85, 95)
        frame_color = (40, 45, 50)
        pygame.draw.rect(surface, frame_color, (self.rect.left, self.rect.top, self.rect.width, 6))
        pygame.draw.rect(surface, frame_color, (self.rect.left, self.rect.bottom - 6, self.rect.width, 6))
        num_bars = 5
        bar_width = 6
        spacing = (self.rect.width - num_bars * bar_width) // (num_bars + 1)
        for i in range(num_bars):
            bar_x = self.rect.left + spacing + i * (bar_width + spacing)
            pygame.draw.rect(surface, bar_color, (bar_x, self.rect.top + 6, bar_width, self.rect.height - 12))
            pygame.draw.line(surface, bar_highlight, (bar_x + 1, self.rect.top + 6), (bar_x + 1, self.rect.bottom - 6), 1)


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
                cell_value = level_map[new_row][new_col]
                is_wall = cell_value == 1 or cell_value == 1.1 or cell_value == 1.2 or cell_value == 1.3
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
        self.footprint_timer = 0
        
        zombie_img = pygame.image.load(get_resource_path("zombie.png")).convert_alpha()
        self.original_surface = pygame.transform.scale(zombie_img, (self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, player, walls, level_map, doors):
        if not self.alive:
            return None

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
        
        footprint = None
        self.footprint_timer += 1
        if self.footprint_timer >= 30:
            self.footprint_timer = 0
            footprint = Footprint(zombie_cx, zombie_cy + self.height // 3, self.angle)
        
        return footprint

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
    alarm_tiles = []
    for row_idx, row in enumerate(level_map):
        for col_idx, cell in enumerate(row):
            if cell == 1:
                walls.append(Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif cell == 1.1:
                walls.append(CleanMetal(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif cell == 1.2:
                walls.append(MetalLocker(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif cell == 1.3:
                alarm = AlarmTile(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                walls.append(alarm)
                alarm_tiles.append(alarm)
    return walls, alarm_tiles


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
            elif cell == 6.1:
                doors.append(PrisonBars(col_idx * TILE_SIZE, row_idx * TILE_SIZE, row_idx, col_idx))
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
        
        player_img = pygame.image.load(get_resource_path("player.png")).convert_alpha()
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


class MenuZombie:
    def __init__(self):
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = random.randint(100, SCREEN_HEIGHT - 100)
        self.size = 50
        self.speed = 1.5
        self.angle = 0
        zombie_img = pygame.image.load(get_resource_path("zombie.png")).convert_alpha()
        self.surface = pygame.transform.scale(zombie_img, (self.size, self.size))
    
    def update(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 5:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        
        self.angle = -math.degrees(math.atan2(dy, dx))
    
    def draw(self, surface):
        rotated = pygame.transform.rotate(self.surface, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect.topleft)


def draw_menu(surface, selected_option, menu_zombie=None):
    surface.fill((20, 20, 25))
    
    if menu_zombie:
        menu_zombie.draw(surface)

    title_font = pygame.font.Font(None, 80)
    menu_font = pygame.font.Font(None, 50)

    title_text = title_font.render("Evil Residents", True, (200, 50, 50))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
    surface.blit(title_text, title_rect)

    subtitle_font = pygame.font.Font(None, 30)
    subtitle_text = subtitle_font.render("Survive the outbreak", True, (150, 150, 150))
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
    surface.blit(subtitle_text, subtitle_rect)

    menu_options = ["Start Game", "Quit"]
    for i, option in enumerate(menu_options):
        if i == selected_option:
            color = (255, 100, 100)
            prefix = "> "
            suffix = " <"
        else:
            color = (180, 180, 180)
            prefix = ""
            suffix = ""

        option_text = menu_font.render(f"{prefix}{option}{suffix}", True, color)
        option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, 400 + i * 60))
        surface.blit(option_text, option_rect)

    controls_font = pygame.font.Font(None, 24)
    controls = ["WASD - Move", "Mouse - Aim", "Left Click / Space - Shoot", "R - Restart Level", "ESC - Quit"]
    for i, control in enumerate(controls):
        control_text = controls_font.render(control, True, (100, 100, 100))
        control_rect = control_text.get_rect(center=(SCREEN_WIDTH // 2, 550 + i * 25))
        surface.blit(control_text, control_rect)


def show_menu(screen, clock):
    pygame.mixer.music.load(get_resource_path("menu_music.wav"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    
    menu_zombie = MenuZombie()
    selected_option = 0
    num_options = 2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % num_options
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % num_options
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected_option == 0:
                        return "start"
                    elif selected_option == 1:
                        return "quit"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"

        mouse_pos = pygame.mouse.get_pos()
        menu_zombie.update(mouse_pos)
        
        draw_menu(screen, selected_option, menu_zombie)
        pygame.display.flip()
        clock.tick(FPS)


def show_intro_cutscene(screen, clock):
    story_lines = [
        "This was supposed to be my first day as a police officer...",
        "Only for me to find out that the city has fallen.",
        "The police station is overrun with the infected.",
        "Maybe there are still some survivors...",
        "I'll have to try and find them.",
        "And if there's none...",
        "I'll have to make my own way out.",
    ]
    
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 28)
    
    char_delay = 50
    line_delay = 800
    
    displayed_text = []
    current_line = 0
    current_char = 0
    last_char_time = pygame.time.get_ticks()
    last_line_time = pygame.time.get_ticks()
    waiting_for_line = False
    
    fade_alpha = 255
    fade_in = True
    
    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "skip"
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return "skip"
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "skip"
        
        if fade_in:
            fade_alpha -= 5
            if fade_alpha <= 0:
                fade_alpha = 0
                fade_in = False
        
        if not fade_in and current_line < len(story_lines):
            if waiting_for_line:
                if current_time - last_line_time >= line_delay:
                    waiting_for_line = False
                    current_line += 1
                    current_char = 0
                    if current_line < len(story_lines):
                        displayed_text.append("")
            else:
                if current_line < len(story_lines):
                    line = story_lines[current_line]
                    if current_char < len(line):
                        if current_time - last_char_time >= char_delay:
                            if len(displayed_text) <= current_line:
                                displayed_text.append("")
                            displayed_text[current_line] += line[current_char]
                            current_char += 1
                            last_char_time = current_time
                    else:
                        waiting_for_line = True
                        last_line_time = current_time
        
        if current_line >= len(story_lines) and not waiting_for_line:
            pygame.time.wait(1500)
            return "done"
        
        screen.fill((10, 10, 15))
        
        y_offset = 200
        for i, line in enumerate(displayed_text):
            if line:
                text_surface = font.render(line, True, (180, 180, 180))
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 45))
                screen.blit(text_surface, text_rect)
            else:
                y_offset -= 20
        
        skip_text = small_font.render("Press SPACE to skip", True, (80, 80, 80))
        skip_rect = skip_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(skip_text, skip_rect)
        
        if fade_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()
        clock.tick(FPS)


def main():
    menu_result = show_menu(screen, clock)
    if menu_result == "quit":
        pygame.quit()
        sys.exit()
    
    cutscene_result = show_intro_cutscene(screen, clock)
    if cutscene_result == "quit":
        pygame.quit()
        sys.exit()

    pygame.mixer.music.load(get_resource_path("music.wav"))
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1)

    level = 1
    level_data = get_current_level_data(level)
    current_map = level_data["map"]
    points_to_exit = level_data["points_to_exit"]
    
    player = Player(50, SCREEN_HEIGHT - 100)
    walls, alarm_tiles = create_walls(current_map)
    medkits, ammo_packs, exits, zombies, doors = create_pickups(current_map)
    bullets = []
    particles = []
    footprints = []
    dust_particles = [DustParticle() for _ in range(100)]
    damage_cooldown = 0
    skip_level_cooldown = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    player.hp = MAX_HP
                    player.ammo = 2
                    player.x = 50
                    player.y = SCREEN_HEIGHT - 100
                    player.points = 0
                    walls, alarm_tiles = create_walls(current_map)
                    medkits, ammo_packs, exits, zombies, doors = create_pickups(current_map)
                    bullets = []
                    particles = []
                    footprints = []
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
        
        if skip_level_cooldown > 0:
            skip_level_cooldown -= 1
        
        if keys[pygame.K_l] and keys[pygame.K_k] and skip_level_cooldown == 0 and level < len(LEVEL_DATA):
            skip_level_cooldown = 60
            level += 1
            level_data = get_current_level_data(level)
            current_map = level_data["map"]
            points_to_exit = level_data["points_to_exit"]
            player.x = 50
            player.y = SCREEN_HEIGHT - 100
            player.points = 0
            player.ammo = 2
            walls, alarm_tiles = create_walls(current_map)
            medkits, ammo_packs, exits, zombies, doors = create_pickups(current_map)
            bullets = []
            particles = []
            footprints = []
        
        mouse_pos = pygame.mouse.get_pos()
        player.look_at_mouse(mouse_pos)

        for zombie in zombies:
            footprint = zombie.update(player, walls, current_map, doors)
            if footprint:
                footprints.append(footprint)

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
                pickup_sound.play()
        for ammo_pack in ammo_packs:
            if ammo_pack.alive and player_rect.colliderect(ammo_pack.rect):
                player.add_ammo(3)
                ammo_pack.alive = False
                pickup_sound.play()

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
                    walls, alarm_tiles = create_walls(current_map)
                    medkits, ammo_packs, exits, zombies, doors = create_pickups(current_map)
                    bullets = []
                    break

        has_enough_points = player.points >= points_to_exit

        for particle in particles:
            particle.update()
        particles = [p for p in particles if p.lifetime > 0]
        
        footprints = [f for f in footprints if f.update()]
        
        for dust in dust_particles:
            dust.update()

        draw_floor(screen)
        for footprint in footprints:
            footprint.draw(screen)
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
        for dust in dust_particles:
            dust.draw(screen)
        for alarm in alarm_tiles:
            alarm.update()
        draw_flashlight(screen, player, exits, has_enough_points, bullets, alarm_tiles)
        draw_ui(screen, player, level, points_to_exit)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
