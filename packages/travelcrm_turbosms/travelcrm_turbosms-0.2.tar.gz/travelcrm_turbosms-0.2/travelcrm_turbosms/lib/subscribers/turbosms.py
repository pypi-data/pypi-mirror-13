#-*-coding:utf-8-*-

from pyramid.events import subscriber

from travelcrm.lib.events.leads import (
    LeadCreated, LeadStatusChanged
)
from travelcrm.lib.utils.common_utils import translate as _
 
from ...lib.scheduler.turbosms import schedule_send_message


@subscriber(LeadCreated)
def lead_created(event):
    message = _(u'Enquiry status is %s.' % event.lead.status)
    schedule_send_message(event.lead.customer.id, message)


@subscriber(LeadStatusChanged)
def lead_status_changed(event):
    message = _(u'Enquiry status is %s now.' % event.lead.status)
    schedule_send_message(event.lead.customer.id, message)
