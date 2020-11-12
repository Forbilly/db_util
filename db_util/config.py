#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'Silva'

import sys
import os
import logging


# APP_ROOT = getattr(sys, '__APP_ROOT__', os.path.split(os.path.realpath(__file__))[0])
# APP_PATH = getattr(sys, '__APP_PATH__', os.path.split(os.path.realpath(__file__))[0])
#

# 队列地址
AMQP_URL = 'amqp://admin:elecfans@192.168.13.61:5672/'

'''
数据库相关
'''
DATABASES = {
    'mysql': ({                             # hqchip
        'user': 'root',
        'passwd': 'root',
        'host': '127.0.0.1',
        'port': 3306,
        'charset': 'utf8',
        'db': 'silva',
        'tablepre': '',  # 表前缀
        'db_fields_cache': False,
        'data_type': 'dict',
    },{                                     # other supplier
        'user': 'tlrobt',
        'passwd': '123456',
        'host': 'db.elecfans.net',
        'port': 3306,
        'charset': 'utf8',
        'tablepre': '',
        'db_fields_cache': False,
        'data_type': 'dict',
    }),
    'mongo':(
        'mongodb://hqjf:aa88OO00@mongodb.elecfans.net/hqchip',
    ),
    'elasticsearch':{
        "host": [
            '192.168.12.21:9200',
        ],
        "index_goods": 'bom_bom,bom_bom_supplier'
    }
}

DB_KEY = {
    0: 'szlcsc',
    10 : 'supplier',
}


'''
日志配置
'''
# APP_LOG = getattr(sys, '__APP_LOG__', True)
# APP_LOG_LEVEL = logging.DEBUG
# APP_LOGDIR = os.path.join(APP_ROOT, "logs")
# APP_LOG_HANDLER = 'console,file'
# LOGGER_NAME = 'hqchip'


'''
邮件配置
'''
EMAIL = {
    'SMTP_HOST': 'smtp.163.com',
    #'SMTO_HOST': 'smtp.sina.com',
    'SMTP_PORT': 25,
    'SMTP_USER': 'hqchip@163.com',
    #'SMTP_USER': 'hqchip@sina.com',
    'SMTP_PASSWORD': 'hq123456',
    #'SMTP_PASSWORD': 'Test123456',
    'SMTP_DEBUG': True,
    'SMTP_FROM': 'hqchip@163.com',
    #'SMTP_FROM': 'hqchip@sina.com',
}

EMAIL_NOTICE = {
    # 接收人员邮箱地址列表
    'accept_list': (
        'qaulau@qq.com',
        'qaulau@139.com',
        #'373799302@qq.com',
    )
}
