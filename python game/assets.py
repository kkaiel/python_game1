import pygame
import os
from config import SCREEN_WIDTH, SCREEN_HEIGHT, CHARACTER_TARGET_HEIGHT

# This script is in 'python game', so the assets are in the parent directory ('..')
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

CHARACTERS = {}
BACKGROUNDS = {}
PLAYER_FRAMES = {}

def load_assets():
    """Loads all game images from the parent directory."""
    print("Loading assets...")
    character_files = ['mina.png', 'seoyoung.png', 'jihun.png', 'taesung.png', 'taehun.png']
    background_files = ['ship_deck.png', 'ship.png', 'bottle.png', 'investigation.png', 'startship.png']
    player_files = {
        "idle": "walking1.png",
        "walk1": "walking2.png",
        "walk2": "walking3.png"
    }

    for filename in character_files:
        try:
            name = os.path.splitext(filename)[0]
            path = os.path.join(ASSETS_DIR, filename)
            image = pygame.image.load(path).convert_alpha()

            # Scale character images to a fixed height to ensure they fit on screen
            new_height = CHARACTER_TARGET_HEIGHT
            original_width, original_height = image.get_size()
            if original_height > new_height:
                aspect_ratio = original_width / original_height
                new_width = int(new_height * aspect_ratio)
                scaled_image = pygame.transform.scale(image, (new_width, new_height))
                CHARACTERS[name] = scaled_image
            else:
                CHARACTERS[name] = image
            print(f"Loaded character: {filename}")
        except pygame.error as e:
            print(f'Error loading character "{filename}": {e}')

    for filename in background_files:
        try:
            name = os.path.splitext(filename)[0]
            path = os.path.join(ASSETS_DIR, filename)
            image = pygame.image.load(path).convert()
            # Scale background images to fit the screen size
            scaled_bg = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            BACKGROUNDS[name] = scaled_bg
            print(f"Loaded background: {filename}")
        except pygame.error as e:
            print(f'Error loading background "{filename}": {e}')

    for name, filename in player_files.items():
        try:
            path = os.path.join(ASSETS_DIR, filename)
            image = pygame.image.load(path).convert_alpha()
            # You might want to scale player frames as well, e.g., to a fixed size
            # For now, using original size
            PLAYER_FRAMES[name] = image
            print(f"Loaded player frame: {filename}")
        except pygame.error as e:
            print(f'Error loading player frame "{filename}": {e}')

    print("Asset loading complete.")
