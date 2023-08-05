# -*-coding: utf-8-*-

import logging

from pyramid.view import view_config, view_defaults

from travelcrm.views import BaseView

from travelcrm.lib.utils.common_utils import translate as _
from travelcrm.lib.utils.resources_utils import get_resource_type_by_resource

from ..forms.turbosms import TurbosmsSettingsForm


log = logging.getLogger(__name__)


@view_defaults(
    context='..resources.turbosms.TurbosmsResource',
)
class TurbosmsView(BaseView):

    @view_config(
        name='settings',
        request_method='GET',
        renderer='travelcrm_turbosms:templates/settings.mako',
        permission='settings',
    )
    def settings(self):
        rt = get_resource_type_by_resource(self.context)
        return {
            'title': self._get_title(_(u'Settings')),
            'rt': rt,
        }

    @view_config(
        name='settings',
        request_method='POST',
        renderer='json',
        permission='settings',
    )
    def _settings(self):
        form = TurbosmsSettingsForm(self.request)
        if form.validate():
            form.submit()
            return {'success_message': _(u'Saved')}
        else:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': form.errors
            }
