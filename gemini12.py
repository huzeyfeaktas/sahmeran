import pgzrun
from pygame import Rect
from random import randint
import time

WIDTH = 1500
HEIGHT = 850
game_started = False
game_over = False
sound_on = True
score = 0
BACKGROUND_COLOR = (30, 30, 30)
GRAVITY = 0.5
PLAYER_HEIGHT = 128
ENEMY_HEIGHT = 128

platforms = [
    Rect(0, HEIGHT - 50, WIDTH, 50),  # Zemin
    Rect(200, HEIGHT - 150, 100, 20),
    Rect(500, HEIGHT - 250, 100, 20),
    Rect(800, HEIGHT - 100, 100, 20),
    Rect(1100, HEIGHT - 300, 100, 20),
    Rect(100, HEIGHT - 400, 100, 20),
    Rect(650, HEIGHT - 500, 100, 20),
    Rect(1200, HEIGHT - 600, 100, 20),
    Rect(350, HEIGHT - 700, 100, 20)
]

class Player:
    def __init__(self):
        self.pos = [50, HEIGHT - PLAYER_HEIGHT]
        self.vel = [0, 0]
        self.frame = 0
        self.speed = 6
        self.is_alive = True
        self.is_attacking = False
        self.sprites_walk = [f"oyuncu_yürüme{i}" for i in range(1, 9)]
        self.sprites_idle = [f"oyuncu_durma{i}" for i in range(1, 3)]
        self.sprites_attack = [f"oyuncu_alev{i}" for i in range(1, 7)]
        self.sprites_death = [f"oyuncu_ölüm{i}" for i in range(1, 6)]
        self.sprites_walk_sol = [f"oyuncu_yürüme{i}_sol" for i in range(1, 9)]
        self.sprites_idle_sol = [f"oyuncu_durma{i}_sol" for i in range(1, 3)]
        self.sprites_attack_sol = [f"oyuncu_alev{i}_sol" for i in range(1, 7)]
        self.sprites_death_sol = [f"oyuncu_ölüm{i}_sol" for i in range(1, 6)]
        self.current_sprite = self.sprites_idle[0]
        self.flame = None
        self.animation_delay = 5
        self.delay_counter = 0
        self.direction = "right"
        self.on_ground = False

    def update(self):
        if not self.is_alive:
            if not self.on_ground:
                self.vel[1] += GRAVITY
                self.pos[1] += self.vel[1]
                for platform in platforms:
                    if self.colliderect(platform):
                        self.pos[1] = platform.top - PLAYER_HEIGHT
                        self.vel[1] = 0
                        self.on_ground = True
                        break
            self.play_death_animation()
            if self.frame >= len(self.sprites_death):
                self.pos[1] += 50 # Ölüm animasyonu bitince kaydır
            return

        if keyboard.left and not self.is_attacking:
            self.vel[0] = -self.speed
            self.direction = "left"
            self.update_animation(self.sprites_walk_sol)
        elif keyboard.right and not self.is_attacking:
            self.vel[0] = self.speed
            self.direction = "right"
            self.update_animation(self.sprites_walk)
        elif not self.is_attacking:
            self.vel[0] = 0
            if self.direction == "left":
                self.update_animation(self.sprites_idle_sol)
            else:
                self.update_animation(self.sprites_idle)

        if keyboard.up and self.on_ground:
            self.vel[1] = -15

        if keyboard.space and not self.is_attacking:
            self.is_attacking = True
            self.frame = 0

        if self.is_attacking:
            if self.direction == "left":
                self.update_animation(self.sprites_attack_sol)
                if self.frame == len(self.sprites_attack) - 1:
                    self.flame = Flame(list(self.pos), self.direction, self.current_sprite)
            else:
                self.update_animation(self.sprites_attack)
                if self.frame == len(self.sprites_attack) - 1:
                    self.flame = Flame(list(self.pos), self.direction, self.current_sprite)

            if self.frame >= len(self.sprites_attack):
                self.frame = 0
                self.is_attacking = False

        self.vel[1] += GRAVITY
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        self.on_ground = False
        for platform in platforms:
            if self.colliderect(platform):
                self.pos[1] = platform.top - PLAYER_HEIGHT
                self.vel[1] = 0
                self.on_ground = True
                break

        if self.pos[0] < 0:
            self.pos[0] = 0
        elif self.pos[0] > WIDTH:
            self.pos[0] = WIDTH

    def update_animation(self, sprites):
        if self.delay_counter >= self.animation_delay:
            if self.is_attacking:
                if self.frame < len(sprites):
                    self.current_sprite = sprites[self.frame]
                    self.frame += 1
            else:
                self.frame = (self.frame + 1) % len(sprites)
                self.current_sprite = sprites[self.frame]
            self.delay_counter = 0
        else:
            self.delay_counter += 1

    def play_death_animation(self):
        if self.delay_counter >= self.animation_delay:
            if self.frame < len(self.sprites_death):
                if self.direction == "left":
                    self.current_sprite = self.sprites_death_sol[self.frame]
                else:
                    self.current_sprite = self.sprites_death[self.frame]
                self.frame += 1
            self.delay_counter = 0
        else:
            self.delay_counter += 1

    def draw(self):
        if self.direction == "left":
            image = self.current_sprite
            screen.blit(image, (self.pos[0] - 20, self.pos[1]))
        elif self.direction == "right":
            screen.blit(self.current_sprite, (self.pos[0] - 20, self.pos[1]))

        if self.flame and self.flame.active:
            self.flame.update()
            self.flame.draw()

    def colliderect(self, rect):
        player_rect = Rect(self.pos[0] - 20, self.pos[1], 40, PLAYER_HEIGHT)
        return player_rect.colliderect(rect)

    def get_rect(self):
        return Rect(self.pos[0] - 20, self.pos[1], 40, PLAYER_HEIGHT)


class Flame:
    def __init__(self, player_pos, direction, player_sprite):
        self.direction = direction
        self.image = "alev" if self.direction == "right" else "alev_sol"
        try:
            player_sprite_image = images.load(player_sprite)
            if self.direction == "left":
                alev_x = player_pos[0] - player_sprite_image.get_width() // 2 - 30
            else:
                alev_x = player_pos[0] + player_sprite_image.get_width() // 2 + 30
            self.pos = [alev_x, player_pos[1] - 65]
        except Exception as e:
            print(f"Hata: {e}")
            self.active = False
            return
        self.speed = 10
        self.active = True
        self.lifetime = 80

    def update(self):
        if self.active:
            if self.direction == "right":
                self.pos[0] += self.speed
            elif self.direction == "left":
                self.pos[0] -= self.speed
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.active = False

            if self.pos[0] < 0 or self.pos[0] > WIDTH:
                self.active = False

    def draw(self):
        if self.active:
            screen.blit(self.image, (self.pos[0], self.pos[1]))

    def get_rect(self):
        if self.active:
            return Rect(self.pos[0], self.pos[1], images.load(self.image).get_width(), images.load(self.image).get_height())
        else:
            return None

class Enemy:
    def __init__(self):
        self.pos = [WIDTH - 50, randint(50, HEIGHT - ENEMY_HEIGHT - 50)]
        self.speed = 2.5
        self.frame = 0
        self.is_alive = True
        self.sprites_walk = [f"düşman_yürüme{i}" for i in range(1, 8)]
        self.sprites_death = [f"düşman_ölüm{i}" for i in range(1, 4)]
        self.sprites_walk_sol = [f"düşman_yürüme{i}_sol" for i in range(1, 8)]
        self.sprites_death_sol = [f"düşman_ölüm{i}_sol" for i in range(1, 4)]
        self.current_sprite = self.sprites_walk[0]
        self.death_timer = 0
        self.animation_delay = 5
        self.delay_counter = 0
        self.direction = "right"
        self.dying = False
        self.vel = [0, 0]  # Düşman için dikey hız eklendi
        self.on_ground = False

    def update(self, player):
        if self.dying:
            self.play_death_animation()
            if not self.on_ground:
                self.vel[1] += GRAVITY
                self.pos[1] += self.vel[1]
                for platform in platforms:
                    if self.get_rect().colliderect(platform):
                        self.pos[1] = platform.top - ENEMY_HEIGHT
                        self.vel[1] = 0
                        self.on_ground = True
                        break

            if self.frame >= len(self.sprites_death):
                 self.pos[1] += 50 # Ölüm animasyonu bitince kaydır
            return

        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]

        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed

        if dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

        if self.direction == "left":
            self.update_animation(self.sprites_walk_sol)
        elif self.direction == "right":
            self.update_animation(self.sprites_walk)

    def update_animation(self, sprites):
        if self.delay_counter >= self.animation_delay:

            if self.direction == "left":
               self.current_sprite = sprites[self.frame]
            elif self.direction == "right":
               self.current_sprite = sprites[self.frame]

            self.frame = (self.frame + 1) % len(sprites)
            self.delay_counter = 0

        else:
            self.delay_counter += 1

    def play_death_animation(self):
        if self.delay_counter >= self.animation_delay:
            if self.frame < len(self.sprites_death):
                if self.direction == "left":
                    self.current_sprite = self.sprites_death_sol[self.frame]
                elif self.direction == "right":
                    self.current_sprite = self.sprites_death[self.frame]
                self.frame += 1
            else:
                self.is_alive = False

            self.delay_counter = 0
        else:
            self.delay_counter += 1

    def draw(self):
        screen.blit(self.current_sprite, (self.pos[0] - 20, self.pos[1]))

    def get_rect(self):
        return Rect(self.pos[0] - 20, self.pos[1], 40, ENEMY_HEIGHT)


player = Player()
enemy = Enemy()
enemy_respawn_timer = None
player_death_timer = None
menu_options = ["Oyuna Başla", "Sesi Aç/Kapat", "Çık"]
selected_option = 0

def draw():
    if not game_started:
        draw_menu()
    elif game_over:
        draw_game_over()
    else:
        draw_game()

def draw_menu():
    screen.clear()
    screen.fill(BACKGROUND_COLOR)
    screen.draw.text("Ana Menü", center=(WIDTH // 2, 100), fontsize=50, color="white")
    for i, option in enumerate(menu_options):
        color = "yellow" if i == selected_option else "white"
        screen.draw.text(option, center=(WIDTH // 2, 200 + i * 50), fontsize=30, color=color)


def draw_game():
    screen.clear()
    screen.fill((135, 206, 235))
    screen.draw.text(f"Puan: {score}", (10, 10), fontsize=30, color="black")
    player.draw()

    for platform in platforms:
        screen.draw.filled_rect(platform, (255, 0, 0))

    if enemy.is_alive or enemy.dying:
        enemy.draw()


def draw_game_over():
    screen.clear()
    screen.fill(BACKGROUND_COLOR)
    screen.draw.text(f"Skor: {score}", center=(WIDTH // 2, 100), fontsize=50, color="white")
    screen.draw.text("Yeniden Başlat", center=(WIDTH // 2, 250), fontsize=30,
                     color="yellow" if selected_option == 0 else "white")
    screen.draw.text("Çık", center=(WIDTH // 2, 300), fontsize=30,
                     color="yellow" if selected_option == 1 else "white")


def update():
    global game_started, game_over, score, enemy, enemy_respawn_timer, player, player_death_timer

    if game_started and not game_over:
        player.update()

        if enemy.is_alive:
            enemy.update(player)

        if enemy.is_alive and player.is_alive:
            if player.get_rect().colliderect(enemy.get_rect()):
                player.is_alive = False
                player.dying = True
                player_death_timer = time.time()
            elif player.flame and player.flame.active:
                if player.flame.get_rect().colliderect(enemy.get_rect()):
                    enemy.dying = True
                    enemy.frame = 0
                    score += 1
                    enemy_respawn_timer = time.time()
                    player.flame.active = False

        if enemy_respawn_timer and time.time() - enemy_respawn_timer >= 3:
            enemy = Enemy()
            enemy_respawn_timer = None

        if player_death_timer and time.time() - player_death_timer >= 2:
            game_over = True



def on_key_down(key):
    global game_started, selected_option, sound_on, game_over

    if not game_started:
        if key == keys.DOWN:
            selected_option = (selected_option + 1) % len(menu_options)
        elif key == keys.UP:
            selected_option = (selected_option - 1) % len(menu_options)
        elif key == keys.RETURN:
            if menu_options[selected_option] == "Oyuna Başla":
                game_started = True
                music.play("background_music")
            elif menu_options[selected_option] == "Sesi Aç/Kapat":
                sound_on = not sound_on
            elif menu_options[selected_option] == "Çık":
                exit()
    elif game_over:
        if key == keys.UP or key == keys.DOWN:
            selected_option = (selected_option + 1) % 2
        elif key == keys.RETURN:
            if selected_option == 0:
                reset_game()
            elif selected_option == 1:
                exit()

    elif key == keys.ESCAPE:
        game_started = False

def reset_game():
    global game_started, game_over, score, enemy, player, enemy_respawn_timer, player_death_timer
    game_started = True
    game_over = False
    score = 0
    player = Player()
    enemy = Enemy()
    enemy_respawn_timer = None
    player_death_timer = None



def on_mouse_down(pos):
    global game_started, sound_on
    if not game_started:
        for i, option in enumerate(menu_options):
            if Rect((WIDTH // 2) - 75, 200 + i * 50 - 15, 150, 30).collidepoint(pos):
                if i == 0:
                    game_started = True
                    music.play("background_music")
                elif i == 1:
                    sound_on = not sound_on
                    menu_options[1] = f"Sesi {'Aç' if sound_on else 'Kapat'}"
                elif i == 2:
                    exit()

pgzrun.go()