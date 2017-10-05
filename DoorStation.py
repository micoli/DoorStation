import sys,os
from SIPAgent import SIPAgent
import UI
#import Webcam
import logging
import requests
import ScreenSaver

NOTIFICATION_DOUBLE_CALL = 'double_call'
NOTIFICATION_AUTO_ANSWER = 'auto_answer'
NOTIFICATION_DISCONNECTED = 'disconnected'
NOTIFICATION_MEDIA_ACTIVE = 'media_active'
NOTIFICATION_MEDIA_INACTIVE = 'media_inactive'
NOTIFICATION_SIP_START = 'sip_start'
NOTIFICATION_SIP_AGENT_OK = 'sip_agent_ok'
NOTIFICATION_FORBIDDEN_DOUBLE_CALL = 'forbidden_double_call'
NOTIFICATION_CALL_INITIATED = 'call_initiated'
NOTIFICATION_UI_OK = 'ui_ok'
NOTIFICATION_CALL_REQUESTED = 'call_requested'
NOTIFICATION_EXIT_REQUESTED = 'exit_requested'
NOTIFICATION_DTMF = 'dtmf'

logger = logging.getLogger('doorStation')

class DoorStation:
    sip_agent = None
    ui = None
    bus = None
    Surface = None
    
    def __init__(self,bus,Surface):
        self.bus = bus
        self.Surface = Surface
        
    def init_sip_agent(self,config,log_level):
        self.sip_agent = SIPAgent(self,config,log_level)
        self.sip_agent.start()
        return self.sip_agent

    def get_sip_agent(self):
        return self.sip_agent

    def init_ui(self,config,contacts):
        self.ui = UI.UI(self,self.Surface,self.bus,config,contacts)
        self.ui.start()
        return self.ui

    def init_webcam(self,config):
        #self.webcam = Webcam.webcam(self,config)
        #self.webcam.start()
        return self.webcam


    def get_ui(self):
        return self.ui

    def notify(self,notification,args=None):
        logger.info("notification %s [%s]"%(notification,repr(args)))
        if notification == NOTIFICATION_EXIT_REQUESTED:
            os._exit(1)
        elif notification == NOTIFICATION_AUTO_ANSWER :
            pass
        elif notification == NOTIFICATION_UI_OK :
            pass
        elif notification == NOTIFICATION_SIP_START :
            pass
        elif notification == NOTIFICATION_SIP_AGENT_OK :
            pass
        elif notification == NOTIFICATION_DTMF :
            pass
        elif notification == NOTIFICATION_DOUBLE_CALL :
            self.ui.set_state(UI.UI_STATE_CONTACT)
            self.ui.display()
            pass
        elif notification == NOTIFICATION_DISCONNECTED :
            self.ui.set_state(UI.UI_STATE_CONTACT)
            self.ui.display()
            pass
        elif notification == NOTIFICATION_MEDIA_ACTIVE :
            self.ui.set_state(UI.UI_STATE_INCALL)
            self.ui.display('',self.ui.contacts[self.ui.line]['name'])
            pass
        elif notification == NOTIFICATION_MEDIA_INACTIVE :
            self.ui.set_state(UI.UI_STATE_CONTACT)
            self.ui.display()
            pass
        elif notification == NOTIFICATION_FORBIDDEN_DOUBLE_CALL :
            pass
        elif notification == NOTIFICATION_CALL_INITIATED :
            self.ui.set_state(UI.UI_STATE_CALLING)
            self.ui.display("",args)
            pass
        elif notification == NOTIFICATION_CALL_REQUESTED :
            requests.get('http://127.0.0.1:8086/call/',params={'uri':args['number']})
            pass
        elif notification == NOTIFICATION_EXIT_REQUESTED :
            pass

    def shutdown(self):
        agent = self.get_sip_agent()
        agent.transport = None
        agent.account.delete()
        agent.account = None
        agent.lib.destroy()
        agent.lib = None
