import pjsua as pj
import DoorStation
import logging

logger = logging.getLogger('SIPAgent')

class CallCallback(pj.CallCallback):
    def __init__(self, sip_agent, call=None):
        pj.CallCallback.__init__(self, call)
        self.sip_agent = sip_agent

    # Notification when call state has changed
    def on_state(self):
        logger.info("Call with %s is %s, ladst code = %s (%s)"%(self.call.info().remote_uri, self.call.info().state_text, self.call.info().last_code, self.call.info().last_reason))

        if self.call.info().state == pj.CallState.DISCONNECTED:
            self.sip_agent.current_call = None
            logger.info('Current call is %s'%(self.sip_agent.current_call))
            self.sip_agent.door_station.notify(DoorStation.NOTIFICATION_DISCONNECTED)

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            self.sip_agent.door_station.notify(DoorStation.NOTIFICATION_MEDIA_ACTIVE)
        else:
            self.sip_agent.door_station.notify(DoorStation.NOTIFICATION_MEDIA_INACTIVE)

    def on_dtmf_digit(self, digits):
        self.sip_agent.door_station.notify(DoorStation.NOTIFICATION_DTMF)
