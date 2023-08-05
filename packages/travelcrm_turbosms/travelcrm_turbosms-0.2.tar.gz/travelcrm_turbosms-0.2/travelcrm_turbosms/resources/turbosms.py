# -*-coding: utf-8 -*-

from zope.interface import implementer

from travelcrm.interfaces import (
    IResourceType,
)
from travelcrm.resources import (
    ResourceTypeBase,
)
from travelcrm.lib.utils.common_utils import translate as _


@implementer(IResourceType)
class TurbosmsResource(ResourceTypeBase):

    __name__ = 'turbosms'


    @property
    def allowed_permisions(self):
        return [
            ('settings', _(u'settings')),
        ]

    @property
    def allowed_settings(self):
        return True
