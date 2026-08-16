import pygame

class Eventboard_text:
    eventboard_text_list: list[Eventboard_text] = []
    font = pygame.Font("assets/VCR_OSD_MONO_1.001.ttf", 20)
    
    def update_all(game_speed):
        for text in Eventboard_text.eventboard_text_list:
            text.update(game_speed)
    
    def __init__(self, text: str, duration: int = 200, color: str = "#aaaaaa"):
        self.text = text
        self.duration = duration
        self.age = 0
        self.color = color
        
        self.sprite = Eventboard_text.font.render(self.text, False, self.color)
        
        Eventboard_text.eventboard_text_list.append(self)
        
    def update(self, game_speed):
        self.age += 1 * game_speed
        if self.age > self.duration:
            Eventboard_text.eventboard_text_list.remove(self)
            del self