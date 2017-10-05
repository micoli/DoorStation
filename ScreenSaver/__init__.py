from Ball import Ball
import pygame
class ScreenSaver:
    def __init__ (self, Surface,ballNumber,ballRadius):
        self.balls=[]
        self.Surface = Surface
        screen_rect = Surface.get_rect()
        for i in range(0,ballNumber):
            self.balls.append(Ball(screen_rect,ballRadius))
    def run(self):
        self.Surface.fill((0,0,0))
        for i in range(0,10):
            self.balls[i].move()
            pygame.draw.circle(self.Surface, pygame.Color("blue"), (int(self.balls[i].x),int(self.balls[i].y)), self.balls[i].radius, 0)
        #blit_text(self.Surface,"\n".join(title).replace('HH:II',time.strftime("%H:%M")),  (screen_rect.width/2, screen_rect.height/2), largeFont,1,frontColor)
        pygame.display.update()
