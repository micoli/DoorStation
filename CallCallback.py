import pjsua as pj
import DoorStation

class CallCallback(pj.CallCallback):
    def __init__(self, sip_agent, call=None):
        pj.CallCallback.__init__(self, call)
        self.sip_agent = sip_agent

    # Notification when call state has changed
    def on_state(self):
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            self.sip_agent.current_call = None
            print 'Current call is', self.sip_agent.current_call
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
