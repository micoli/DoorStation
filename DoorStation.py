import sys,os
from SIPAgent import SIPAgent
from UI import UI

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
        if notification == NOTIFICATION_EXIT_REQUESTED:
            os._exit(1)
        elif notification == NOTIFICATION_DOUBLE_CALL :
            pass
        elif notification == NOTIFICATION_AUTO_ANSWER :
            pass
        elif notification == NOTIFICATION_DISCONNECTED :
            pass
        elif notification == NOTIFICATION_MEDIA_ACTIVE :
            pass
        elif notification == NOTIFICATION_MEDIA_INACTIVE :
            pass
        elif notification == NOTIFICATION_SIP_START :
            pass
        elif notification == NOTIFICATION_SIP_AGENT_OK :
            pass
        elif notification == NOTIFICATION_FORBIDDEN_DOUBLE_CALL :
            pass
        elif notification == NOTIFICATION_CALL_INITIATED :
            self.ui.set_state(UI.UI_STATE_CALLING)
            self.ui.display("",args)
            pass
        elif notification == NOTIFICATION_UI_OK :
            pass
        elif notification == NOTIFICATION_CALL_REQUESTED :
            pass
        elif notification == NOTIFICATION_EXIT_REQUESTED :
            pass
