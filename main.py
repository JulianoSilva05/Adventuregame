import pgzero
import math
import random
from pygame import Rect

try:
    from pgzero.builtins import music, sounds
except ImportError:
    pass

try:
    import pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
except:
    pass

WIDTH = 800
HEIGHT = 600
TITLE = "Adventure Game"

GAME_STATE = "menu"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (128, 128, 128)

start_button = Rect(300, 200, 200, 50)
settings_button = Rect(300, 270, 200, 50)
exit_button = Rect(300, 340, 200, 50)
back_button = Rect(50, 50, 100, 40)

music_enabled = True
sounds_enabled = True
music_toggle_button = Rect(300, 200, 200, 50)
sounds_toggle_button = Rect(300, 270, 200, 50)

try:
    music.play('background')
    music.set_volume(0.3)
    print("Música de fundo iniciada!")
except Exception as e:
    print(f"Erro ao carregar música: {e}")
    pass

class Hero:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 32, 32)
        self.speed = 3
        self.animation_frame = 0
        self.animation_timer = 0
        self.breathing_timer = 0
        self.direction = "right"
        self.moving = False
        
    def update(self):
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= 8:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
        else:
            self.animation_frame = 0
            
        self.breathing_timer += 1
        if self.breathing_timer >= 120:
            self.breathing_timer = 0
            
        self.rect.clamp_ip(Rect(0, 0, WIDTH, HEIGHT))
        
    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.moving = dx != 0 or dy != 0
        
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
            
    def draw(self, screen):
        base_color = BLUE
        
        breathing_offset = 0
        if not self.moving:
            breathing_cycle = self.breathing_timer / 60.0
            breathing_offset = int(math.sin(breathing_cycle * math.pi) * 2)
        
        body_rect = Rect(self.rect.x, self.rect.y + breathing_offset, 
                        self.rect.width, self.rect.height - 4)
        screen.draw.filled_rect(body_rect, base_color)
        
        head_size = 12 + breathing_offset // 2
        head_x = self.rect.centerx - head_size // 2
        head_y = self.rect.y - 8 + breathing_offset
        screen.draw.filled_circle((self.rect.centerx, head_y + head_size // 2), 
                                head_size // 2, (0, 120, 220))
        
        eye_offset = 6 if self.direction == "right" else -6
        eye_x = self.rect.centerx + eye_offset // 2
        eye_y = head_y + 4
        screen.draw.filled_circle((eye_x, eye_y), 2, WHITE)
        screen.draw.filled_circle((eye_x + (1 if self.direction == "right" else -1), eye_y), 1, BLACK)
        
        # Legs animation when moving
        if self.moving:
            leg_offset = 0
            if self.animation_frame == 1 or self.animation_frame == 3:
                leg_offset = 3 if self.animation_frame == 1 else -3
            
            # Left leg
            left_leg_x = self.rect.centerx - 6 + (leg_offset if self.direction == "right" else -leg_offset)
            screen.draw.filled_rect(Rect(left_leg_x, self.rect.bottom - 4, 4, 8), (0, 80, 160))
            
            # Right leg  
            right_leg_x = self.rect.centerx + 2 + (-leg_offset if self.direction == "right" else leg_offset)
            screen.draw.filled_rect(Rect(right_leg_x, self.rect.bottom - 4, 4, 8), (0, 80, 160))
        else:
            # Static legs when not moving
            screen.draw.filled_rect(Rect(self.rect.centerx - 6, self.rect.bottom - 4, 4, 6), (0, 80, 160))
            screen.draw.filled_rect(Rect(self.rect.centerx + 2, self.rect.bottom - 4, 4, 6), (0, 80, 160))
        
        # Arms
        arm_y = self.rect.centery - 2 + breathing_offset
        if self.moving:
            # Swinging arms
            arm_swing = 2 if self.animation_frame % 2 == 0 else -2
            screen.draw.filled_rect(Rect(self.rect.x - 2, arm_y + arm_swing, 4, 12), (0, 100, 200))
            screen.draw.filled_rect(Rect(self.rect.right - 2, arm_y - arm_swing, 4, 12), (0, 100, 200))
        else:
            # Static arms
            screen.draw.filled_rect(Rect(self.rect.x - 2, arm_y, 4, 10), (0, 100, 200))
            screen.draw.filled_rect(Rect(self.rect.right - 2, arm_y, 4, 10), (0, 100, 200))

class Enemy:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 24, 24)
        self.speed = 1
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.animation_frame = 0
        self.animation_timer = 0
        self.look_timer = 0
        self.look_direction = 0  # -1 left, 0 center, 1 right
        self.breathing_timer = 0
        self.territory_center = (x, y)
        self.territory_radius = 100
        self.moving = False
        
    def update(self):
        was_moving = self.moving
        self.moving = self.direction_x != 0 or self.direction_y != 0
        
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= 12:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
        else:
            self.animation_frame = 0
            
        self.look_timer += 1
        if not self.moving or random.randint(1, 180) == 1:
            if self.look_timer >= 90:
                self.look_direction = random.choice([-1, 0, 1])
                self.look_timer = 0
        
        self.breathing_timer += 1
        if self.breathing_timer >= 150:
            self.breathing_timer = 0
            
        # Move enemy
        new_x = self.rect.x + self.direction_x * self.speed
        new_y = self.rect.y + self.direction_y * self.speed
        
        # Check territory bounds
        distance_from_center = math.sqrt(
            (new_x - self.territory_center[0])**2 + 
            (new_y - self.territory_center[1])**2
        )
        
        if distance_from_center > self.territory_radius:
            self.direction_x *= -1
            self.direction_y *= -1
        else:
            self.rect.x = new_x
            self.rect.y = new_y
            
        # Random direction change
        if random.randint(1, 90) == 1:
            self.direction_x = random.choice([-1, 0, 1])
            self.direction_y = random.choice([-1, 0, 1])
            
        # Keep within screen bounds
        self.rect.clamp_ip(Rect(0, 0, WIDTH, HEIGHT))
        
    def draw(self, screen):
        base_color = RED
        
        breathing_offset = 0
        if not self.moving:
            breathing_cycle = self.breathing_timer / 75.0
            breathing_offset = int(math.sin(breathing_cycle * math.pi) * 1.5)
        
        body_rect = Rect(self.rect.x, self.rect.y + breathing_offset, 
                        self.rect.width, self.rect.height - 3)
        screen.draw.filled_rect(body_rect, base_color)
        
        head_size = 10 + breathing_offset // 2
        head_y = self.rect.y - 6 + breathing_offset
        screen.draw.filled_circle((self.rect.centerx, head_y + head_size // 2), 
                                head_size // 2, (220, 0, 0))
        
        base_eye_x = self.rect.centerx
        eye_y = head_y + 3
        
        left_eye_x = base_eye_x - 3 + self.look_direction
        screen.draw.filled_circle((left_eye_x, eye_y), 2, WHITE)
        screen.draw.filled_circle((left_eye_x + self.look_direction, eye_y), 1, BLACK)
        
        right_eye_x = base_eye_x + 3 + self.look_direction
        screen.draw.filled_circle((right_eye_x, eye_y), 2, WHITE)
        screen.draw.filled_circle((right_eye_x + self.look_direction, eye_y), 1, BLACK)
        
        if self.moving:
            leg_offset = 0
            if self.animation_frame == 1 or self.animation_frame == 3:
                leg_offset = 2 if self.animation_frame == 1 else -2
            
            left_leg_x = self.rect.centerx - 4 + leg_offset
            screen.draw.filled_rect(Rect(left_leg_x, self.rect.bottom - 3, 3, 6), (160, 0, 0))
            
            right_leg_x = self.rect.centerx + 1 - leg_offset
            screen.draw.filled_rect(Rect(right_leg_x, self.rect.bottom - 3, 3, 6), (160, 0, 0))
        else:
            screen.draw.filled_rect(Rect(self.rect.centerx - 4, self.rect.bottom - 3, 3, 5), (160, 0, 0))
            screen.draw.filled_rect(Rect(self.rect.centerx + 1, self.rect.bottom - 3, 3, 5), (160, 0, 0))
        
        arm_y = self.rect.centery - 1 + breathing_offset
        if self.moving:
            arm_swing = 1 if self.animation_frame % 2 == 0 else -1
            screen.draw.filled_rect(Rect(self.rect.x - 1, arm_y + arm_swing, 3, 8), (180, 0, 0))
            screen.draw.filled_rect(Rect(self.rect.right - 2, arm_y - arm_swing, 3, 8), (180, 0, 0))
        else:
            screen.draw.filled_rect(Rect(self.rect.x - 1, arm_y, 3, 7), (180, 0, 0))
            screen.draw.filled_rect(Rect(self.rect.right - 2, arm_y, 3, 7), (180, 0, 0))
        
        screen.draw.filled_circle((self.rect.centerx - 4, self.rect.centery - 4), 2, WHITE)
        screen.draw.filled_circle((self.rect.centerx + 4, self.rect.centery - 4), 2, WHITE)

# Game objects
hero = Hero(100, 100)
enemies = [
    Enemy(300, 200),
    Enemy(500, 300),
    Enemy(200, 400),
    Enemy(600, 150)
]

def update():
    global GAME_STATE
    
    # Ensure background music keeps playing
    if music_enabled:
        try:
            if not music.get_busy():
                music.play('background')
                music.set_volume(0.3)
        except Exception as e:
            pass  # Continue without music if file not found
    
    if GAME_STATE == "playing":
        dx, dy = 0, 0
        if keyboard.left or keyboard.a:
            dx = -1
        if keyboard.right or keyboard.d:
            dx = 1
        if keyboard.up or keyboard.w:
            dy = -1
        if keyboard.down or keyboard.s:
            dy = 1
            
        hero.move(dx, dy)
        hero.update()
        
        for enemy in enemies:
            enemy.update()
            
        for enemy in enemies:
            if hero.rect.colliderect(enemy.rect):
                if sounds_enabled:
                    try:
                        sounds.hit.play()
                    except:
                        pass
                if hero.rect.centerx < enemy.rect.centerx:
                    hero.rect.x = enemy.rect.left - hero.rect.width
                else:
                    hero.rect.x = enemy.rect.right
                    
        if keyboard.escape:
            GAME_STATE = "menu"

def draw():
    screen.clear()
    
    if GAME_STATE == "menu":
        draw_menu()
    elif GAME_STATE == "settings":
        draw_settings()
    elif GAME_STATE == "playing":
        draw_game()
        
def draw_menu():
    screen.fill(BLACK)
    
    # Title
    screen.draw.text("ADVENTURE GAME", center=(WIDTH//2, 100), fontsize=50, color=WHITE)
    
    # Buttons
    screen.draw.filled_rect(start_button, BLUE)
    screen.draw.text("Start Game", center=start_button.center, fontsize=30, color=WHITE)
    
    screen.draw.filled_rect(settings_button, GRAY)
    screen.draw.text("Music & Sounds", center=settings_button.center, fontsize=30, color=WHITE)
    
    screen.draw.filled_rect(exit_button, RED)
    screen.draw.text("Exit", center=exit_button.center, fontsize=30, color=WHITE)
    
    # Instructions
    screen.draw.text("Use WASD or Arrow Keys to move", center=(WIDTH//2, 450), fontsize=20, color=WHITE)
    screen.draw.text("Avoid the red enemies!", center=(WIDTH//2, 480), fontsize=20, color=WHITE)
    screen.draw.text("Press ESC to return to menu", center=(WIDTH//2, 510), fontsize=20, color=WHITE)

def draw_settings():
    screen.fill(BLACK)
    
    # Title
    screen.draw.text("SETTINGS", center=(WIDTH//2, 100), fontsize=40, color=WHITE)
    
    # Music toggle
    music_color = GREEN if music_enabled else RED
    screen.draw.filled_rect(music_toggle_button, music_color)
    music_text = "Music: ON" if music_enabled else "Music: OFF"
    screen.draw.text(music_text, center=music_toggle_button.center, fontsize=25, color=WHITE)
    
    # Sounds toggle
    sounds_color = GREEN if sounds_enabled else RED
    screen.draw.filled_rect(sounds_toggle_button, sounds_color)
    sounds_text = "Sounds: ON" if sounds_enabled else "Sounds: OFF"
    screen.draw.text(sounds_text, center=sounds_toggle_button.center, fontsize=25, color=WHITE)
    
    # Back button
    screen.draw.filled_rect(back_button, GRAY)
    screen.draw.text("Back", center=back_button.center, fontsize=20, color=WHITE)

def draw_game():
    screen.fill((20, 50, 20))  # Dark green background
    
    # Draw hero
    hero.draw(screen)
    
    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen)
        
    # Draw UI
    screen.draw.text("Adventure Mode", (10, 10), fontsize=25, color=WHITE)
    screen.draw.text("ESC: Menu", (10, HEIGHT - 30), fontsize=20, color=WHITE)

def on_mouse_down(pos):
    global GAME_STATE, music_enabled, sounds_enabled
    
    if GAME_STATE == "menu":
        if start_button.collidepoint(pos):
            # Play button click sound
            if sounds_enabled:
                try:
                    sounds.click.play()
                except:
                    pass
            GAME_STATE = "playing"
        elif settings_button.collidepoint(pos):
            # Play button click sound
            if sounds_enabled:
                try:
                    sounds.click.play()
                except:
                    pass
            GAME_STATE = "settings"
        elif exit_button.collidepoint(pos):
            # Play button click sound
            if sounds_enabled:
                try:
                    sounds.click.play()
                except:
                    pass
            exit()
            
    elif GAME_STATE == "settings":
        if music_toggle_button.collidepoint(pos):
            # Play button click sound
            if sounds_enabled:
                try:
                    sounds.click.play()
                except:
                    pass
            music_enabled = not music_enabled
            # Toggle background music
            if music_enabled:
                try:
                    music.play('background')
                    music.set_volume(0.3)
                    print("Música ligada!")
                except Exception as e:
                    print(f"Erro: {e} - Adicione um arquivo sounds/background.ogg")
                    pass
            else:
                try:
                    music.stop()
                    print("Música desligada!")
                except:
                    pass
        elif sounds_toggle_button.collidepoint(pos):
            # Play button click sound
            if sounds_enabled:
                try:
                    sounds.click.play()
                except:
                    pass
            sounds_enabled = not sounds_enabled
        elif back_button.collidepoint(pos):
            # Play button click sound
            if sounds_enabled:
                try:
                    sounds.click.play()
                except:
                    pass
            GAME_STATE = "menu"

# Initialize game
if __name__ == "__main__":
    # Start background music if enabled
    if music_enabled:
        try:
            music.play('background')
            music.set_volume(0.3)
        except:
            pass
    
    try:
        import pgzrun
        pgzrun.go()
    except Exception as e:
        print(f"Erro ao iniciar o jogo: {e}")
        print("Use 'pgzrun main.py' para executar o jogo.")