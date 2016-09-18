import pjsua as pj
import threading
from CallCallback import CallCallback

class AccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account, sip_agent):
        pj.AccountCallback.__init__(self, account)
        self.sip_agent = sip_agent

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    # Notification on incoming call
    def on_incoming_call(self, call):
        if self.sip_agent.current_call:
            self.sip_agent.door_app.notify('double_call')
            call.answer(486, "Busy")
            return
        self.sip_agent.door_app.notify('auto_answer')
        self.sip_agent.current_call = call
        self.sip_agent.current_call.set_callback(CallCallback(self.sip_agent.current_call))
        self.sip_agent.current_call.answer(200)