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
BULLET_SPEED = 10
BULLET_COLOR = (255, 220, 50)
MAX_HP = 3
MEDKIT_COLOR = (255, 100, 100)
AMMO_COLOR = (100, 200, 100)

font = None

LEVEL_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 3, 1],
    [1, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
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


def create_walls():
    walls = []
    for row_idx, row in enumerate(LEVEL_MAP):
        for col_idx, cell in enumerate(row):
            if cell == 1:
                walls.append(Wall(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return walls


def create_pickups():
    medkits = []
    ammo_packs = []
    for row_idx, row in enumerate(LEVEL_MAP):
        for col_idx, cell in enumerate(row):
            if cell == 2:
                medkits.append(Medkit(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
            elif cell == 3:
                ammo_packs.append(AmmoPack(col_idx * TILE_SIZE, row_idx * TILE_SIZE))
    return medkits, ammo_packs


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
        self.ammo = 3
        
        self.original_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.original_surface, BLUE, (0, 0, self.width, self.height))
        pygame.draw.polygon(self.original_surface, (255, 100, 100), [
            (self.width, self.height // 2),
            (self.width - 12, 4),
            (self.width - 12, self.height - 4)
        ])

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            return Bullet(center_x, center_y, self.angle)
        return None

    def heal(self, amount):
        self.hp = min(self.hp + amount, MAX_HP)

    def add_ammo(self, amount):
        self.ammo += amount

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


def draw_ui(surface, player):
    global font
    if font is None:
        font = pygame.font.Font(None, 36)
    
    hp_text = font.render(f"HP: {player.hp}", True, (255, 80, 80))
    ammo_text = font.render(f"Ammo: {player.ammo}", True, (255, 220, 50))
    
    surface.blit(hp_text, (10, 10))
    surface.blit(ammo_text, (10, 45))


def main():
    player = Player(50, SCREEN_HEIGHT - 100)
    walls = create_walls()
    medkits, ammo_packs = create_pickups()
    bullets = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    if bullet:
                        bullets.append(bullet)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bullet = player.shoot()
                    if bullet:
                        bullets.append(bullet)

        keys = pygame.key.get_pressed()
        player.handle_input(keys, walls)
        
        mouse_pos = pygame.mouse.get_pos()
        player.look_at_mouse(mouse_pos)

        for bullet in bullets:
            bullet.update(walls)
        bullets = [b for b in bullets if b.alive]

        player_rect = player.get_rect()
        for medkit in medkits:
            if medkit.alive and player_rect.colliderect(medkit.rect):
                player.heal(1)
                medkit.alive = False
        for ammo_pack in ammo_packs:
            if ammo_pack.alive and player_rect.colliderect(ammo_pack.rect):
                player.add_ammo(3)
                ammo_pack.alive = False

        draw_floor(screen)
        for wall in walls:
            wall.draw(screen)
        for medkit in medkits:
            if medkit.alive:
                medkit.draw(screen)
        for ammo_pack in ammo_packs:
            if ammo_pack.alive:
                ammo_pack.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        player.draw(screen)
        draw_ui(screen, player)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
