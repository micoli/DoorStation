import sys,os
from SIPAgent import SIPAgent
from UI import UI

class DoorStation:
    sip_agent = None
    ui = None

    def init_sip_agent(self,cfg,log_level):
        self.sip_agent = SIPAgent(self,cfg,log_level)
        self.sip_agent.start()
        return self.sip_agent

    def get_sip_agent(self):
        return self.sip_agent

    def init_ui(self,contacts):
        self.ui = UI(self,contacts)
        self.ui.start()
        return self.ui

    def get_ui(self):
        return self.ui

    def notify(self,notification,args=None):
    	print "notification %s [%s]"%(notification,repr(args))
    	if notification == 'exit_requested':
    		os._exit(1)
