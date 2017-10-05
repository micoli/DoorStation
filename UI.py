import time
from SIPAgent import SIPAgent
from threading import Thread
import DoorStation
from RearmableTimer import RearmableTimer
import logging
from menu import menu
import pygame
import ScreenSaver

UI_STATE_BOOTING = 0
UI_STATE_CONTACT = 1
UI_STATE_CONFIRM_CALL = 2
UI_STATE_CALLING = 3
UI_STATE_INCALL = 4

logger = logging.getLogger('UI')

class UI(Thread):
    bus = None
    contacts = []
    line = 0
    lines= [0,1]
    door_station = None
    state = UI_STATE_BOOTING

    def __init__(self,door_station,Surface,bus,cfg,contacts):
        Thread.__init__(self)
        self.Surface = Surface
        self.bus = bus
        self.rearmableTimer = RearmableTimer(self.light_shutdown)
        self.rearmableTimer.setCounterCallback(self.light_on)
        self.rearmableTimer.run(1)
        self.contacts = contacts
        self.door_station = door_station
        self.door_station.notify(DoorStation.NOTIFICATION_UI_OK)
            
        self.Items = [(contact['name'],k,"button") for k,contact in enumerate(self.contacts)]


        self.contactIndex = 0
        self.displayMode = "contactsList"
        #displayMode = "screensaver"
        self.foreverLoop = True
        
        self.bus.subscribe('gui.menu', self.menuCallback)
        
        font = pygame.font.Font("mksanstallx.ttf",12)
        frontColor = (255, 255, 0)
        halfColor = (200, 200, 0)
        disabledColor = (155, 155, 0)
        
        self.screens={}
        self.screens["contactsList"] = menu(self.Surface, "contactsList", self.bus, self.Items, 10, 180, 10,  30, 50, 300, font, focus=self.contactIndex, frontcolor=frontColor, halfcolor=halfColor, disabledcolor=disabledColor)
        self.screens["callConfirmation"] = menu(self.Surface, "callConfirmation" ,self.bus , [('Appeler','call','button'),('Retour','cancel','button')], 140, 180, 100, 30, 50, 150, font,frontcolor=frontColor,halfcolor=halfColor,disabledcolor=disabledColor,additionalFunc = self.contactDisplay)
        self.screens["call"] = menu(self.Surface,'call', self.bus, [('Retour','cancel','button')], 140, 180, 150, 30, 50, 150, font,frontcolor=frontColor,halfcolor=halfColor,disabledcolor=disabledColor,additionalFunc = self.contactDisplay)
        self.screens["screenSaver"] = ScreenSaver.ScreenSaver(self.Surface,10,6)

    def contactDisplay(self):
        bigFont = pygame.font.Font("mksanstallx.ttf",24)
        self.Surface.blit(bigFont.render(self.contact[0], True, (200, 200, 0)),(15, 40),None)
    
    def blit_text(self,text, pos, font, justif=0,color=pygame.Color('black')):
        x, y = pos
        for line in text.splitlines():
            y = y-font.render(line,0,color).get_height()/2
            
        for line in text.splitlines():
            word_surface = font.render(line,0,color)
            word_width, word_height = word_surface.get_size()
            if justif==0:
                offsetx = word_width
            elif justif==1:
                offsetx = word_width/2
            elif justif==2:
                offsetx = 0
            self.Surface.blit(word_surface, (x-offsetx, y))
            y += word_height  # Start on new row.
        
        
    def setScreen(self,screenName):
        self.displayMode=screenName
        self.screens[self.displayMode].needToUpdate=True
        
    def menuCallback(self,bus,menuName,eventType,item=None,data=None,idx=0):
        if menuName == "contactsList":
            if eventType == "exit" or eventType == "cancel":
                self.foreverLoop = False
            elif eventType == "select" :   
                self.contactIndex = idx
                self.contact = self.Items[idx]
                self.setScreen("callConfirmation")
                self.screens["callConfirmation"].focus=0
                
        if menuName == "callConfirmation":
            if eventType == "select" and item[1] == "call":
                self.setScreen("call")
            else: 
                self.setScreen("contactsList")
    
        if menuName == "call":
            self.setScreen("contactsList")
        
    def lcd_backlightoff(self):
        pass
    
    def lcd_toggle_enable(self, bits):
        pass

    def light_on(self,cnt):
        pass
        #self.print_at("light on %d    " % (cnt),30,1)
        
    def light_shutdown(self):
        #self.print_at("light off      " ,30,1)
        if self.bus != None:
            self.lcd_backlightoff()
        
    def m(self,n):
        return (n)%len(self.contacts)

    def set_state(self,state):
        self.state = state

    def display(self,a1=None,a2=None):
        if self.state == UI_STATE_BOOTING:
            pass
        elif self.state == UI_STATE_CONTACT:
            pass
        elif self.state == UI_STATE_CONFIRM_CALL:
            pass
        elif self.state == UI_STATE_CALLING:
            pass
        elif self.state == UI_STATE_INCALL:
            pass

    def run(self):
        self.setScreen("contactsList")
        while self.foreverLoop:
            print "e"
            pygame.time.Clock().tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.bus.publish('gui.global',when=self.displayMode,eventType=pygame.QUIT)
                elif event.type == pygame.KEYDOWN:
                    self.bus.publish('gui.key',when=self.displayMode,eventKey=event.key)
                       
            self.screens[self.displayMode].run()

    '''def cmd_up(self):
        if (self.state == UI_STATE_CONFIRM_CALL | self.state == UI_STATE_INCALL):
            self.state = UI_STATE_CONTACT
        else:
            self.state = UI_STATE_CONTACT
            self.line = self.line-1
            if (self.line < self.lines[0]):
                self.lines[0]=self.m(self.lines[0]-1)
                self.lines[1]=self.m(self.lines[1]-1)
            self.line = self.m(self.line)
        self.display()

    def cmd_down(self):
        if (self.state == UI_STATE_CONFIRM_CALL | self.state == UI_STATE_INCALL):
            self.state = UI_STATE_CONTACT
        else:
            self.state = UI_STATE_CONTACT
            self.line = self.line+1
            if (self.line > self.lines[1]):
                self.lines[0]=self.m(self.lines[0]+1)
                self.lines[1]=self.m(self.lines[1]+1)
            self.line = self.m(self.line)
        self.display()

    def cmd_enter(self):
        if self.state == UI_STATE_CONTACT:
            self.set_state (UI_STATE_CONFIRM_CALL)
            self.display('',self.contacts[self.line]['name'])
        elif self.state == UI_STATE_CONFIRM_CALL:
            self.door_station.notify(DoorStation.NOTIFICATION_CALL_REQUESTED,self.contacts[self.line])
            self.display('',self.contacts[self.line]['name'])

    def cmd_exit(self):
        self.door_station.notify(DoorStation.NOTIFICATION_EXIT_REQUESTED)
'''