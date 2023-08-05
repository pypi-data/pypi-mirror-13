# -*coding: utf-8-*-

from travelcrm.lib.factories import SMSGatewayFactory

from ...lib.scheduler.turbosms import schedule_send_message


class TurbosmsFactory(SMSGatewayFactory):

    @classmethod
    def send_message(cls, person_id, message):
        schedule_send_message(person_id, message)

