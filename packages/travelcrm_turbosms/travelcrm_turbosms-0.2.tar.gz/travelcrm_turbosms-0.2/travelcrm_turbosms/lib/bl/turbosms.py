# -*coding: utf-8-*-

from travelcrm.lib.utils.resources_utils import get_resource_settings_by_resource_cls

from ...resources.turbosms import TurbosmsResource


def get_settings():
    return get_resource_settings_by_resource_cls(TurbosmsResource)
