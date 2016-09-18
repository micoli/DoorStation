import sys
import time
from SIPAgent import SIPAgent
from threading import Thread
import DoorStation

## http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
UI_STATE_BOOTING = 0
UI_STATE_CONTACT = 1
UI_STATE_CONFIRM_CALL = 2
UI_STATE_CALLING = 3
UI_STATE_INCALL = 4

class UI(Thread):
    contacts = []
    line = 0
    lines= [0,1]
    door_station = None
    state = UI_STATE_BOOTING

    def __init__(self,door_station,contacts):
        Thread.__init__(self)
        self.contacts = contacts
        self.door_station = door_station
        self.door_station.notify(DoorStation.NOTIFICATION_UI_OK)

    def m(self,n):
        return (n)%len(self.contacts)

    def set_state(self,state):
        self.state = state

    def display(self,a1=None,a2=None):
        print "------------------"
        if self.state == UI_STATE_BOOTING:
            print "|****  BOOT  ****|"
            print "|****************|"
            pass

        elif self.state == UI_STATE_CONTACT:
            l1 = self.lines[0]
            l2 = self.lines[1]
            if(self.lines[0]==self.line):
                print "|[%2d] %-11.11s|"%(l1+1,self.contacts[l1]['name'])
                print "| %2d  %-11.11s|"%(l2+1,self.contacts[l2]['name'])
            else:
                print "| %2d  %-11.11s|"%(l1+1,self.contacts[l1]['name'])
                print "|[%2d] %-11.11s|"%(l2+1,self.contacts[l2]['name'])

        elif self.state == UI_STATE_CONFIRM_CALL:
            print "|Appel ?        |"
            print "|%-16.16s|"%(a2)

        elif self.state == UI_STATE_CALLING:
            print "|Appel en cours..|"
            print "|%-16.16s|"%(a2)

        elif self.state == UI_STATE_INCALL:
            print "| %02d:%02d|"%(10,20)
            print "|%-16.16s|"%(a2)
            pass

        print "------------------"

    def run(self):
        running = True
        self.set_state(UI_STATE_CONTACT)
        self.display()
        while running:
            cmd = sys.stdin.readline().rstrip("\r\n")
            if cmd=="u":
                self.state = UI_STATE_CONTACT
                self.line = self.line-1
                if(self.line<self.lines[0]):
                    self.lines[0]=self.m(self.lines[0]-1)
                    self.lines[1]=self.m(self.lines[1]-1)
                self.line = self.m(self.line)
                self.display()
            elif cmd=="d":
                self.state = UI_STATE_CONTACT
                self.line = self.line+1
                if(self.line>self.lines[1]):
                    self.lines[0]=self.m(self.lines[0]+1)
                    self.lines[1]=self.m(self.lines[1]+1)
                self.line = self.m(self.line)
                self.display()
            elif cmd=="":
                if self.state == UI_STATE_CONTACT:
                    self.set_state (UI_STATE_CONFIRM_CALL)
                    self.display('',self.contacts[self.line]['name'])
                elif self.state == UI_STATE_CONFIRM_CALL:
                    self.door_station.notify(DoorStation.NOTIFICATION_CALL_REQUESTED,self.contacts[self.line])
                print ">> enter"
            elif cmd=="x":
                running = False
                self.door_station.notify(DoorStation.NOTIFICATION_EXIT_REQUESTED)
            else:
                self.display()
            time.sleep(0.1)
