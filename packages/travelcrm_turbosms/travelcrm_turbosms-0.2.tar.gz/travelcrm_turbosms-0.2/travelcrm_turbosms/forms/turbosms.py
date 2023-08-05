# -*-coding: utf-8 -*-

import colander

from travelcrm.forms import BaseForm
from travelcrm.lib.utils.resources_utils import get_resource_type_by_resource

from ..resources.turbosms import TurbosmsResource



class _SettingsSchema(colander.Schema):
    username = colander.SchemaNode(
        colander.String(),
    )
    password = colander.SchemaNode(
        colander.String(),
    )
    default_sender = colander.SchemaNode(
        colander.String(),
    )


class TurbosmsSettingsForm(BaseForm):
    _schema = _SettingsSchema

    def submit(self):
        context = TurbosmsResource(self.request)
        rt = get_resource_type_by_resource(context)
        rt.settings = {
            'username': self._controls.get('username'),
            'password': self._controls.get('password'),
            'default_sender': self._controls.get('default_sender'),
        }
