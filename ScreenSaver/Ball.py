import math
import random
class Ball:
    __slots__ = ('x', 'y', 'v','angle','vx','vy','radius','screen_rect')
    def __init__ (self, screen_rect,radius):
        self.screen_rect = screen_rect
        self.radius=radius
        self.x = random.randint(self.screen_rect.width/4,self.screen_rect.width*3/4)
        self.y = random.randint(self.screen_rect.height/4,self.screen_rect.height*3/4)
        self.v = random.randint(5,10)
        self.angle = random.random()*2*math.pi
        self.initPos()
        
    def initPos(self):
        self.vx = self.v*math.cos(self.angle)
        self.vy = self.v*math.sin(self.angle)
        
    def move(self):
        ''' 1
        4       2
            3'''
        self.x += self.vx
        self.y += self.vy
        prms=(
            ('y', 1  , 2  , self.y<self.radius),
            ('x', 1/2, 3/2, self.x>self.screen_rect.width-self.radius),
            ('y', 0  , 1  , self.y>self.screen_rect.height-self.radius),
            ('x', 3/2, 5/2, self.x<self.radius)
        )
        for p in prms:
            if(p[3]):
                if p[0]=='y':
                    self.vy = -self.vy
                    self.y += self.vy
                else:
                    self.vx = -self.vx
                    self.x += self.vx
                if random.randrange(0,100)>80:
                    self.angle = random.uniform(p[1],p[2])*math.pi
                    self.initPos()
        return
