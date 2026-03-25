import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 70, 200)
GRAY = (200, 200, 200)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Game")

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Fonts
title_font = pygame.font.Font(None, 72)
button_font = pygame.font.Font(None, 40)

# Game states
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self, surface):
        # Change color if hovered
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border
        
        # Draw text
        text_surface = button_font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.rect.collidepoint(mouse_pos) and mouse_clicked

# Create start button
start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60, "START", BLUE, DARK_BLUE)

# Main game state
current_state = GAME_STATE_START

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
            current_state = GAME_STATE_PLAYING
    
    # Draw
    screen.fill(WHITE)
    
    if current_state == GAME_STATE_START:
        # Draw start screen
        title_text = title_font.render("MY GAME", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)
        
        start_button.draw(screen)
    
    elif current_state == GAME_STATE_PLAYING:
        # Draw game content
        game_text = title_font.render("Game Started!", True, BLACK)
        game_rect = game_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_text, game_rect)
    
    pygame.display.flip()

pygame.quit()
sys.exit()

