# -*- encoding: utf-8 -*-

__author__ = "Silva"

from .libs import rabbitmq, lazy
from . import app as base

def __property(name):
    """初始化获取属性名称"""
    if name == 'app.db':
        obj = base.DbClass()
    elif name == 'app.queue':
        obj = rabbitmq.RabbitMQ()
    elif name == 'app.dbms':
        obj = base.DbSession()
    else:
        obj = None
    return obj

def lazy_property(name):
    """懒加载属性"""
    return lazy.SimpleLazyObject(lambda: __property(name))
