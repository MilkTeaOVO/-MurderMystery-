import sys
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCRIPT_ROOT = ROOT.parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from scripts.lan_comm import TcpClient
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


class JoinSetupScene:
    def __init__(self, game, room_code=''):
        self.game = game
        self.room_code = room_code
        self.input_text = room_code
        self.hosts = ['ROOM-001', 'ROOM-002', 'ROOM-003']
        self.selected_host = 0
        try:
            pygame.font.init()
        except pygame.error:
            pass
        self.font_title = self._make_font(FONT_SIZE_TITLE)
        self.font_label = self._make_font(FONT_SIZE_LABEL)
        self.font_small = self._make_font(FONT_SIZE_SMALL)
        self.back_button = pygame.Rect(WIDTH - 180, 20, 120, 44)
        self.confirm_button = pygame.Rect(250, 420, 220, 56)
        self.input_rect = pygame.Rect(250, 250, 300, 48)
        self.tcp_client = None

    def _make_font(self, size):
        try:
            return pygame.font.Font(FONT_NAME, size)
        except (FileNotFoundError, pygame.error):
            return pygame.font.Font(None, size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.collidepoint(event.pos):
                if self.game is not None:
                    self.game.go_back()
            elif self.confirm_button.collidepoint(event.pos):
                self.room_code = self.input_text or self.hosts[self.selected_host]
                self._connect_to_host()
            elif self.input_rect.collidepoint(event.pos):
                self.input_text = ''
            else:
                self.selected_host = (self.selected_host + 1) % len(self.hosts)
                self.input_text = self.hosts[self.selected_host]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game is not None:
                    self.game.go_back()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.room_code = self.input_text or self.hosts[self.selected_host]
                self._connect_to_host()
            elif event.unicode and event.unicode.isalnum():
                self.input_text += event.unicode.upper()

    def _connect_to_host(self):
        host = self.room_code.replace('ROOM-', '') if self.room_code.startswith('ROOM-') else self.room_code
        if not host:
            host = '127.0.0.1'
        self.tcp_client = TcpClient(server_host='127.0.0.1', server_port=5000 + int(host[-3:]) % 1000 if host[-3:].isdigit() else 5000)

        def on_connected():
            if self.game is not None:
                self.game.set_status('配对成功，等待开始')
                self.game.set_scene(HostSetupScene(self.game, room_code=self.room_code))

        def on_message(data):
            if self.game is not None:
                self.game.set_status(data.decode('utf-8', errors='ignore'))

        self.tcp_client.on_connected = on_connected
        self.tcp_client.on_message = on_message
        if self.tcp_client.connect(timeout=1.0):
            self.tcp_client.send(self.room_code.encode('utf-8'))
        else:
            if self.game is not None:
                self.game.set_status('连接失败，请确认主机已开启')

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(BG_COLOR)
        title = self.font_title.render('加入游戏', True, TEXT_COLOR)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        subtitle = self.font_small.render('输入房间号或选择可搜索到的主机', True, SUBTITLE_COLOR)
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 140))

        pygame.draw.rect(surface, (80, 80, 90), self.input_rect, border_radius=10)
        input_label = self.font_label.render(self.input_text or '请输入房间号', True, TEXT_COLOR)
        surface.blit(input_label, (self.input_rect.x + 16, self.input_rect.y + 10))

        host_label = self.font_small.render('可搜索到的主机:', True, SUBTITLE_COLOR)
        surface.blit(host_label, (250, 330))
        for index, host in enumerate(self.hosts):
            rect = pygame.Rect(250 + index * 120, 370, 100, 38)
            color = BUTTON_COLOR if index == self.selected_host else (90, 90, 110)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            text = self.font_small.render(host, True, BUTTON_TEXT_COLOR)
            surface.blit(text, (rect.x + 10, rect.y + 8))

        pygame.draw.rect(surface, BUTTON_COLOR, self.confirm_button, border_radius=10)
        confirm_label = self.font_label.render('确定配对', True, BUTTON_TEXT_COLOR)
        surface.blit(confirm_label, (self.confirm_button.x + 54, self.confirm_button.y + 12))

        pygame.draw.rect(surface, (90, 90, 110), self.back_button, border_radius=10)
        back_label = self.font_small.render('返回', True, BUTTON_TEXT_COLOR)
        surface.blit(back_label, (self.back_button.x + 38, self.back_button.y + 12))
