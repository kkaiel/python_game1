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
    # Chapter 1: The Masked Departure
    {"bg": "ship_deck", "char": "taehun", "dialogue": "'최후의 1인에게 모든 것을.' 이것이 우리가 이 배에 탄 이유다. 모두가 웃고 있지만, 그 가면 아래에는 날카로운 발톱이 숨겨져 있겠지."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "나는 '이상적인 리더'를 연기해야 한다. 모두를 이끄는 척, 걱정하는 척. 그래야 그들의 경계를 풀 수 있다."},
    {"bg": "ship_deck", "char": "jihun", "dialogue": "태훈, 준비는 다 됐어? 다들 널 기다리고 있어. 역시 당신이 우리 리더야."},
    {"bg": "ship_deck", "char": "seoyoung", "dialogue": "왠지... 불안해요. 우리, 정말 서로를 믿고 끝까지 갈 수 있을까요?"},
    {"bg": "ship_deck", "char": "taesung", "dialogue": "믿음? 이 배에 그런 순진한 걸 들고 온 녀석도 있나?"},
    {"bg": "ship_deck", "char": "mina", "dialogue": "(수첩에 무언가를 적으며) 신뢰는 가장 강력한 무기이자, 가장 치명적인 약점이죠."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "걱정 마, 서영. 내가 모두를 이끌겠다. 우리는 '하나의 팀'이니까. (마음속: 그래, 마지막 한 명이 남을 때까지는.)"},

    # Chapter 2: The First Gamble
    {"bg": "ship", "char": "taesung", "dialogue": "이 단축 항로는 미친 짓이야. 실패하면 모든 걸 잃어. 돌아가야 해."},
    {"bg": "ship", "char": "taehun", "dialogue": "(마음속: 태성은 나를 무모한 리더로 보이게 해서 내 권위를 실추시키려는 거다. 여기서 물러설 순 없어.)"},
    {"bg": "ship", "char": "taehun", "dialogue": "위험이 큰 만큼, 성공했을 때 얻는 것도 크다. '중간 평가 1위'에게 주어지는 어드밴티지를 잊었나?"},
    {"bg": "ship", "char": "jihun", "dialogue": "하지만 태성의 말도 일리가 있어. 너무 위험해. 다수결로 정하는 게 어때?"},
    {"bg": "ship", "char": "taehun", "dialogue": "(마음속: 지훈은 교묘하게 내 리더십에 흠집을 내고 있다. 중재자인 척하며 자신의 영향력을 키우려는 속셈.)"},
    {"bg": "ship", "char": "seoyoung", "dialogue": "전... 전 무서워요. 그냥 안전하게 가고 싶어요..."},
    {"bg": "ship", "char": "mina", "dialogue": "(데이터를 보여주며) 단축 항로의 성공 확률은 34.5%. 하지만 성공 시, 최종 점수에서 20%의 가산점을 얻습니다. 선택은 각자의 몫이죠."},
    {"bg": "ship", "char": "taehun", "dialogue": "나는 가겠다. 이 위험을 감수하지 않고는 어차피 최후의 1인이 될 수 없어. 따라오지 않을 사람은 지금 말해라."},

    # Chapter 3: The Stolen Secrets
    {"bg": "investigation", "char": "seoyoung", "dialogue": "내... 내 가방이...!! 주최 측이 나눠준 각자의 '비밀 과제'가 들어있었는데, 없어졌어요!"},
    {"bg": "investigation", "char": "taesung", "dialogue": "그걸 왜 이제 와서 말하는 거야! 그리고 왜 날 그런 눈으로 봐? 내가 훔쳤다는 거야?"},
    {"bg": "investigation", "char": "jihun", "dialogue": "진정해, 태성. 하지만 넌 아까부터 계속 서영 씨 주변을 맴돌았잖아."},
    {"bg": "investigation", "char": "taehun", "dialogue": "(마음속: 모두가 서로를 의심하기 시작했다. 혼란스럽지만, 지금이 다른 사람의 속내를 떠볼 기회다.)"},
    {"bg": "investigation", "char": "taehun", "dialogue": "모두 진정해. 내가 한 명씩 들어보겠다. 서영, 마지막으로 가방을 본 게 언제지?"},
    {"bg": "investigation", "char": "seoyoung", "dialogue": "(울먹이며) 아까... 태성 씨랑 잠시 부딪혔을 때... 그 후로 보지 못했어요..."},
    {"bg": "investigation", "char": "taesung", "dialogue": "뭐? 너 지금 날 범인으로 모는 거냐? 그냥 스쳐 지나간 것뿐이야!"},
    {"bg": "investigation", "char": "mina", "dialogue": "(수첩을 넘기며) 흥미롭네요. 두 사람의 동선이 겹친 시간은 3.7초. 무언가를 훔치기엔 너무 짧은 시간 아닌가요?"},
    {"bg": "investigation", "char": "taehun", "dialogue": "(마음속: 민아... 넌 항상 모든 걸 지켜보고 있구나. 널 가장 경계해야 할지도 몰라.)"},

    # Chapter 4: Storm and Sacrifice
    {"bg": "ship", "char": "seoyoung", "dialogue": "(폭풍 속에서 비명을 지르며) 알았어요! 누가 내 과제를 훔쳐 갔는지 알았어! 그 사람은..."},
    {"bg": "ship", "char": "taesung", "dialogue": "시끄러워! 이 상황에 그게 중요해? 밧줄이나 꽉 잡아!"},
    {"bg": "ship", "char": "taehun", "dialogue": "(거대한 파도가 덮치고, 서영이 균형을 잃는다. 그녀의 손이 내게 닿으려 한다. 잡을 것인가, 놓을 것인가...)"},
    {"bg": "ship", "char": "taehun", "dialogue": "(마음속: 그녀를 구하면 혼란만 가중될 뿐이다. 그녀는 너무 많은 것을 알아버렸어. 여기서 탈락해주는 편이... 모두를 위해 좋아.)"},
    {"bg": "ship", "char": "taehun", "dialogue": "서영아! 으... 놓쳤다! 파도가 너무 강했어..."},
    {"bg": "ship", "char": "jihun", "dialogue": "(충격받은 표정으로) 태훈... 너... 방금..."},
    {"bg": "ship", "char": "taesung", "dialogue": "네 놈이 일부러 놓은 거 다 봤어! 이 살인자!"},
    {"bg": "ship", "char": "taehun", "dialogue": "헛소리 마! 이 혼란 속에서 내가 뭘 어떻게 할 수 있었다는 거야!"},
    {"bg": "ship", "char": "jihun", "dialogue": "그만해! 둘 다! 이러다 다 죽어! 태성, 넌 저쪽 밧줄을 잡아! 태훈, 넌 나랑 같이... (그때, 부러진 돛대가 지훈을 덮친다)"},
    {"bg": "ship", "char": "jihun", "dialogue": "(피를 흘리며) 태훈... 민아를... 조심해... 그녀의 수첩에... 모든..."},
    {"bg": "ship", "char": "taesung", "dialogue": "이제 너랑 나, 둘만 남았다. 여기서 끝장을 보자, 태훈!"},
    {"bg": "ship", "char": "taehun", "dialogue": "(태성과의 격투 끝에, 나는 그를 차가운 바다로 밀어 넣었다. 그의 눈에 비친 것은 공포가 아닌, 안도감이었다. 왜지?)"},

    # Chapter 5: The Last Liar
    {"bg": "ship_deck", "char": "mina", "dialogue": "결국 우리 둘만 남았네요, 태훈 씨."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "민아... 지훈이가 마지막에 네 이야기를 했어. 대체 뭘 알고 있는 거지?"},
    {"bg": "ship_deck", "char": "mina", "dialogue": "(수첩을 펼쳐 보이며) 모든 것을요. 서영 씨의 과제를 훔친 건 지훈 씨였어요. 그는 그걸로 태성 씨를 협박해 당신을 리더 자리에서 끌어내리려 했죠."},
    {"bg": "ship_deck", "char": "mina", "dialogue": "서영 씨는 당신이 일부러 손을 놓았고, 태성 씨는 당신과 싸우다 죽은 게 아니라, 지쳐서 스스로 바다에 몸을 던졌죠. 삶에 대한 의지가 없었으니까."},
    {"bg": 'ship_deck', "char": "mina", "dialogue": "그리고 전... 이 모든 사실을 기록했죠. 이제 어떡할까요? 이 기록을 주최 측에 넘기면, 최종 승자는 제가 되겠네요."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "...원하는 게 뭐지?"},
    {"bg": "ship_deck", "char": "mina", "dialogue": "(미소 지으며) 간단해요. 저와 함께 '완벽한 이야기'를 만드는 거예요. 비극적인 사고로 모두를 잃고, 힘을 합쳐 살아남은 두 명의 생존자. 상금은 반반씩 나누는 거죠."},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "(그녀가 내민 독이 든 와인잔을 받으며) ...좋은 제안이군. 우리의 생존을 위하여."},
    {"bg": "ship_deck", "char": "mina", "dialogue": "(잔을 부딪힌다) 생존을 위하여. (와인을 마신다)"},
    {"bg": "ship_deck", "char": "taehun", "dialogue": "(나는 와인을 마시는 척하며 버렸다. 그녀의 잔에만 독이 들어있었으니까. 그녀는... 너무 많은 것을 알고 있었다.)"},
    {"bg": "ship_deck", "char": "mina", "dialogue": "(피를 토하며) ...역시... 당신은... 최악의..."},

    # Chapter 6: The Victor's Chronicle
    {"bg": "bottle", "char": "taehun", "dialogue": "이제... 마지막 이야기를 쓸 시간이다. 진실은 승자의 것이니까."},
    {"bg": "bottle", "char": "taehun", "dialogue": "'항해 일지. 나는 태훈이다. 끔찍한 폭풍 속에서, 나는 사랑하는 동료들을 모두 잃었다.'"},
    {"bg": "bottle", "char": "taehun", "dialogue": "'서영은 모두를 구하기 위해 자신을 희생했고, 지훈은 마지막까지 배를 지키다 쓰러졌다. 태성은 나를 구하고 대신 파도에 휩쓸려갔다.'"},
    {"bg": "bottle", "char": "taehun", "dialogue": "'그리고 민아... 그녀는 절망을 이기지 못하고 스스로... 아, 이 얼마나 비극적인가.'"},
    {"bg": "bottle", "char": "taehun", "dialogue": "'이제 나 혼자 남았다. 그들의 희생을 헛되이 하지 않기 위해서라도, 나는 살아야만 한다. 이 슬픔을 안고서.' (완벽한 이야기다.)"},
]

PSYCHOLOGY_TEXT = [
    ("A Victor's Psychology", True),
    ("승자의 심리학", False),
    ("", False),
    ("1. 자기 합리화 (Self-Justification)", True),
    ("태훈은 자신의 이기적인 선택(동료의 죽음 방관, 살인)을 '어쩔 수 없는 희생' 또는 '모두를 위한 결단'이었다고 스스로를 속입니다. 이는 '나는 선한 사람'이라는 자기 이미지와 잔혹한 현실 사이의 부조화를 견디기 위한 방어기제입니다.", False),
    ("", False),
    ("2. 가스라이팅 (Gaslighting)", True),
    ("최종적으로 그는 '항해 일지'라는 객관적 기록을 조작하여, 타인의 기억과 판단력을 흐리게 만들고 자신의 거짓된 서사를 진실로 만듭니다. 이는 현실을 왜곡하여 타인을 통제하려는 극단적인 심리 지배 기술입니다.", False),
    ("", False),
    ("3. 마키아벨리즘 (Machiavellianism)", True),
    ("태훈은 목적(최종 승리)을 위해 수단과 방법을 가리지 않습니다. 타인을 도구로 여기고, 공감 능력 없이 냉담하게 자신의 이익을 추구하는 모습은 마키아벨리즘 성향의 전형적인 특징을 보여줍니다.", False),
    ("", False),
    ("결국, 진실은 힘을 가진 자에 의해 쓰여지는 '이야기'에 불과한 것일지도 모릅니다.", True)
]


# --- Game Scenes ---

class TitleScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.title_font = pygame.font.Font(font_path, 72)
        self.prompt_font = pygame.font.Font(font_path, 30)
        self.title_text = self.title_font.render("The Last Liar", True, WHITE)
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
            self.next_scene = EndingScene()

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
            # Position all characters to the bottom-left
            screen.blit(char_image, (80, SCREEN_HEIGHT - char_image.get_height() - 230))

        s = pygame.Surface((self.text_box_rect.width, self.text_box_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, self.text_box_rect.topleft)
        pygame.draw.rect(screen, WHITE, self.text_box_rect, 2)

        char_display_name = char_name.capitalize()
        if "(마음속:" in self.full_text or "(He thinks:" in self.full_text:
             char_display_name = "Taehun (Monologue)"

        name_surface = self.name_font.render(char_display_name, True, WHITE)
        screen.blit(name_surface, (self.name_box_rect.x + 10, self.name_box_rect.y))

        text_rect = self.text_box_rect.inflate(-40, -40)
        draw_text(screen, self.text_buffer, self.dialogue_font, WHITE, text_rect)

class EndingScene(Scene):
    def __init__(self):
        super().__init__()
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'D2Coding.ttf')
        self.font = pygame.font.Font(font_path, 24)
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
        # A simple way to end the game after scrolling
        if self.scroll_y < -1000: # Adjust this value based on text length
            self.terminate()

    def render(self, screen):
        screen.fill(BLACK)
        y_offset = self.scroll_y
        
        for line, is_title in PSYCHOLOGY_TEXT:
            font = self.title_font if is_title else self.font
            color = WHITE if is_title else (200, 200, 200)
            
            # Simple text wrapping for long lines
            if font.size(line)[0] > SCREEN_WIDTH - 100:
                words = line.split(' ')
                lines = []
                current_line = ''
                for word in words:
                    if font.size(current_line + ' ' + word)[0] < SCREEN_WIDTH - 100:
                        current_line += ' ' + word
                    else:
                        lines.append(current_line.strip())
                        current_line = word
                lines.append(current_line.strip())
                
                for wrapped_line in lines:
                    text_surface = font.render(wrapped_line, True, color)
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, y_offset))
                    screen.blit(text_surface, text_rect)
                    y_offset += text_rect.height + 10
            else:
                text_surface = font.render(line, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, y_offset))
                screen.blit(text_surface, text_rect)
                y_offset += text_rect.height + 20