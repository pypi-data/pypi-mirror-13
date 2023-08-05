#-*-coding:utf-8-*-

from pyramid.config import Configurator


def includeme(config):
    config.add_translation_dirs('travelcrm_turbosms:locale')
    config.scan()
