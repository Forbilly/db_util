# -*- encoding: utf-8 -*-

__author__ = "qaulau"

import os
from . import global_settings
from .libs.lazy import LazyObject, empty
from .libs.six import _import_module

# 项目初始化时赋值的系统变量
ENVIRONMENT_VARIABLE = 'SETTINGS_MODULE'

class ConfigureError(Exception):
    pass

class LazySettings(LazyObject):

    def _setup(self, name=None):
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            desc = ("setting %s" % name) if name else "settings"
            raise ConfigureError(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, ENVIRONMENT_VARIABLE))

        self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup(name)
        return getattr(self._wrapped, name)


class Settings(object):
    '''
    懒加载的代理类
    1. 加载当前定义的 global_settings 对象的所有属性
    2. 外部调用时可 可动态加载导入模块 settings_module 的所有属性
    NOTE: 后一次属性会覆盖前一次
    '''
    def __init__(self, settings_module):

        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        self.SETTINGS_MODULE = settings_module

        if isinstance(settings_module, str):
            mod = _import_module(self.SETTINGS_MODULE)
        else:
            mod = settings_module

        for setting in dir(mod):
            if setting.isupper():
                setattr(self, setting, getattr(mod, setting))


setting = LazySettings()