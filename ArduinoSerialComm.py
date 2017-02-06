#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Le Raspbery Pi demande une information à l'Arduino,
# puis il affiche la réponse à l'écran

import serial  # bibliothèque permettant la communication série
import time    # pour le délai d'attente entre les messages
import sys
import threading

class ArduinoSerialComm(threading.Thread):
    running = True
    sercnx = False
    def __init__(self,dev,rate):
        threading.Thread.__init__(self)
        self.sercnx = serial.Serial(dev,rate)

    def send(self,command):
        self.sercnx.write('[[[%s\n'%(command))

    def handle_data(self,data):
        if data[:3] == "]]]":
            print(data[3:].strip('\n'))

    def run(self):
        self.running = True
        while self.running:
            while (self.sercnx.inWaiting()>0):
                reading = self.sercnx.readline()
                self.handle_data(reading)
            time.sleep(0.4)
try:
    #arduinoSerialComm = ArduinoSerialComm('/dev/ttyUSB0', 115200)
    arduinoSerialComm = ArduinoSerialComm('/dev/tty.wchusbserialfa1330', 115200)
    arduinoSerialComm.start()
    while arduinoSerialComm.running:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    arduinoSerialComm.running = False
    print '\n! Received keyboard interrupt, quitting threads.\n'
