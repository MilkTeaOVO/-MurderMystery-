import pygame
from .settings import WIDTH, HEIGHT, FPS, TITLE, BG_COLOR
from .home import HomeScene


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = HomeScene(self)
        self.status_text = '请选择你的角色开始配对'

    def set_status(self, text):
        self.status_text = text

    def set_scene(self, scene):
        self.scene = scene

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.scene.handle_event(event)

    def update(self, dt):
        self.scene.update(dt)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.scene.draw(self.screen)
        font = pygame.font.Font(None, 28)
        status = font.render(self.status_text, True, (255, 255, 255))
        self.screen.blit(status, (40, 560))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

    def quit(self):
        pygame.quit()
