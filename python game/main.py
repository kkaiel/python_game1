import pygame
import os
from config import *
from scenes import TitleScene
from assets import load_assets, CHARACTERS, BACKGROUNDS # Import asset loaders

def main():
    pygame.init()
    
    # Load and play background music
    music_path = os.path.join(os.path.dirname(__file__), 'assets', 'beethoven-concert-nr3-relaxing-classical-piano-216328.mp3')
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # -1 for infinite loop

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Load all the images
    load_assets()
    pygame.display.set_caption("Story Game")
    clock = pygame.time.Clock()

    active_scene = TitleScene()

    while active_scene is not None:
        # Event handling
        pressed_keys = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                active_scene.terminate()

        # Process scene-specific input
        active_scene.process_input(events, pressed_keys)

        # Update scene
        active_scene.update()

        # Render scene
        active_scene.render(screen)

        # Go to the next scene
        active_scene = active_scene.next_scene

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()