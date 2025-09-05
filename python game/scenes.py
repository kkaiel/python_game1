import pygame
import os
from config import *
from assets import CHARACTERS, BACKGROUNDS

# --- Helper Functions & Classes ---

def draw_text(surface, text, font, color, rect, aa=True):
    """Draws text on a surface, wrapping it if necessary."""
    y = rect.top
    line_spacing = -2
    font_height = font.size("Tg")[1]

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

    return text

# --- Scene Base Class ---

class Scene:
    def __init__(self):
        self.next_scene = self
    def process_input(self, events, pressed_keys): raise NotImplementedError
    def update(self): raise NotImplementedError
    def render(self, screen): raise NotImplementedError
    def terminate(self): self.next_scene = None

# --- Story Data ---

STORY_SCRIPT = [
    # 1장: 파도 위의 미묘한 시작
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
    {"bg": "ship", "char": "taehun", "dialogue": "‘이 게임의 정답은... 인간성에 남겨진 흔적뿐이다.’"},

    # 5장: 마지막 인류애 (The Last Humanity)
    {"bg": "ship_deck", "char": "mina", "dialogue": "태훈씨, 결국 남은 건 우리뿐이네요. 제 임무는 모든 것을 관찰하고 기록하는 것이었어요."},
    {"bg": "ship_deck", "char": "mina", "dialogue": "하지만... 마지막 생존자의 ‘인류애(Humanity)’를 시험하라는 숨겨진 조건이 있었죠."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "내... 인류애를 시험하라고?"},
    {"bg": "ship_deck", "char": "mina", "dialogue": "그래요. 이 프로그램은 생존 게임이 아니었어요. 극한 상황에서 인간이 어떤 선택을 하는지 데이터를 수집하는 거대한 실험이었죠."},
    {"bg": "ship_deck", "char": "mina", "dialogue": "이제, 마지막 선택은 당신의 몫이에요."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "이곳에 이 비극의 진실을 쓸 수도, 혹은 모두를 위한 거짓된 영웅담을 쓸 수도 있어요. 당신의 마지막 기록이, 인류애에 대한 당신의 최종 대답이 될 겁니다."},
]

TWIST_TEXT = [
    ("", False),
    ("태훈이 어떤 선택을 하든, 그가 종이에 글을 남기고 병을 봉인한 순간,", False),
    ("민아의 눈이 희미한 빛을 내며 기계적으로 깜빡인다.", False),
    ("", False),
    ("민아: “흥미로운 선택입니다. 데이터 포인트가 기록되었습니다.”", True),
    ("민아: “‘인류애’ 시뮬레이션 버전 7.3을 종료합니다. 참여에 감사드립니다.”", True),
    ("", False),
    ("그 말이 끝나자마자, 태훈의 눈앞에 펼쳐졌던 모든 것이", False),
    ("차가운 디지털 노이즈로 변하며 시야에서 사라진다.", False),
    ("", False),
    ("그는 자신이 단 한 번도 진짜 바다 위에 있었던 적이 없다는 사실을 깨닫는다.", False),
    ("", False),
    ("모든 것이 인류애를 배우기 위한 정교한 시뮬레이션이었던 것이다.", True)
]


# --- Game Scenes ---

class TitleScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.title_font = pygame.font.Font(font_path, 72)
        self.prompt_font = pygame.font.Font(font_path, 30)
        self.title_text = self.title_font.render("Humanity", True, WHITE) # Changed Title
        self.prompt_text = self.prompt_font.render("화면을 클릭하여 시작하세요", True, WHITE)

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.next_scene = StoryScene()

    def update(self):
        pass

    def render(self, screen):
        screen.fill(BLACK)
        title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(self.title_text, title_rect)
        prompt_rect = self.prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(self.prompt_text, prompt_rect)


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
            self.next_scene = ChoiceScene() # Transition to ChoiceScene

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if len(self.text_buffer) < len(self.full_text):
                    self.text_buffer = self.full_text
                else:
                    self.script_index += 1
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
            screen.blit(char_image, (80, SCREEN_HEIGHT - char_image.get_height() - 230))

        s = pygame.Surface((self.text_box_rect.width, self.text_box_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, self.text_box_rect.topleft)
        pygame.draw.rect(screen, WHITE, self.text_box_rect, 2)

        font_to_use = self.dialogue_font
        text_color = WHITE

        if char_name == "action":
            font_to_use = self.action_font
            text_color = (200, 200, 200) # Light grey
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
        
        self.title_surf = self.title_font.render("당신의 선택은?", True, WHITE)
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
                        self.next_scene = TwistScene() # Go to twist scene after any choice
                        return

    def update(self):
        pass

    def render(self, screen):
        screen.blit(BACKGROUNDS['ship_deck'], (0, 0))
        
        # Semi-transparent overlay
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0,0))

        screen.blit(self.title_surf, self.title_rect)

        for i, choice in enumerate(self.choices):
            # Highlight on hover
            if self.choice_rects[i].collidepoint(pygame.mouse.get_pos()):
                text_surf = self.font.render(choice, True, (255, 255, 100)) # Yellow
            else:
                text_surf = self.font.render(choice, True, WHITE)
            screen.blit(text_surf, self.choice_rects[i])


class TwistScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.font = pygame.font.Font(font_path, 28)
        self.title_font = pygame.font.Font(font_path, 36)
        self.scroll_y = SCREEN_HEIGHT
        self.speed = 1

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                self.speed = 5 
        if pressed_keys[pygame.K_ESCAPE]:
            self.terminate()

    def update(self):
        self.scroll_y -= self.speed
        if self.scroll_y < -800: # Adjust this value
            self.terminate()

    def render(self, screen):
        screen.fill(BLACK)
        y_offset = self.scroll_y
        
        for line, is_title in TWIST_TEXT:
            font = self.title_font if is_title else self.font
            color = WHITE if is_title else (200, 200, 200)
            
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += text_rect.height + 15