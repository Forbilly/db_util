


# -*- encoding: utf-8 -*-

__author__ = "Silva"

import os
from .base import lazy_property
from .init_settings import setting

# 初始化配置文件
os.environ.setdefault('SETTINGS_MODULE', 'db_util.config')

# 统一需要被调用的懒加载对象
# db object
db = lazy_property('app.db')
# dbms object
dbms = lazy_property('app.dbms')
# queue object
queue = lazy_property('app.db')


