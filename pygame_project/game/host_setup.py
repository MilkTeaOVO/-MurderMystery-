import os
import pygame
try:
    import pyperclip
except ImportError:  # pragma: no cover - fallback for environments without pyperclip
    pyperclip = None
from .settings import (
    WIDTH,
    HEIGHT,
    BG_COLOR,
    TEXT_COLOR,
    SUBTITLE_COLOR,
    BUTTON_COLOR,
    BUTTON_TEXT_COLOR,
    FONT_NAME,
    FONT_SIZE_TITLE,
    FONT_SIZE_LABEL,
    FONT_SIZE_SMALL,
)


class HostSetupScene:
    def __init__(self, game, room_code='ROOM-001'):
        self.game = game
        self.room_code = room_code
        try:
            pygame.font.init()
        except pygame.error:
            pass

        def make_font(size):
            try:
                return pygame.font.Font(FONT_NAME, size)
            except (FileNotFoundError, pygame.error):
                return pygame.font.Font(None, size)

        self.font_title = make_font(FONT_SIZE_TITLE)
        self.font_label = make_font(FONT_SIZE_LABEL)
        self.font_small = make_font(FONT_SIZE_SMALL)
        self.copy_button = pygame.Rect(40, 80, 180, 48)
        self.scripts = self._load_scripts()
        self.selected_index = 0

    def _load_scripts(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'scripts.txt')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as fh:
                return [line.strip() for line in fh if line.strip()]
        return ['《密室杀机》']

    def get_selected_script(self):
        if not self.scripts:
            return ''
        return self.scripts[self.selected_index]

    def select_next(self):
        if self.scripts:
            self.selected_index = (self.selected_index + 1) % len(self.scripts)

    def select_previous(self):
        if self.scripts:
            self.selected_index = (self.selected_index - 1) % len(self.scripts)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.copy_button.collidepoint(event.pos):
                try:
                    if pyperclip is not None:
                        pyperclip.copy(self.room_code)
                    if self.game is not None:
                        self.game.set_status('房间号已复制' if pyperclip is not None else '复制功能不可用，请手动复制')
                except Exception:
                    if self.game is not None:
                        self.game.set_status('复制失败，请手动复制')
            elif event.pos[0] > WIDTH // 2:
                self.select_next()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.select_previous()
            elif event.key == pygame.K_DOWN:
                self.select_next()

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(BG_COLOR)
        title = self.font_title.render('房主设置', True, TEXT_COLOR)
        surface.blit(title, (40, 20))

        room_label = self.font_small.render(f'房间号: {self.room_code}', True, SUBTITLE_COLOR)
        surface.blit(room_label, (40, 120))

        pygame.draw.rect(surface, BUTTON_COLOR, self.copy_button, border_radius=10)
        copy_label = self.font_label.render('复制房间号', True, BUTTON_TEXT_COLOR)
        surface.blit(copy_label, (self.copy_button.x + 18, self.copy_button.y + 8))

        left_text = self.font_small.render('请选择要游玩的剧本', True, SUBTITLE_COLOR)
        surface.blit(left_text, (440, 80))

        list_rect = pygame.Rect(440, 130, 300, 260)
        pygame.draw.rect(surface, (50, 50, 60), list_rect, border_radius=10)
        for index, script in enumerate(self.scripts):
            y = 150 + index * 40
            text = self.font_small.render(script, True, TEXT_COLOR)
            surface.blit(text, (460, y))
            if index == self.selected_index:
                pygame.draw.rect(surface, BUTTON_COLOR, pygame.Rect(440, y - 5, 300, 30), 2)

        selected_text = self.font_label.render(f'已选择: {self.get_selected_script()}', True, TEXT_COLOR)
        surface.blit(selected_text, (440, 420))
