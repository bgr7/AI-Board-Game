#Bugra Baygul 20190705005-072
import pygame

class Button:
    def __init__(self, x, y, width, height, text, highlighted=False, font_size=30, callback=None):
        self.highlighted = highlighted
        self.font_size = font_size
        self.callback = callback
        self.shape = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (150, 150, 150) #I defined all buttons' characteristics
        if self.highlighted:
            self.color = (100, 200, 100)
        self.font = pygame.font.SysFont(None, self.font_size)
        self.text_surf = self.font.render(self.text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(center=self.shape.center)

    def render(self, draw_area):
        pygame.draw.rect(draw_area, self.color, self.shape)
        draw_area.blit(self.text_surf, self.text_rect)

    def click_handler(self, pos):
        return self.shape.collidepoint(pos)

    def ev_handler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.click_handler(event.pos):
                if self.callback:
                    self.callback()
