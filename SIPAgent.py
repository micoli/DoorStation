import pjsua as pj
from AccountCallback import AccountCallback
from CallCallback import CallCallback

# Logging callback
def log_cb(level, str, len):
    print str,        

class SIPAgent : 
    door_app = None
    cfg = {}
    account=None
    ui = None
    def __init__(self,door_app,cfg,log_level = 3):
        self.door_app = door_app
        self.cfg = cfg
        self.current_call = None
        self.lib = pj.Lib()
        self.lib.init(log_cfg = pj.LogConfig(level=log_level, callback=log_cb))
        self.transport = self.lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(self.cfg['local_sip_port']))
        self.lib.start()

    def start(self):
        try:
            print "\nListening on", self.transport.info().host, 
            print "port", self.transport.info().port, "\n"

            self.account = self.lib.create_account(pj.AccountConfig(self.cfg['registrar'],self.cfg['username'],self.cfg['passwrd']))

            acc_cb = AccountCallback(self.account,self)
            self.account.set_callback(acc_cb)
            acc_cb.wait()

            print "Registration complete, status=", \
                self.account.info().reg_status, \
                "(",self.account.info().reg_reason,")", \
                "sip:",self.transport.info().host, \
                ":",str(self.transport.info().port) 
            self.door_app.notify('sip_agent_ok')
            return self.account
        except pj.Error, e:
            print "Exception: " + str(e)
            lib.destroy()

    def make_call(self, uri):
        print "Making call to ", uri
        if self.current_call:
            self.door_app.notify('cant_double_call')
            return "busy"
        self.current_call = self.account.make_call(uri, cb=CallCallback(self))
        self.door_app.notify('calling')
        return "ok"