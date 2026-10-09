import pygame
import random
import math
from PIL import Image, ImageDraw

# Pygame ve Font Başlatma
pygame.init()
pygame.font.init()

# Ekran Ayarları
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("XS TEAM - Anime Battle Engine")

CLOCK = pygame.time.Clock()
FPS = 60

# Renkler
BLACK = (15, 15, 20)
WHITE = (255, 255, 255)
YELLOW_BG = (245, 220, 90)
DARK_YELLOW = (210, 180, 40)
RED = (230, 50, 50)
GREEN = (50, 205, 50)
BLUE = (30, 144, 255)
PURPLE = (147, 112, 219)
GRAY = (70, 70, 80)
LIGHT_GRAY = (200, 200, 200)

# Karakter Renkleri
MIKU_COLOR = (57, 197, 187)
NERU_COLOR = (255, 223, 0)
TETO_COLOR = (255, 43, 80)
MITA_COLOR = (186, 85, 211)

FONT = pygame.font.SysFont("Arial", 18, bold=True)
BIG_FONT = pygame.font.SysFont("Arial", 32, bold=True)
TITLE_FONT = pygame.font.SysFont("Arial", 54, bold=True)

def generate_anime_avatar(name, base_color):
    img = Image.new("RGBA", (100, 100), (30, 30, 40, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 90, 90], fill=base_color)
    draw.ellipse([25, 20, 75, 70], fill=(255, 230, 210))
    draw.polygon([(20, 20), (50, 5), (80, 20), (50, 45)], fill=base_color)
    draw.ellipse([35, 40, 43, 50], fill=(20, 20, 20))
    draw.ellipse([57, 40, 65, 50], fill=(20, 20, 20))
    draw.ellipse([30, 52, 40, 58], fill=(255, 150, 150))
    draw.ellipse([60, 52, 70, 58], fill=(255, 150, 150))
    
    mode = img.mode
    size = img.size
    data = img.tobytes()
    return pygame.image.fromstring(data, size, mode)

CHARACTERS = {
    "Miku": {"color": MIKU_COLOR, "speed": 7, "hp": 4, "desc": "Hızlı & Denge", "img": generate_anime_avatar("Miku", MIKU_COLOR)},
    "Neru": {"color": NERU_COLOR, "speed": 8, "hp": 3, "desc": "Çok Hızlı", "img": generate_anime_avatar("Neru", NERU_COLOR)},
    "Teto": {"color": TETO_COLOR, "speed": 5, "hp": 5, "desc": "Yüksek Can", "img": generate_anime_avatar("Teto", TETO_COLOR)},
    "Mita": {"color": MITA_COLOR, "speed": 6, "hp": 4, "desc": "MiSide Gücü", "img": generate_anime_avatar("Mita", MITA_COLOR)}
}

users_db = {
    "AyazXS": "ayaz201689."
}

class InputBox:
    def __init__(self, x, y, w, h, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN and len(self.text) < 18:
                self.text += event.unicode

    def draw(self, surface):
        color = BLACK if self.active else GRAY
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=6)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=6)
        
        display_text = "*" * len(self.text) if self.is_password else self.text
        if not self.text and not self.active:
            txt_surface = FONT.render(self.placeholder, True, GRAY)
        else:
            txt_surface = FONT.render(display_text, True, BLACK)
            
        surface.blit(txt_surface, (self.rect.x + 10, self.rect.y + 12))

class Button:
    def __init__(self, x, y, w, h, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=8)
        txt = FONT.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Player:
    def __init__(self, char_name):
        data = CHARACTERS[char_name]
        self.name = char_name
        self.x = 120
        self.y = HEIGHT // 2
        self.speed = data["speed"]
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.color = data["color"]
        self.img = data["img"]
        self.score = 0
        self.ultimate_charge = 0
        self.shoot_cooldown = 0

    def move(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed

        self.x = max(40, min(WIDTH // 2 - 60, self.x))
        self.y = max(40, min(HEIGHT - 40, self.y))

    def draw(self, surface):
        surface.blit(self.img, (self.x - 50, self.y - 50))
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 4)
        name_txt = FONT.render(self.name, True, WHITE)
        surface.blit(name_txt, (self.x - 20, self.y - 70))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 80
        self.max_hp = 80
        self.shoot_timer = 0
        self.dir = 1

    def update(self):
        self.shoot_timer += 1
        self.y += 2 * self.dir
        if self.y < 80 or self.y > HEIGHT - 80:
            self.dir *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), 40)
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 22)
        pygame.draw.rect(surface, RED, (self.x - 40, self.y - 60, 80, 8))
        pygame.draw.rect(surface, GREEN, (self.x - 40, self.y - 60, max(0, int(80 * (self.hp / self.max_hp))), 8))

class Bullet:
    def __init__(self, x, y, dx, dy, color, radius=6):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.radius = radius

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

GAME_STATE = 'AUTH_MAIN'
current_user = ""
status_message = ""

txt_user = InputBox(WIDTH // 2 - 120, 230, 240, 45, "Kullanıcı Adı")
txt_pass = InputBox(WIDTH // 2 - 120, 290, 240, 45, "Şifre", is_password=True)

btn_goto_login = Button(WIDTH // 2 - 120, 260, 240, 50, "GİRİŞ YAP", BLACK)
btn_goto_reg = Button(WIDTH // 2 - 120, 330, 240, 50, "KAYIT OL", DARK_YELLOW, BLACK)

btn_submit_login = Button(WIDTH // 2 - 120, 350, 240, 45, "Girişi Onayla", GREEN)
btn_admin_login = Button(WIDTH // 2 - 120, 405, 240, 45, "ADMIN GİRİŞİ", BLUE)
btn_submit_reg = Button(WIDTH // 2 - 120, 350, 240, 45, "Kayıt Ol ve Başla", GREEN)
btn_back = Button(20, 20, 100, 35, "< Geri", BLACK)

char_buttons = []
cx = 60
for name in CHARACTERS:
    char_buttons.append((Button(cx, 360, 170, 50, f"Seç: {name}", CHARACTERS[name]["color"], BLACK), name))
    cx += 200

player = None
enemy = None
player_bullets = []
enemy_bullets = []

running = True

while running:
    CLOCK.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        txt_user.handle_event(event)
        txt_pass.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if GAME_STATE == 'AUTH_MAIN':
                if btn_goto_login.is_clicked(mouse_pos):
                    GAME_STATE = 'LOGIN'
                    status_message = ""
                elif btn_goto_reg.is_clicked(mouse_pos):
                    GAME_STATE = 'REGISTER'
                    status_message = ""

            elif GAME_STATE in ['LOGIN', 'REGISTER']:
                if btn_back.is_clicked(mouse_pos):
                    GAME_STATE = 'AUTH_MAIN'
                elif GAME_STATE == 'LOGIN' and btn_submit_login.is_clicked(mouse_pos):
                    u = txt_user.text.strip()
                    p = txt_pass.text.strip()
                    if u in users_db and users_db[u] == p:
                        current_user = u
                        GAME_STATE = 'CHAR_SELECT'
                    else:
                        status_message = "Hatalı Kullanıcı Adı veya Şifre!"
                elif GAME_STATE == 'LOGIN' and btn_admin_login.is_clicked(mouse_pos):
                    current_user = "AyazXS"
                    GAME_STATE = 'CHAR_SELECT'
                elif GAME_STATE == 'REGISTER' and btn_submit_reg.is_clicked(mouse_pos):
                    u = txt_user.text.strip()
                    p = txt_pass.text.strip()
                    if not u or not p:
                        status_message = "Kullanıcı adı ve şifre boş olamaz!"
                    elif u in users_db:
                        status_message = "Bu kullanıcı adı zaten alınmış!"
                    else:
                        users_db[u] = p
                        current_user = u
                        GAME_STATE = 'CHAR_SELECT'

            elif GAME_STATE == 'CHAR_SELECT':
                for btn, name in char_buttons:
                    if btn.is_clicked(mouse_pos):
                        player = Player(name)
                        enemy = Enemy(WIDTH - 120, HEIGHT // 2)
                        player_bullets.clear()
                        enemy_bullets.clear()
                        GAME_STATE = 'GAME'

        if event.type == pygame.KEYDOWN and GAME_STATE == 'GAME':
            if event.key == pygame.K_SPACE and player.ultimate_charge >= 100:
                enemy_bullets.clear()
                enemy.hp -= 20
                player.ultimate_charge = 0

    if GAME_STATE in ['AUTH_MAIN', 'LOGIN', 'REGISTER']:
        screen.fill(YELLOW_BG)
        title_txt = TITLE_FONT.render("XS TEAM", True, BLACK)
        screen.blit(title_txt, title_txt.get_rect(center=(WIDTH // 2, 120)))

        if GAME_STATE == 'AUTH_MAIN':
            btn_goto_login.draw(screen)
            btn_goto_reg.draw(screen)
        elif GAME_STATE == 'LOGIN':
            btn_back.draw(screen)
            sub_title = BIG_FONT.render("KULLANICI GİRİŞİ", True, BLACK)
            screen.blit(sub_title, sub_title.get_rect(center=(WIDTH // 2, 180)))
            txt_user.draw(screen)
            txt_pass.draw(screen)
            btn_submit_login.draw(screen)
            btn_admin_login.draw(screen)
        elif GAME_STATE == 'REGISTER':
            btn_back.draw(screen)
            sub_title = BIG_FONT.render("YENİ KAYIT OL", True, BLACK)
            screen.blit(sub_title, sub_title.get_rect(center=(WIDTH // 2, 180)))
            txt_user.draw(screen)
            txt_pass.draw(screen)
            btn_submit_reg.draw(screen)

        if status_message:
            msg_txt = FONT.render(status_message, True, RED)
            screen.blit(msg_txt, msg_txt.get_rect(center=(WIDTH // 2, 470)))

    elif GAME_STATE == 'CHAR_SELECT':
        screen.fill(BLACK)
        welcome_txt = FONT.render(f"Oyuncu: {current_user}", True, MIKU_COLOR)
        screen.blit(welcome_txt, (20, 20))
        select_title = BIG_FONT.render("KARAKTERİNİ SEÇ", True, WHITE)
        screen.blit(select_title, select_title.get_rect(center=(WIDTH // 2, 80)))

        cx = 60
        for name in CHARACTERS:
            data = CHARACTERS[name]
            pygame.draw.rect(screen, GRAY, (cx, 160, 170, 180), border_radius=10)
            pygame.draw.rect(screen, data["color"], (cx, 160, 170, 180), width=3, border_radius=10)
            screen.blit(data["img"], (cx + 35, 180))
            n_txt = FONT.render(name, True, WHITE)
            d_txt = FONT.render(data["desc"], True, LIGHT_GRAY)
            screen.blit(n_txt, (cx + 10, 290))
            screen.blit(d_txt, (cx + 10, 315))
            cx += 200

        for btn, name in char_buttons:
            btn.draw(screen)

    elif GAME_STATE in ['GAME', 'GAME_OVER']:
        screen.fill(BLACK)

        if GAME_STATE == 'GAME':
            keys = pygame.key.get_pressed()
            player.move(keys)

            if player.shoot_cooldown <= 0:
                player_bullets.append(Bullet(player.x + 20, player.y, 12, 0, player.color, 5))
                player.shoot_cooldown = 8
            else:
                player.shoot_cooldown -= 1

            enemy.update()
            if enemy.shoot_timer % 25 == 0:
                for angle in [-0.3, -0.15, 0, 0.15, 0.3]:
                    dx = -math.cos(angle) * 6
                    dy = math.sin(angle) * 6
                    enemy_bullets.append(Bullet(enemy.x - 30, enemy.y, dx, dy, RED, 6))

            for pb in player_bullets[:]:
                pb.update()
                if math.hypot(pb.x - enemy.x, pb.y - enemy.y) < 40:
                    enemy.hp -= 1
                    player.score += 100
                    player.ultimate_charge = min(100, player.ultimate_charge + 3)
                    if pb in player_bullets:
                        player_bullets.remove(pb)
                elif pb.x > WIDTH:
                    player_bullets.remove(pb)

            for eb in enemy_bullets[:]:
                eb.update()
                if math.hypot(eb.x - player.x, eb.y - player.y) < 20:
                    player.hp -= 1
                    if eb in enemy_bullets:
                        enemy_bullets.remove(eb)
                    if player.hp <= 0:
                        GAME_STATE = 'GAME_OVER'
                elif eb.x < 0 or eb.y < 0 or eb.y > HEIGHT:
                    if eb in enemy_bullets:
                        enemy_bullets.remove(eb)

            if enemy.hp <= 0:
                enemy.max_hp += 20
                enemy.hp = enemy.max_hp

        player.draw(screen)
        enemy.draw(screen)

        for pb in player_bullets:
            pb.draw(screen)
        for eb in enemy_bullets:
            eb.draw(screen)

        hp_txt = FONT.render(f"CAN: {player.hp}/{player.max_hp}", True, RED)
        score_txt = FONT.render(f"SKOR: {player.score}", True, WHITE)
        ult_txt = FONT.render(f"ULTİ (SPACE): {player.ultimate_charge}%", True, NERU_COLOR if player.ultimate_charge == 100 else WHITE)

        screen.blit(hp_txt, (20, 20))
        screen.blit(score_txt, (20, 45))
        screen.blit(ult_txt, (20, 70))

        if GAME_STATE == 'GAME_OVER':
            go_txt = BIG_FONT.render("GAME OVER", True, RED)
            screen.blit(go_txt, go_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

pygame.quit()
