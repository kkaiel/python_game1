import pygame
import os
from config import *
from assets import BACKGROUNDS, CHARACTERS

# --- Helper function for text wrapping ---
def draw_text(surface, text, pos, font, max_width, color=WHITE, italic=False):
    font.set_italic(italic)
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_offset = 0
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (pos[0], pos[1] + y_offset))
        y_offset += font.get_linesize()
    font.set_italic(False) # Reset font style


# --- Base Scene Classes ---
class Scene:
    def __init__(self):
        self.next_scene = self
    
    def process_input(self, events, pressed_keys):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def render(self, screen):
        raise NotImplementedError

    def terminate(self):
        self.next_scene = None

class TitleScene(Scene):
    def __init__(self):
        super().__init__()
        # Use local font for title as well, in case system font is an issue
        try:
            font_path = os.path.join("assets", "D2Coding.ttf")
            self.font = pygame.font.Font(font_path, 50)
        except (pygame.error, FileNotFoundError):
            self.font = pygame.font.Font(None, 50)

        self.title_text = self.font.render("My Story Game", True, BLACK)
        self.title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.prompt_text = self.font.render("Press SPACE to Start", True, BLACK)
        self.prompt_rect = self.prompt_text.get_rect(center=(SCREEN_WIDTH // 2, 400))

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.next_scene = Chapter1Scene()

    def update(self):
        pass

    def render(self, screen):
        screen.fill(WHITE)
        screen.blit(self.title_text, self.title_rect)
        screen.blit(self.prompt_text, self.prompt_rect)


# --- Dialogue Scene Engine ---
class DialogueScene(Scene):
    def __init__(self, script, next_scene_constructor):
        super().__init__()
        self.script = script
        self.script_index = 0
        self.next_scene_constructor = next_scene_constructor

        # Font settings (size reduced)
        font_path = os.path.join("assets", "D2Coding.ttf")
        try:
            self.dialogue_font = pygame.font.Font(font_path, 28) # Smaller
            self.narration_font = pygame.font.Font(font_path, 24) # Smaller
            self.choice_font = pygame.font.Font(font_path, 26) # New font for choices
        except (pygame.error, FileNotFoundError):
            self.dialogue_font = pygame.font.Font(None, 28)
            self.narration_font = pygame.font.Font(None, 24)
            self.choice_font = pygame.font.Font(None, 26)

        # Typewriter effect state
        self.text_speed = 40  # Milliseconds per character
        self.visible_chars = 0
        self.last_char_time = 0
        self.current_dialogue = ""
        self.current_narration = ""

        # Choice state
        self.showing_choices = False
        self.choice_question = ""
        self.choice_options = [] # List of {"text": "...", "next_event_index": ...}

        # Initialize state variables before first use
        self.current_background = None
        self.current_character = None
        
        # Set initial state for the first line
        self._set_new_line()

    def _set_new_line(self):
        """Resets the typewriter effect for the current line in the script."""
        if self.script_index < len(self.script):
            current_event = self.script[self.script_index]
            
            if current_event["type"] == "dialogue":
                self.showing_choices = False
                self.current_background = current_event.get("background", self.current_background)
                self.current_character = current_event.get("character", self.current_character)
                self.current_dialogue = current_event.get("dialogue", "")
                self.current_narration = current_event.get("narration", "")
                self.visible_chars = 0
                self.last_char_time = pygame.time.get_ticks()
            elif current_event["type"] == "choice":
                self.showing_choices = True
                self.choice_question = current_event["question"]
                self.choice_options = current_event["options"]
                self.visible_chars = 0 # No typewriter for choices
                self.current_dialogue = "" # Clear dialogue area
                self.current_narration = "" # Clear narration area
            elif current_event["type"] == "jump":
                self.script_index = current_event["target_index"]
                self._set_new_line() # Immediately process the jumped-to line
        else:
            # End of script, transition to next scene
            self.next_scene = self.next_scene_constructor()
