import pygame
from .settings import (
    WIDTH,
    HEIGHT,
    BG_COLOR,
    TEXT_COLOR,
    SUBTITLE_COLOR,
    ALT_TEXT_COLOR,
    SUCCESS_TEXT_COLOR,
    BUTTON_COLOR,
    BUTTON_TEXT_COLOR,
    FONT_NAME,
    FONT_SIZE_TITLE,
    FONT_SIZE_LABEL,
    FONT_SIZE_SMALL,
)
from .host_setup import HostSetupScene
from .join_setup import JoinSetupScene


class HomeScene:
    def __init__(self, game):
        self.game = game

        def make_font(size):
            try:
                return pygame.font.Font(FONT_NAME, size)
            except (FileNotFoundError, pygame.error):
                return pygame.font.Font(None, size)

        self.font_title = make_font(FONT_SIZE_TITLE)
        self.font_label = make_font(FONT_SIZE_LABEL)
        self.font_small = make_font(FONT_SIZE_SMALL)
        self.buttons = {}
        self.match_state = {'mode': None, 'room_code': ''}
        self._build_buttons()

    def _build_buttons(self):
        self.buttons['host'] = {
            'rect': pygame.Rect(250, 260, 300, 60),
            'label': '作为主机创建游戏',
        }
        self.buttons['join'] = {
            'rect': pygame.Rect(250, 340, 300, 60),
            'label': '作为成员加入游戏',
        }

    def get_button(self, key):
        return self.buttons.get(key)

    def set_mode(self, mode):
        self.match_state['mode'] = mode
        self.match_state['room_code'] = ''

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, button in self.buttons.items():
                if button['rect'].collidepoint(event.pos):
                    if key == 'host':
                        self.set_mode('host')
                        if self.game is not None:
                            self.game.set_scene(HostSetupScene(self.game, room_code='ROOM-001'))
                    elif key == 'join':
                        self.set_mode('join')
                        if self.game is not None:
                            self.game.set_scene(JoinSetupScene(self.game, room_code=''))
                    break

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(BG_COLOR)
        title = self.font_title.render('剧本杀', True, TEXT_COLOR)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = self.font_small.render('请选择你的身份', True, SUBTITLE_COLOR)
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 170))

        for key, button in self.buttons.items():
            rect = button['rect']
            pygame.draw.rect(surface, BUTTON_COLOR, rect, border_radius=12)
            label = self.font_label.render(button['label'], True, BUTTON_TEXT_COLOR)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)
