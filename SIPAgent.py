import pjsua as pj
from AccountCallback import AccountCallback
from CallCallback import CallCallback
import DoorStation
import logging

logger = logging.getLogger('SIPAgent')

# Logging callback
def log_cb(level, str, len):
    logger.debug('pjsip:'+level)

class SIPAgent :
    door_station = None
    cfg = {}
    account=None
    ui = None
    def __init__(self,door_station,cfg,log_level = 3):
        self.door_station = door_station
        self.cfg = cfg
        self.current_call = None
        self.lib = pj.Lib()
        self.lib.init(log_cfg = pj.LogConfig(level=log_level, callback=log_cb))
        self.log_sound_devices()
        if(cfg['devices']):
            self.lib.set_snd_dev(cfg['devices']['capture'],cfg['devices']['playback'])
            self.log_sound_devices()
        self.transport = self.lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(self.cfg['local_sip_port']))
        self.lib.start()

    def log_sound_devices(self):
        logger.info("** SOUND_DEVICE LIST **")
        cdev, pdev = self.lib.get_snd_dev()
        logger.info("** current : capture %s/ play %s**"%(cdev,pdev))
        for index, sound_device_info in enumerate(self.lib.enum_snd_dev()):
            direction = ""
            if index==cdev or index == pdev:
                direction = direction + " * "
            else:
                direction = direction + "   "
            if sound_device_info.input_channels:
                direction = direction + "IN "
            if sound_device_info.output_channels:
                direction = direction + "OUT"
            logger.info("DEVICE : %s %s %s"%(index, direction, sound_device_info.name))
        logger.info("END DEVICE LIST")

    def start(self):
        try:
            logger.info("Listening on %s:%s"%(self.transport.info().host, self.transport.info().port))
            self.door_station.notify(DoorStation.NOTIFICATION_SIP_START)
            self.account = self.lib.create_account(pj.AccountConfig(self.cfg['registrar'],self.cfg['username'],self.cfg['password']))

            acc_cb = AccountCallback(self.account,self)
            self.account.set_callback(acc_cb)
            acc_cb.wait()

            logger.info("Listening on %s:%s"%(self.transport.info().host, self.transport.info().port))
            logger.info("Registration complete, status=%s (%s) sip: %s:%s"%( \
                self.account.info().reg_status, \
                self.account.info().reg_reason, \
                self.transport.info().host, \
                str(self.transport.info().port)))
            self.door_station.notify(DoorStation.NOTIFICATION_SIP_AGENT_OK)
            return self.account
        except pj.Error, e:
            logger.error("Exception 0: " + str(e))
            self.lib.destroy()

    def make_call(self, uri):
        logger.ingo("Making call to %s"%(uri))
        if self.current_call:
            self.door_station.notify(DoorStation.NOTIFICATION_FORBIDDEN_DOUBLE_CALL)
            return "busy"
        try:
            self.current_call = self.account.make_call(uri, cb=CallCallback(self))
            self.door_station.notify(DoorStation.NOTIFICATION_CALL_INITIATED)
        except pj.Error, e:
            logger.error("Exception 1: " + str(e))
            self.door_station.notify(DoorStation.NOTIFICATION_DISCONNECTED)
        return "ok"
