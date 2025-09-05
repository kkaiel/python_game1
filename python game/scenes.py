import pygame
import os
from config import * # Imports all config variables
from assets import CHARACTERS, BACKGROUNDS, PLAYER_FRAMES

# --- Helper Functions & Classes ---

def draw_text(surface, text, font, color, rect, aa=True, wrap=True):
    """Draws text on a surface, wrapping it if necessary."""
    y = rect.top
    line_spacing = -2
    font_height = font.size("Tg")[1]

    if wrap:
        while text:
            i = 1
            if y + font_height > rect.bottom:
                break
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1
            if i < len(text):
                i = text.rfind(" ", 0, i) + 1
            
            image = font.render(text[:i], aa, color)
            surface.blit(image, (rect.left, y))
            y += font_height + line_spacing
            text = text[i:]
    else:
        image = font.render(text, aa, color)
        surface.blit(image, rect)

    return text

# --- Scene Base Class ---

class Scene:
    def __init__(self):
        self.next_scene = self

    def process_input(self, events, pressed_keys): raise NotImplementedError
    def update(self): raise NotImplementedError
    def render(self, screen): raise NotImplementedError
    def terminate(self): self.next_scene = None

    

# --- Story Data (remains the same) ---

STORY_SCRIPT = [
    # 1장: 가면 뒤의 얼굴
    {"bg": "ship_deck", "char": "taehun", "dialogue": "5일 동안 함께 지낼 얼굴들인데, 다들 어딘가 거짓된 미소를 가지고 있다. 나 역시 예외는 아니고."},
    {"bg": "ship_deck", "char": "action", "dialogue": "슬쩍 주머니 속 봉투를 만지작거린다. 평범한 안내문 뒤에는 각자에게 주어진 은밀한 임무가 있었다."},
    {"bg": "ship_deck", "char": "jihun", "dialogue": "태훈아, 오늘 날씨 꽤 괜찮지? 그래도 내일부터는 또 폭풍 친다던데... 좀 불안해."},
    {"bg": "ship_deck", "char": "seoyoung", "dialogue": "전 처음이라 좀 무서워요... 그런데 왜 구명조끼가 딱 5개밖에 없죠?"},
    {"bg": "ship_deck", "char": "mina", "dialogue": "우리 엄마는 참가 전에 유언장 쓰라더라고요. 농담이겠지, 그래도 그런 농담이 왜 자꾸 생각나는지."},
    {"bg": "ship_deck", "char": "taesung", "dialogue": "정말... 좀 이상하네. 이렇게 여유분 없는 준비라니."},
    {"bg": "ship_deck", "char": "action", "dialogue": "뭔가 이상하다. 누구도 자신의 임무를 말하지 않고, 묘하게 서로를 경계하고 있었다."},

    # 2장: 선택의 길목
    {"bg": "ship", "char": "taehun", "dialogue": "우리... 아마 시간 단축하려면 위험을 감수해야 해."},
    {"bg": "ship", "char": "taesung", "dialogue": "진짜 그 길로 갈 생각이야? 어제 일기예보에서 거기 폭풍 몰아친다던데."},
    {"bg": "ship", "char": "jihun", "dialogue": "각자 받은 봉투 내용, 솔직히 다들 신경 쓰고 있잖아. 그냥 놀러 온 게 아니란 거 우리 모두 알고 있지?"},
    {"bg": "ship", "char": "seoyoung", "dialogue": "그, 그런 얘기 하지 마요. 우리 임무는 비밀이라 했잖아요."},
    {"bg": "ship", "char": "mina", "dialogue": "전 다른 사람 행동 관찰이 임무에요. 이미 이 모든 게 연결된다는 생각이 들어요."},
    {"bg": "ship", "char": "action", "dialogue": "서로를 보는 시선이 점점 날카로워진다. 이건 분명 단순한 팀워크 프로그램이 아니다."},
    {"bg": "ship", "char": "taehun", "dialogue": "‘지금 우리에게 필요한 건 정직이 아니라... 살아남는 쪽을 선택하는 용기일지도 모른다.’"},

    # 3장: 의심의 불씨
    {"bg": "ship_deck", "char": "seoyoung", "dialogue": "제... 제 개인 임무서가 없어졌어요. 아무도 안 봤나요?"},
    {"bg": "ship_deck", "char": "taesung", "dialogue": "그런 거 왜 아무 데나 둬? 설마 누가 훔칠 일이 있겠냐?"},
    {"bg": "ship_deck", "char": "jihun", "dialogue": "혹시 네 임무... 우리 중 누군가랑 관련된 거야?"},
    {"bg": "ship_deck", "char": "seoyoung", "dialogue": "...말할 수 없어요. 비밀이잖아요."},
    {"bg": "ship_deck", "char": "mina", "dialogue": "모두의 행동을 기록하고 있는데... 서영씨만 계속 무언가를 숨기네요."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "‘우린 서로를 견제하도록 설계된 거야. 이 바다에선 누구도 완전한 아군이 아니구나.’"},

    # 4장: 폭풍과 갈등
    {"bg": "ship", "char": "seoyoung", "dialogue": "제 임무, 사실... 리더의 판단력을 시험하라는 거였어요. 태훈씨를 관찰하라고 했어요."},
    {"bg": "ship", "char": "taesung", "dialogue": "무슨 소리야? 우리 모두가 서로를 감시하고 있었단 말이야?"},
    {"bg": "ship", "char": "jihun", "dialogue": "지금 그런 거 따질 때가 아니야! 살아남는 게 먼저야!"},
    {"bg": "ship", "char": "action", "dialogue": "그 순간, 배가 기울며 서영이 미끄러졌다. 태훈은 망설임 끝에 손을 내밀었지만 파도가 그녀를 데려갔다."},
    {"bg": "ship", "char": "action", "dialogue": "지훈은 그녀를 잡으려다 돛대에 다쳤고, 태성은 절망 속에서 바다를 바라보다 시야에서 사라졌다."},
    {"bg": "ship", "char": "taehun", "dialogue": "‘결국 모두가 가면을 벗고 자신의 진짜 성향을 드러내는군.’"},

    # 5장: 마지막 인격
    {"bg": "ship_deck", "char": "mina", "dialogue": "태훈씨, 결국 남은 건 우리뿐이네요. 제 임무는 모든 것을 관찰하고 기록하는 것이었어요."},
    {"bg": "ship_deck", "char": "mina", "dialogue": "하지만... 마지막 생존자의 사회적 가면 뒤에 숨겨진 진짜 ‘인격’이 무엇인지 기록하라는 숨겨진 조건이 있었죠."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "내... 진짜 인격을?"},
    {"bg": "ship_deck", "char": "mina", "dialogue": "그래요. 이 프로그램은 생존 게임이 아니었어요. 극한 상황에서 각자의 본래 인격이 어떻게 드러나는지 데이터를 수집하는 거대한 실험이었죠."},
    {"bg": 'ship_deck', "char": "mina", "dialogue": "이제, 당신의 마지막 선택이 당신의 인격을 증명할 겁니다."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "이곳에 묻힌 진실을 기록할 수도, 혹은 모두를 위한 영웅담이라는 마지막 가면을 쓸 수도 있어요. 당신의 선택은 무엇인가요?"},
]

REVEAL_TEXT = [
    ("", False),
    ("태훈이 어떤 선택을 하든, 그가 종이에 글을 남기고 병을 봉인한 순간,", False),
    ("민아의 눈이 희미한 빛을 내며 기계적으로 깜빡인다.", False),
    ("", False),
    ("민아: “흥미로운 데이터입니다. 최종 인격 데이터가 기록되었습니다.”", True),
    ("민아: “‘인격 분석’ 시뮬레이션 버전 8.0을 종료합니다. 참여에 감사드립니다.”", True),
    ("", False),
    ("그 말이 끝나자마자, 태훈의 눈앞에 펼쳐졌던 모든 것이", False),
    ("차가운 디지털 노이즈로 변하며 시야에서 사라진다.", False),
    ("", False),
]

ANALYSIS_TEXT = {
    0: [
        ("당신의 선택: 진실 기록", True),
        ("", False),
        ("당신은 ‘정의 지향적 현실주의자’ 성향을 보입니다.", False),
        ("혼돈 속에서도 진실과 원칙을 지키려는 강한 의지를 가지고 있습니다.", False),
        ("이는 당신의 행동이 개인의 명예나 감정보다는 객관적 사실과 장기적인 결과에 더 큰 가치를 둔다는 것을 의미합니다.", False),
        ("당신은 이 기록이 미래에 더 나은 판단을 위한 교훈이 되기를 바라고 있습니다.", False),
    ],
    1: [
        ("당신의 선택: 비밀 유지", True),
        ("", False),
        ("당신은 ‘공동체 중심의 이타주의자’ 성향을 보입니다.", False),
        ("비극적 진실이 미칠 고통과 혼란을 막고, 희생된 동료들의 명예를 지키려는 마음이 강합니다.", False),
        ("이는 당신이 개인의 신념보다 공동체의 안정과 조화를 우선시하며, 긍정적인 기억을 통해 치유를 도모하려는 깊은 공감 능력을 보여줍니다.", False),
    ],
    2: [
        ("당신의 선택: 모든 가능성 기록", True),
        ("", False),
        ("당신은 ‘신중한 회의주의자’ 또는 ‘다원주의적 관찰자’ 성향을 보입니다.", False),
        ("하나의 관점만이 진실이라 단정하는 것을 경계하며, 모든 가능성을 열어두고 미래의 판단에 맡기고자 합니다.", False),
        ("이는 복잡한 상황을 다각적으로 이해하려는 지적 겸손함과, 섣부른 결정보다 객관적인 정보 전달자로서의 역할을 선택했음을 의미합니다.", False),
    ]
}


# --- Game Scenes ---

class TitleScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.title_font = pygame.font.Font(font_path, 96)
        self.button_font = pygame.font.Font(font_path, 48)
        self.small_button_font = pygame.font.Font(font_path, 28)

        self.title_surf = self.title_font.render("인격", True, WHITE)
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        # Menu Buttons
        self.buttons = {
            "start": {"text": "게임 시작", "rect": pygame.Rect(0, 0, 300, 60)},
            "how_to_play": {"text": "게임 방법", "rect": pygame.Rect(0, 0, 300, 60)},
            "quit": {"text": "게임 종료", "rect": pygame.Rect(0, 0, 300, 60)},
            "analysis": {"text": "엔딩 해석", "rect": pygame.Rect(0, 0, 180, 40)}
        }

        # Position buttons
        self.buttons["start"]["rect"].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        self.buttons["how_to_play"]["rect"].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        self.buttons["quit"]["rect"].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140)
        self.buttons["analysis"]["rect"].topright = (SCREEN_WIDTH - 30, 30)

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.buttons["start"]["rect"].collidepoint(event.pos):
                    self.next_scene = MovementScene() # Go to MovementScene
                elif self.buttons["how_to_play"]["rect"].collidepoint(event.pos):
                    self.next_scene = HowToPlayScene()
                elif self.buttons["analysis"]["rect"].collidepoint(event.pos):
                    self.next_scene = EndingAnalysisScene()
                elif self.buttons["quit"]["rect"].collidepoint(event.pos):
                    self.terminate()

    def update(self):
        pass

    def render(self, screen):
        screen.blit(BACKGROUNDS['ship_deck'], (0, 0))
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0,0))

        screen.blit(self.title_surf, self.title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for key, button in self.buttons.items():
            font = self.small_button_font if key == 'analysis' else self.button_font
            color = (255, 255, 100) if button["rect"].collidepoint(mouse_pos) else WHITE
            text_surf = font.render(button["text"], True, color)
            text_rect = text_surf.get_rect(center=button["rect"].center)
            screen.blit(text_surf, text_rect)
        

class HowToPlayScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.title_font = pygame.font.Font(font_path, 48)
        self.text_font = pygame.font.Font(font_path, 28)
        self.button_font = pygame.font.Font(font_path, 32)

        self.back_button_rect = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 50)

        self.instructions = [
            ("조작 방법", self.title_font, WHITE, SCREEN_HEIGHT // 4),
            ("", self.text_font, WHITE, 0), # Spacer
            ("마우스 좌클릭: 스토리 진행", self.text_font, (200, 200, 200), SCREEN_HEIGHT // 2 - 80),
            ("마우스 우클릭: 이전 스토리로 돌아가기", self.text_font, (200, 200, 200), SCREEN_HEIGHT // 2 - 40),
            ("WASD: 캐릭터 이동", self.text_font, (200, 200, 200), SCREEN_HEIGHT // 2),
        ]

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button_rect.collidepoint(event.pos):
                    self.next_scene = TitleScene()

    def update(self):
        pass

    def render(self, screen):
        screen.fill(BLACK)
        for text, font, color, y_pos in self.instructions:
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(text_surf, text_rect)

        mouse_pos = pygame.mouse.get_pos()
        color = (255, 255, 100) if self.back_button_rect.collidepoint(mouse_pos) else WHITE
        text_surf = self.button_font.render("뒤로 가기", True, color)
        text_rect = text_surf.get_rect(center=self.back_button_rect.center)
        pygame.draw.rect(screen, color, self.back_button_rect, 2)
        screen.blit(text_surf, text_rect)

class EndingAnalysisScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 32)
        self.scroll_y = 0
        self.target_scroll_y = 0

        self.back_button_rect = pygame.Rect(30, 30, 150, 50)

        self.all_analysis_texts = []
        for i in range(len(ANALYSIS_TEXT)):
            self.all_analysis_texts.extend(ANALYSIS_TEXT[i])
            self.all_analysis_texts.append(("", False))

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.back_button_rect.collidepoint(event.pos):
                    self.next_scene = TitleScene()
                elif event.button == 4: self.target_scroll_y += 30
                elif event.button == 5: self.target_scroll_y -= 30

    def update(self):
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * 0.1

    def render(self, screen):
        screen.fill(BLACK)
        y_offset = 40 + self.scroll_y
        
        for line, is_title in self.all_analysis_texts:
            font = self.title_font if is_title else self.font
            color = WHITE if is_title else (200, 200, 200)
            text_rect = pygame.Rect(50, y_offset, SCREEN_WIDTH - 100, 100)
            draw_text(screen, line, font, color, text_rect, wrap=True)
            if font.size(line)[0] > SCREEN_WIDTH - 100:
                num_lines = (font.size(line)[0] // (SCREEN_WIDTH - 100)) + 1
                y_offset += font.get_height() * num_lines + 10
            else:
                y_offset += font.get_height() + 15

        pygame.draw.rect(screen, BLACK, self.back_button_rect)
        mouse_pos = pygame.mouse.get_pos()
        color = (255, 255, 100) if self.back_button_rect.collidepoint(mouse_pos) else WHITE
        text_surf = self.title_font.render("뒤로 가기", True, color)
        text_rect = text_surf.get_rect(center=self.back_button_rect.center)
        pygame.draw.rect(screen, color, self.back_button_rect, 2)
        screen.blit(text_surf, text_rect)

class MovementScene(Scene):
    def __init__(self):
        super().__init__()
        self.player_image = PLAYER_FRAMES["idle"]
        self.player_rect = self.player_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.player_speed = 5
        self.is_moving = False

        self.animation_frames = [PLAYER_FRAMES["walk1"], PLAYER_FRAMES["walk2"]]
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 200 # milliseconds per frame

        # Define the deck area to trigger the story
        self.deck_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 150)

    def process_input(self, events, pressed_keys):
        self.is_moving = False
        new_x, new_y = self.player_rect.x, self.player_rect.y

        if pressed_keys[pygame.K_w]:
            new_y -= self.player_speed
            self.is_moving = True
        if pressed_keys[pygame.K_s]:
            new_y += self.player_speed
            self.is_moving = True
        if pressed_keys[pygame.K_a]:
            new_x -= self.player_speed
            self.is_moving = True
        if pressed_keys[pygame.K_d]:
            new_x += self.player_speed
            self.is_moving = True

        # Clamp player position to screen boundaries
        self.player_rect.x = max(0, min(new_x, SCREEN_WIDTH - self.player_rect.width))
        self.player_rect.y = max(0, min(new_y, SCREEN_HEIGHT - self.player_rect.height))

    def update(self):
        # Animate player
        now = pygame.time.get_ticks()
        if self.is_moving:
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.player_image = self.animation_frames[self.current_frame]
        else:
            self.player_image = PLAYER_FRAMES["idle"]

        # Check for collision with deck
        if self.player_rect.colliderect(self.deck_rect):
            self.next_scene = StoryScene()

    def render(self, screen):
        screen.blit(BACKGROUNDS['startship'], (0, 0))
        
        # Draw the trigger zone for visualization
        s = pygame.Surface((self.deck_rect.width, self.deck_rect.height), pygame.SRCALPHA)
        s.fill((255, 0, 0, 100)) # Semi-transparent red
        screen.blit(s, self.deck_rect.topleft)

        screen.blit(self.player_image, self.player_rect)

class StoryScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.dialogue_font = pygame.font.Font(font_path, 28)
        self.name_font = pygame.font.Font(font_path, 32)
        self.action_font = pygame.font.Font(font_path, 28)
        self.action_font.set_italic(True)
        
        self.script_index = 0
        self.text_buffer = ""
        self.typing_timer = 0
        self.typing_speed = 2

        self.text_box_rect = pygame.Rect(50, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 100, 200)
        self.name_box_rect = pygame.Rect(70, SCREEN_HEIGHT - 220, 200, 40)

        self._load_current_line()

    def _load_current_line(self):
        if self.script_index < len(STORY_SCRIPT):
            self.current_line = STORY_SCRIPT[self.script_index]
            self.full_text = self.current_line["dialogue"]
            self.text_buffer = ""
            self.typing_timer = 0
        else:
            self.next_scene = ChoiceScene()

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left-click to advance
                    if len(self.text_buffer) < len(self.full_text):
                        self.text_buffer = self.full_text
                    else:
                        self.script_index += 1
                        self._load_current_line()
                elif event.button == 3:  # Right-click to go back
                    if self.script_index > 0:
                        self.script_index -= 1
                        self._load_current_line()

    def update(self):
        if self.next_scene != self: return
        if len(self.text_buffer) < len(self.full_text):
            self.typing_timer += 1
            if self.typing_timer >= self.typing_speed:
                self.typing_timer = 0
                self.text_buffer += self.full_text[len(self.text_buffer)]

    def render(self, screen):
        if self.next_scene != self: return

        bg_name = self.current_line["bg"]
        if bg_name in BACKGROUNDS:
            screen.blit(BACKGROUNDS[bg_name], (0, 0))

        char_name = self.current_line["char"]
        if char_name in CHARACTERS:
            char_image = CHARACTERS[char_name]
            pos_x = CHARACTER_POS_X
            pos_y = SCREEN_HEIGHT - char_image.get_height() - CHARACTER_POS_Y_FROM_BOTTOM
            screen.blit(char_image, (pos_x, pos_y))

        s = pygame.Surface((self.text_box_rect.width, self.text_box_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, self.text_box_rect.topleft)
        pygame.draw.rect(screen, WHITE, self.text_box_rect, 2)

        font_to_use = self.dialogue_font
        text_color = WHITE

        if char_name == "action":
            font_to_use = self.action_font
            text_color = (200, 200, 200)
        else:
            char_display_name = char_name.capitalize()
            if "‘" in self.full_text:
                 char_display_name = "Taehun (Monologue)"

            name_surface = self.name_font.render(char_display_name, True, WHITE)
            screen.blit(name_surface, (self.name_box_rect.x + 10, self.name_box_rect.y))

        text_rect = self.text_box_rect.inflate(-40, -40)
        draw_text(screen, self.text_buffer, font_to_use, text_color, text_rect)

class ChoiceScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.font = pygame.font.Font(font_path, 28)
        self.title_font = pygame.font.Font(font_path, 36)
        self.choices = [
            "1. 진실을 써서 유리병에 넣자. 언젠가 누군가 찾을 거야.",
            "2. 우리만의 비밀로 묻어두자. 그들을 영웅으로 기억하게 하자.",
            "3. 둘 다 기록해서, 미래가 판단하게 하자."
        ]
        self.choice_rects = []
        
        self.title_surf = self.title_font.render("당신의 마지막 인격은?", True, WHITE)
        self.title_rect = self.title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))

        y_pos = SCREEN_HEIGHT // 2 - 50
        for choice in self.choices:
            text_surf = self.font.render(choice, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.choice_rects.append(text_rect)
            y_pos += 60

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self.choice_rects):
                    if rect.collidepoint(event.pos):
                        self.next_scene = TwistScene(choice_index=i)
                        return

    def update(self):
        pass

    def render(self, screen):
        screen.blit(BACKGROUNDS['ship_deck'], (0, 0))
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0,0))

        screen.blit(self.title_surf, self.title_rect)

        for i, choice in enumerate(self.choices):
            if self.choice_rects[i].collidepoint(pygame.mouse.get_pos()):
                text_surf = self.font.render(choice, True, (255, 255, 100))
            else:
                text_surf = self.font.render(choice, True, WHITE)
            screen.blit(text_surf, self.choice_rects[i])


class TwistScene(Scene):
    def __init__(self, choice_index):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.font = pygame.font.Font(font_path, 24)
        self.title_font = pygame.font.Font(font_path, 32)
        self.scroll_y = SCREEN_HEIGHT
        self.speed = 1
        self.final_text = REVEAL_TEXT + ANALYSIS_TEXT[choice_index]

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                self.speed = 5 
        if pressed_keys[pygame.K_ESCAPE]:
            self.next_scene = TitleScene()

    def update(self):
        self.scroll_y -= self.speed
        if self.scroll_y < - (len(self.final_text) * 40):
            self.next_scene = TitleScene()

    def render(self, screen):
        screen.fill(BLACK)
        y_offset = self.scroll_y
        
        for line, is_title in self.final_text:
            font = self.title_font if is_title else self.font
            color = WHITE if is_title else (200, 200, 200)
            
            text_rect = pygame.Rect(50, y_offset, SCREEN_WIDTH - 100, 100)
            draw_text(screen, line, font, color, text_rect, wrap=True)
            
            if font.size(line)[0] > SCREEN_WIDTH - 100:
                num_lines = (font.size(line)[0] // (SCREEN_WIDTH - 100)) + 1
                y_offset += font.get_height() * num_lines + 10
            else:
                y_offset += font.get_height() + 15