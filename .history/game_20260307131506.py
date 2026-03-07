import pygame
import sys
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLUE = (50, 100, 200)
GRAY_LIGHT = (80, 80, 80)
GRAY_DARK = (60, 60, 60)
WALL_COLOR = (40, 35, 30)
TILE_SIZE = 50
PLAYER_SPEED = 3

LEVEL_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WASD Movement Game")
clock = pygame.time.Clock()


def draw_floor(surface):
    for row in range(SCREEN_HEIGHT // TILE_SIZE + 1):
        for col in range(SCREEN_WIDTH // TILE_SIZE + 1):
            color = GRAY_LIGHT if (row + col) % 2 == 0 else GRAY_DARK
            pygame.draw.rect(surface, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))


class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, WALL_COLOR, self.rect)
        pygame.draw.rect(surface, (60, 55, 50), self.rect, 3)


def create_walls():
    walls = []
    for row_idx, row in enumerate(LEVEL_MAP):
        for col_idx, cell in enumerate(row):
            if cell == 1:
                walls.append(Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return walls


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 45
        self.height = 45
        self.speed = PLAYER_SPEED
        self.angle = 0
        
        self.original_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.original_surface, BLUE, (0, 0, self.width, self.height))
        pygame.draw.polygon(self.original_surface, (255, 100, 100), [
            (self.width, self.height // 2),
            (self.width - 12, 4),
            (self.width - 12, self.height - 4)
        ])

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def handle_input(self, keys, walls):
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


def main():
    player = Player(50, SCREEN_HEIGHT - 100)
    walls = create_walls()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys, walls)
        
        mouse_pos = pygame.mouse.get_pos()
        player.look_at_mouse(mouse_pos)

        draw_floor(screen)
        for wall in walls:
            wall.draw(screen)
        player.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
