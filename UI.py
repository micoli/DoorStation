import sys
from SIPAgent import SIPAgent
from threading import Thread
import time

## http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2

class UI(Thread):
	contacts = []
	line = 0
	lines= [0,1]
	door_station = None

	def __init__(self,door_station,contacts):
		Thread.__init__(self)
		self.contacts = contacts
		self.door_station = door_station
		self.door_station.notify('ui_ok')

	def m(self,n):
		return (n)%len(self.contacts)

	def display(self):
		l1 = self.lines[0]
		l2 = self.lines[1]
		print "------------------"
		if(self.lines[0]==self.line):
			print "|[%2d] %11s|"%(l1+1,self.contacts[l1]['name'])
			print "| %2d  %11s|"%(l2+1,self.contacts[l2]['name'])
		else:
			print "| %2d  %11s|"%(l1+1,self.contacts[l1]['name'])
			print "|[%2d] %11s|"%(l2+1,self.contacts[l2]['name'])
		print "------------------"

	def run(self):
		running = True
		while running:
			cmd = sys.stdin.readline().rstrip("\r\n")
			if cmd=="u":
				self.line = self.line-1
				if(self.line<self.lines[0]):
					self.lines[0]=self.m(self.lines[0]-1)
					self.lines[1]=self.m(self.lines[1]-1)
				self.line = self.m(self.line)
			elif cmd=="d":
				self.line = self.line+1
				if(self.line>self.lines[1]):
					self.lines[0]=self.m(self.lines[0]+1)
					self.lines[1]=self.m(self.lines[1]+1)
				self.line = self.m(self.line)
			elif cmd=="":
				self.door_station.notify('call_requested',self.contacts[self.line])
				print ">> enter"
			elif cmd=="x":
				running = False
				self.door_station.notify('exit_requested')
			self.display()
			time.sleep(0.1)

