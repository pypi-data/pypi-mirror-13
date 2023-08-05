# -*-coding:utf-8-*-

import logging
from datetime import datetime

import pytz
from suds.client import Client

from travelcrm.models import DBSession
from travelcrm.lib.utils.scheduler_utils import gen_task_id, scopped_task
from travelcrm.lib.scheduler import scheduler
from travelcrm.models.person import Person
from travelcrm.models.contact import Contact

from ...lib.bl.turbosms import get_settings


log = logging.getLogger(__name__)

SERVER_URL = 'http://turbosms.in.ua/api/wsdl.html'


@scopped_task
def _send_message(person_id, message):
    contacts = (
        DBSession.query(Contact)
        .join(Person, Contact.person)
        .filter(
            Person.id == person_id,
            Contact.condition_phone(),
            Contact.condition_status_active()
        )
    )
    settings = get_settings()
    client = Client(SERVER_URL)
    client.service.Auth(
        login=settings.get('username'),
        password=settings.get('password')
    )
    for contact in contacts:
        client.service.SendSMS(
            sender=settings.get('default_sender'),
            destination=contact.contact,
            text=message,
        )


def schedule_send_message(person_id, message):
    scheduler.add_job(
        _send_message,
        trigger='date',
        id=gen_task_id(),
        replace_existing=True,
        run_date=datetime.now(pytz.utc),
        args=[person_id, message],
    )
