import pygame


class BaseScene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class ExampleScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.t = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.running = False

    def update(self, dt):
        self.t += dt

    def draw(self, surface):
        text = self.font.render(f'Hello Pygame ({int(self.t)}s)', True, (200, 200, 200))
        rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text, rect)
