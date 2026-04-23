import math
import pygame
import random
import sys
from button import Button

# Initialize pygame 
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors for the game
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 70, 200)
GRAY = (100, 100, 100)

# STEP 1: The first step was to get a basic window up and running with a title. 
# This involved initializing pygame, setting the screen dimensions, and creating a display surface.
# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RUN AWAY")

# Clock for FPS (frames per second) control
clock = pygame.time.Clock()
FPS = 60

# Fonts for text
title_font = pygame.font.Font(None, 72)
button_font = pygame.font.Font(None, 40)

# Game states for managing different screens and logic
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_WON = 3


# Create start and restart buttons
start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60, "START", BLUE, DARK_BLUE, button_font, WHITE)
restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60, "RESTART", BLUE, DARK_BLUE, button_font, WHITE)

# Main game state vriable
current_state = GAME_STATE_START

# Timer variables
show_text = False
start_time = 0

# Player variables
player_size = 20
player_color = (255, 0, 0)
player_speed = 5
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2 + 100

# Enemy variables (spiky black follower)
enemy_size = 26
enemy_color = BLACK
enemy_speed = 0.5
enemy_x = SCREEN_WIDTH // 2 - 200
enemy_y = SCREEN_HEIGHT // 2 - 150

# Powerup variables
enemy_speed_increase_interval = 1000000  # ms
powerup_spawn_interval = 10000  # ms
last_powerup_time = 0
powerups = []  # {'type': 'speed', 'medkit', or 'gun', 'x': x, 'y': y}

# Player lives and base speed
player_lives = 3
player_speed_boost = 0
speed_boost_end_time = 0

# Gun/bullet variables
gun_collected = False
ammo = 0
bullet_speed = 12
bullet_cooldown = 200
last_shot_time = 0
bullets = []  # {'x', 'y', 'dx', 'dy'}

# Enemy health for win condition
enemy_health = 5

# Boss variables
boss_active = False
boss_size = 50
boss_color = (100, 0, 100)  # Dark purple
boss_speed = 1.5
boss_x = SCREEN_WIDTH // 2
boss_y = SCREEN_HEIGHT // 2 - 200
boss_health = 20
boss_projectiles = []  # {'x', 'y', 'dx', 'dy'}
boss_projectile_speed = 6
boss_shoot_cooldown = 1500  # ms
last_boss_shot = 0

def reset_game():
    global current_state, show_text, start_time, player_x, player_y, enemy_x, enemy_y, last_powerup_time, powerups, player_lives, player_speed_boost, enemy_speed, speed_boost_end_time, gun_collected, ammo, bullets, enemy_health, boss_active, boss_health, boss_projectiles, last_boss_shot
    current_state = GAME_STATE_PLAYING
    show_text = True
    start_time = pygame.time.get_ticks()
    last_powerup_time = pygame.time.get_ticks()
    powerups = []
    player_lives = 3
    player_speed_boost = 0
    speed_boost_end_time = 0
    gun_collected = False
    ammo = 0
    bullets = []
    enemy_health = 5
    boss_active = False
    boss_health = 20
    boss_projectiles = []
    last_boss_shot = 0
    enemy_speed = 2

    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2 + 100
    enemy_x = SCREEN_WIDTH // 2 - 200
    enemy_y = SCREEN_HEIGHT // 2 - 150

# Main game loop 
running = True
while running:
    clock.tick(FPS)
    
    # Get events
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_clicked = True
    
    # Update
    if current_state == GAME_STATE_START:
        start_button.update(mouse_pos)
        if start_button.is_clicked(mouse_pos, mouse_clicked):
            reset_game()

    elif current_state == GAME_STATE_GAME_OVER or current_state == GAME_STATE_WON:
        restart_button.update(mouse_pos)
        if restart_button.is_clicked(mouse_pos, mouse_clicked):
            reset_game()

    if current_state == GAME_STATE_PLAYING and show_text:
        if pygame.time.get_ticks() - start_time > 1000:
            show_text = False

    if current_state == GAME_STATE_PLAYING:
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Normalize movement so diagonal speed is not faster
        length = math.hypot(dx, dy)
        if length != 0:
            dx /= length
            dy /= length

        # Apply movement
        player_x += dx * (player_speed + player_speed_boost)
        player_y += dy * (player_speed + player_speed_boost)

        # Keep player inside screen bounds
        player_x = max(player_size // 2, min(SCREEN_WIDTH - player_size // 2, player_x))
        player_y = max(player_size // 2, min(SCREEN_HEIGHT - player_size // 2, player_y))

        # Spawn powerups and increase enemy speed every 10 seconds
        now = pygame.time.get_ticks()

        if now - last_powerup_time >= powerup_spawn_interval:
            last_powerup_time = now
            enemy_speed += 0.5
            # spawn 3 powerups at random positions: speed, medkit, gun
            # ensure they are not too close to the edges
            for ptype in ["speed", "medkit", "gun"]:
                px = random.randint(50, SCREEN_WIDTH - 50)
                py = random.randint(50, SCREEN_HEIGHT - 50)
                powerups.append({"type": ptype, "x": px, "y": py})

        # Collect powerups
        for pu in powerups[:]:
            if math.hypot(player_x - pu["x"], player_y - pu["y"]) <= (player_size + 20) / 2:
                if pu["type"] == "speed":
                    player_speed_boost += 2
                    speed_boost_end_time = now + 5000
                elif pu["type"] == "medkit":
                    player_lives += 1
                elif pu["type"] == "gun":
                    gun_collected = True
                    ammo = 15
                powerups.remove(pu)

        # Speed boost timeout
        if speed_boost_end_time and now >= speed_boost_end_time:
            player_speed_boost = 0
            speed_boost_end_time = 0

        # Shooting
        if gun_collected and ammo > 0 and keys[pygame.K_SPACE]:
            if now - last_shot_time >= bullet_cooldown:
                last_shot_time = now
                # shoot in mouse direction
                mx, my = mouse_pos
                bullet_x, bullet_y = player_x, player_y
                angle = math.atan2(my - bullet_y, mx - bullet_x)
                bullets.append({
                    "x": bullet_x,
                    "y": bullet_y,
                    "dx": math.cos(angle) * bullet_speed,
                    "dy": math.sin(angle) * bullet_speed,
                })
                ammo -= 1

        # Update bullets
        for b in bullets[:]:
            b["x"] += b["dx"]
            b["y"] += b["dy"]
            # remove offscreen bullets
            if b["x"] < 0 or b["x"] > SCREEN_WIDTH or b["y"] < 0 or b["y"] > SCREEN_HEIGHT:
                bullets.remove(b)

        # Enemy follows player at slower speed
        if not boss_active:
            ex = player_x - enemy_x
            ey = player_y - enemy_y
            dist = math.hypot(ex, ey)
            if dist > 0:
                enemy_x += (ex / dist) * enemy_speed
                enemy_y += (ey / dist) * enemy_speed

        # Boss behavior
        if boss_active:
            # Boss follows player slowly
            boss_dx = player_x - boss_x
            boss_dy = player_y - boss_y
            boss_distance = math.hypot(boss_dx, boss_dy)
            if boss_distance > 0:
                boss_x += (boss_dx / boss_distance) * boss_speed
                boss_y += (boss_dy / boss_distance) * boss_speed
            
            # Boss shoots projectiles at player
            now = pygame.time.get_ticks()
            if now - last_boss_shot >= boss_shoot_cooldown:
                last_boss_shot = now
                # Shoot towards player
                angle = math.atan2(player_y - boss_y, player_x - boss_x)
                boss_projectiles.append({
                    "x": boss_x,
                    "y": boss_y,
                    "dx": math.cos(angle) * boss_projectile_speed,
                    "dy": math.sin(angle) * boss_projectile_speed,
                })

        # Update boss projectiles
        for p in boss_projectiles[:]:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            # Remove offscreen projectiles
            if p["x"] < 0 or p["x"] > SCREEN_WIDTH or p["y"] < 0 or p["y"] > SCREEN_HEIGHT:
                boss_projectiles.remove(p)

        # Bullet hits enemy (only if not boss active)
        if not boss_active:
            for b in bullets[:]:
                if math.hypot(b["x"] - enemy_x, b["y"] - enemy_y) <= (enemy_size / 2 + 4):
                    bullets.remove(b)
                    enemy_health -= 1
                    if enemy_health <= 0:
                        boss_active = True
                        # Boss appears, maybe with a message
                        show_text = True
                        start_time = pygame.time.get_ticks()
                        break

        # Bullet hits boss
        if boss_active:
            for b in bullets[:]:
                if math.hypot(b["x"] - boss_x, b["y"] - boss_y) <= (boss_size / 2 + 4):
                    bullets.remove(b)
                    boss_health -= 1
                    if boss_health <= 0:
                        current_state = GAME_STATE_WON
                        break

        # Keep enemy inside bounds
        if not boss_active:
            enemy_x = max(enemy_size // 2, min(SCREEN_WIDTH - enemy_size // 2, enemy_x))
            enemy_y = max(enemy_size // 2, min(SCREEN_HEIGHT - enemy_size // 2, enemy_y))

        # Keep boss inside bounds
        if boss_active:
            boss_x = max(boss_size // 2, min(SCREEN_WIDTH - boss_size // 2, boss_x))
            boss_y = max(boss_size // 2, min(SCREEN_HEIGHT - boss_size // 2, boss_y))

        # Collision detection (enemy catches player)
        if not boss_active:
            collision_distance = (player_size + enemy_size) / 2
            if math.hypot(player_x - enemy_x, player_y - enemy_y) <= collision_distance:
                player_lives -= 1
                if player_lives <= 0:
                    current_state = GAME_STATE_GAME_OVER
                else:
                    # respawn player and enemy after hit
                    player_x = SCREEN_WIDTH // 2
                    player_y = SCREEN_HEIGHT // 2 + 100
                    enemy_x = SCREEN_WIDTH // 2 - 200
                    enemy_y = SCREEN_HEIGHT // 2 - 150

        # Boss catches player
        if boss_active:
            boss_collision_distance = (player_size + boss_size) / 2
            if math.hypot(player_x - boss_x, player_y - boss_y) <= boss_collision_distance:
                player_lives -= 1
                if player_lives <= 0:
                    current_state = GAME_STATE_GAME_OVER
                else:
                    # respawn player after boss hit
                    player_x = SCREEN_WIDTH // 2
                    player_y = SCREEN_HEIGHT // 2 + 100

        # Boss projectiles hit player
        for p in boss_projectiles[:]:
            if math.hypot(p["x"] - player_x, p["y"] - player_y) <= (player_size / 2 + 4):
                boss_projectiles.remove(p)
                player_lives -= 1
                if player_lives <= 0:
                    current_state = GAME_STATE_GAME_OVER
                else:
                    # respawn player after projectile hit
                    player_x = SCREEN_WIDTH // 2
                    player_y = SCREEN_HEIGHT // 2 + 100

            if now - last_shot_time >= bullet_cooldown:
                last_shot_time = now
                # shoot in mouse direction
                mx, my = mouse_pos
                bullet_x, bullet_y = player_x, player_y
                angle = math.atan2(my - bullet_y, mx - bullet_x)
                bullets.append({
                    "x": bullet_x,
                    "y": bullet_y,
                    "dx": math.cos(angle) * bullet_speed,
                    "dy": math.sin(angle) * bullet_speed,
                })
                ammo -= 1

        # Update bullets
        for b in bullets[:]:
            b["x"] += b["dx"]
            b["y"] += b["dy"]
            # remove offscreen bullets
            if b["x"] < 0 or b["x"] > SCREEN_WIDTH or b["y"] < 0 or b["y"] > SCREEN_HEIGHT:
                bullets.remove(b)

        # Enemy follows player at slower speed
        if not boss_active:
            ex = player_x - enemy_x
            ey = player_y - enemy_y
            dist = math.hypot(ex, ey)
            if dist > 0:
                enemy_x += (ex / dist) * enemy_speed
                enemy_y += (ey / dist) * enemy_speed

        # Boss behavior
        if boss_active:
            # Boss follows player slowly
            boss_dx = player_x - boss_x
            boss_dy = player_y - boss_y
            boss_distance = math.hypot(boss_dx, boss_dy)
            if boss_distance > 0:
                boss_x += (boss_dx / boss_distance) * boss_speed
                boss_y += (boss_dy / boss_distance) * boss_speed
            
            # Boss shoots projectiles at player
            now = pygame.time.get_ticks()
            if now - last_boss_shot >= boss_shoot_cooldown:
                last_boss_shot = now
                # Shoot towards player
                angle = math.atan2(player_y - boss_y, player_x - boss_x)
                boss_projectiles.append({
                    "x": boss_x,
                    "y": boss_y,
                    "dx": math.cos(angle) * boss_projectile_speed,
                    "dy": math.sin(angle) * boss_projectile_speed,
                })

        # Update boss projectiles
        for p in boss_projectiles[:]:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            # Remove offscreen projectiles
            if p["x"] < 0 or p["x"] > SCREEN_WIDTH or p["y"] < 0 or p["y"] > SCREEN_HEIGHT:
                boss_projectiles.remove(p)

        # Bullet hits enemy (only if not boss active)
        if not boss_active:
            for b in bullets[:]:
                if math.hypot(b["x"] - enemy_x, b["y"] - enemy_y) <= (enemy_size / 2 + 4):
                    bullets.remove(b)
                    enemy_health -= 1
                    if enemy_health <= 0:
                        boss_active = True
                        # Boss appears, maybe with a message
                        show_text = True
                        start_time = pygame.time.get_ticks()
                        break

        # Bullet hits boss
        if boss_active:
            for b in bullets[:]:
                if math.hypot(b["x"] - boss_x, b["y"] - boss_y) <= (boss_size / 2 + 4):
                    bullets.remove(b)
                    boss_health -= 1
                    if boss_health <= 0:
                        current_state = GAME_STATE_WON
                        break

        # Keep enemy inside bounds - This is done after movement and before collision to make sure they don't get stuck on edges
        if not boss_active:
            enemy_x = max(enemy_size // 2, min(SCREEN_WIDTH - enemy_size // 2, enemy_x))
            enemy_y = max(enemy_size // 2, min(SCREEN_HEIGHT - enemy_size // 2, enemy_y))

        # Keep boss inside bounds
        if boss_active:
            boss_x = max(boss_size // 2, min(SCREEN_WIDTH - boss_size // 2, boss_x))
            boss_y = max(boss_size // 2, min(SCREEN_HEIGHT - boss_size // 2, boss_y))

        # Collision detection (enemy catches player)
        if not boss_active:
            collision_distance = (player_size + enemy_size) / 2
            if math.hypot(player_x - enemy_x, player_y - enemy_y) <= collision_distance:
                player_lives -= 1
                if player_lives <= 0:
                    current_state = GAME_STATE_GAME_OVER
                else:
                    # respawn player and enemy after hit
                    player_x = SCREEN_WIDTH // 2
                    player_y = SCREEN_HEIGHT // 2 + 100
                    enemy_x = SCREEN_WIDTH // 2 - 200
                    enemy_y = SCREEN_HEIGHT // 2 - 150

        # Boss catches player
        if boss_active:
            boss_collision_distance = (player_size + boss_size) / 2
            if math.hypot(player_x - boss_x, player_y - boss_y) <= boss_collision_distance:
                player_lives -= 1
                if player_lives <= 0:
                    current_state = GAME_STATE_GAME_OVER
                else:
                    # respawn player after boss hit
                    player_x = SCREEN_WIDTH // 2
                    player_y = SCREEN_HEIGHT // 2 + 100

        # Boss projectiles hit player
        for p in boss_projectiles[:]:
            if math.hypot(p["x"] - player_x, p["y"] - player_y) <= (player_size / 2 + 4):
                boss_projectiles.remove(p)
                player_lives -= 1
                if player_lives <= 0:
                    current_state = GAME_STATE_GAME_OVER
                else:
                    # respawn player after projectile hit
                    player_x = SCREEN_WIDTH // 2
                    player_y = SCREEN_HEIGHT // 2 + 100

    # Draw
    screen.fill(GRAY)
    
    if current_state == GAME_STATE_START:
        # Draw start screen
        title_text = title_font.render("Runner", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)
        
        start_button.draw(screen)
    
    elif current_state == GAME_STATE_PLAYING:
        # Draw game content
        if show_text:
            if boss_active and enemy_health <= 0:
                game_text = title_font.render("BOSS FIGHT!", True, BLACK)
            else:
                game_text = title_font.render("GOOD LUCK!", True, BLACK)
            game_rect = game_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_text, game_rect)
        else:
            # Draw player as red dot after text disappears
            pygame.draw.circle(screen, player_color, (int(player_x), int(player_y)), player_size // 2)

            # Draw bullets
            for b in bullets:
                pygame.draw.circle(screen, (0, 0, 0), (int(b["x"]), int(b["y"])), 4)

            # Draw spiky black enemy following the player
            if not boss_active:
                enemy_center = (int(enemy_x), int(enemy_y))
                pygame.draw.circle(screen, enemy_color, enemy_center, enemy_size // 2)
                for i in range(8):
                    angle = i * (math.pi * 2 / 8)
                    inner = enemy_size // 2
                    outer = enemy_size // 2 + 10
                    start_x = enemy_x + math.cos(angle) * inner
                    start_y = enemy_y + math.sin(angle) * inner
                    end_x = enemy_x + math.cos(angle) * outer
                    end_y = enemy_y + math.sin(angle) * outer
                    pygame.draw.line(screen, BLACK, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 3)

            # Draw boss
            if boss_active:
                boss_center = (int(boss_x), int(boss_y))
                pygame.draw.circle(screen, boss_color, boss_center, boss_size // 2)
                # Draw boss spikes
                for i in range(12):
                    angle = i * (math.pi * 2 / 12)
                    inner = boss_size // 2
                    outer = boss_size // 2 + 15
                    start_x = boss_x + math.cos(angle) * inner
                    start_y = boss_y + math.sin(angle) * inner
                    end_x = boss_x + math.cos(angle) * outer
                    end_y = boss_y + math.sin(angle) * outer
                    pygame.draw.line(screen, boss_color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 4)
                
                # Draw boss projectiles
                for p in boss_projectiles:
                    pygame.draw.circle(screen, (150, 0, 150), (int(p["x"]), int(p["y"])), 6)

            # Draw powerups
            for pu in powerups:
                px = int(pu["x"])
                py = int(pu["y"])
                if pu["type"] == "speed":
                    pygame.draw.polygon(screen, BLUE, [(px, py - 8), (px + 12, py), (px, py + 8), (px + 4, py),])
                elif pu["type"] == "medkit":
                    pygame.draw.rect(screen, (200, 0, 0), (px - 10, py - 10, 20, 20))
                    pygame.draw.rect(screen, WHITE, (px - 3, py - 10, 6, 20))
                    pygame.draw.rect(screen, WHITE, (px - 10, py - 3, 20, 6))
                elif pu["type"] == "gun":
                    pygame.draw.rect(screen, (150, 75, 0), (px - 8, py - 5, 16, 10))
                    pygame.draw.rect(screen, (0, 0, 0), (px - 8, py - 5, 16, 10), 2)

            # Health bar for enemy/boss
            health_bar_length = 150
            if boss_active:
                health_pct = max(0, min(1, boss_health / 20))
                health_text = "Boss Health"
            else:
                health_pct = max(0, min(1, enemy_health / 5))
                health_text = "Enemy Health"
            pygame.draw.rect(screen, (150, 150, 150), (SCREEN_WIDTH - 220, 20, health_bar_length, 20))
            pygame.draw.rect(screen, (0, 200, 0), (SCREEN_WIDTH - 220, 20, int(health_bar_length * health_pct), 20))
            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 220, 20, health_bar_length, 20), 2)
            
            # Health text
            health_label = button_font.render(health_text, True, BLACK)
            screen.blit(health_label, (SCREEN_WIDTH - 220, 45))

            # HUD: lives, speed boost, ammo
            hud_text = button_font.render(f"Lives: {player_lives}  Speed+: {player_speed_boost}  Ammo: {ammo}", True, BLACK)
            screen.blit(hud_text, (20, 20))

    elif current_state == GAME_STATE_GAME_OVER:
        game_over_text = title_font.render("YOU DIED", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(game_over_text, game_over_rect)

        restart_button.draw(screen)

    elif current_state == GAME_STATE_WON:
        win_text = title_font.render("YOU WIN!", True, BLACK)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(win_text, win_rect)

        restart_button.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

