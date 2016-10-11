import time
from SIPAgent import SIPAgent
from threading import Thread
import DoorStation
from RearmableTimer import RearmableTimer
import readchar
import time

UI_STATE_BOOTING = 0
UI_STATE_CONTACT = 1
UI_STATE_CONFIRM_CALL = 2
UI_STATE_CALLING = 3
UI_STATE_INCALL = 4

# Define some device parameters
I2C_ADDR  = 0x3F # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT_ON  = 0x08  # On
LCD_BACKLIGHT_OFF = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005


class UI(Thread):
    bus = None
    contacts = []
    line = 0
    lines= [0,1]
    door_station = None
    state = UI_STATE_BOOTING

    def __init__(self,door_station,contacts):
        Thread.__init__(self)
        self.rearmableTimer = RearmableTimer(self.light_shutdown)
        self.rearmableTimer.setCounterCallback(self.light_on)
        self.contacts = contacts
        self.door_station = door_station
        self.door_station.notify(DoorStation.NOTIFICATION_UI_OK)
        #self.lcd_init()
        #self.gpio_init()
        self.print_at(' '+'-'*16+' '+' '*60,1,1)
        self.print_at('|'+' '*16+'|'+' '*60,1,2)
        self.print_at('|'+' '*16+'|'+' '*60,1,3)
        self.print_at(' '+'-'*16+' '+' '*60,1,4)
        
    def lcd_init(self):
        import smbus
        self.bus = smbus.SMBus(1) # Rev 2 Pi uses 1
        # Initialise display
        self.lcd_byte(0x33,LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32,LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01,LCD_CMD) # 000001 Clear display
        time.sleep(E_DELAY)
        self.lcd_backlightoff()
        
    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT_ON
        bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT_ON
        # High bits
        self.bus.write_byte(I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)
        # Low bits
        self.bus.write_byte(I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)
    
    
    def lcd_backlightoff(self):
        mode = LCD_CMD
        bits = 0x01
        
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT_OFF
        bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT_OFF
        
        # High bits
        self.bus.write_byte(I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)
        
        # Low bits
        self.bus.write_byte(I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)
    
    def lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(E_DELAY)
        self.bus.write_byte(I2C_ADDR, (bits | ENABLE))
        time.sleep(E_PULSE)
        self.bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
        time.sleep(E_DELAY)

    def gpio_init(self):
        import RPi.GPIO as GPIO
        # Initialise display
        GPIO.setmode(GPIO.BCM)

        self.gpio_init_button(GPIO, 17, self.gpio_cmd_up)
        self.gpio_init_button(GPIO, 22, self.gpio_cmd_down) 
        self.gpio_init_button(GPIO,  4, self.gpio_cmd_enter)

    def gpio_cmd_up(self,channel):
        self.cmd_up()

    def gpio_cmd_down(self,channel):
        self.cmd_down()

    def gpio_cmd_enter(self,channel):
        self.cmd_enter()
        
    def gpio_init_button(self,GPIO, pin, callback):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=300)

    def light_on(self,cnt):
        self.print_at("light on %d    " % (cnt),30,1)
        
    def light_shutdown(self):
        self.print_at("light off      " ,30,1)
        if self.bus != None:
            self.lcd_backlightoff()
        
    def m(self,n):
        return (n)%len(self.contacts)

    def set_state(self,state):
        self.state = state

    
    def print_at(self,stri, x=1, y=1):
        print "\033[%d;%df%s\033[%d;%df%s" % (y,x," "*16,y,x,stri)
        
    def display_string(self, message,line):
        self.print_at(' '+'-'*16+' ',1,1)
        self.print_at(' '+'-'*16+' ',1,4)
        if line == LCD_LINE_1:
            self.print_at(message,2,2)
        else:
            self.print_at(message,2,3)
            
        if self.bus != None:
            # Send string to display
            message = message.ljust(LCD_WIDTH," ")
            self.lcd_byte(line, LCD_CMD)
            for i in range(LCD_WIDTH):
                self.lcd_byte(ord(message[i]),LCD_CHR)

    def display(self,a1=None,a2=None):
        if self.state == UI_STATE_BOOTING:
            self.display_string("****  BOOT  ****" ,LCD_LINE_1)
            self.display_string("****************" ,LCD_LINE_2)
            pass

        elif self.state == UI_STATE_CONTACT:
            l1 = self.lines[0]
            l2 = self.lines[1]
            if (self.lines[0]==self.line):
                self.display_string("[%2d] %-11.11s" % (l1+1,self.contacts[l1]['name']) ,LCD_LINE_1)
                self.display_string(" %2d  %-11.11s" % (l2+1,self.contacts[l2]['name']) ,LCD_LINE_2)
            else:
                self.display_string(" %2d  %-11.11s" % (l1+1,self.contacts[l1]['name']) ,LCD_LINE_1)
                self.display_string("[%2d] %-11.11s" % (l2+1,self.contacts[l2]['name']) ,LCD_LINE_2)

        elif self.state == UI_STATE_CONFIRM_CALL:
            self.display_string("Appel ?         " ,LCD_LINE_1)
            self.display_string("%-16.16s" % (a2)  ,LCD_LINE_2)

        elif self.state == UI_STATE_CALLING:
            self.display_string("Appel en cours.." ,LCD_LINE_1)
            self.display_string("%-16.16s" % (a2)  ,LCD_LINE_2)

        elif self.state == UI_STATE_INCALL:
            self.display_string(" %02d:%02d"%(10,20) ,LCD_LINE_1)
            self.display_string("%-16.16s" % (a2)    ,LCD_LINE_2)
            pass

    def run(self):
        running = True
        self.set_state(UI_STATE_CONTACT)
        self.display()
        while running:
            cmd = readchar.readkey()
            print ""
            self.rearmableTimer.run(5)
            if cmd=="u":
                self.cmd_up()
            elif cmd=="d":
                self.cmd_down()
            elif cmd=="":
                self.cmd_enter()
            elif cmd=="x":
                running = False
                self.cmd_exit()
            else:
                self.display()
            time.sleep(0.1)
        GPIO.cleanup()

    def cmd_up(self):
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
