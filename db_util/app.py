# -*- encoding: utf-8 -*-

__author__ = "Silva"

# built-in
import select
import socket
import threading
import multiprocessing
# thrid-party
import pymongo
# project
from .init_settings import setting
from .libs.database import db_mysql


def _catch_mongo_error(func):
    """捕获mongo错误"""

    def wrap(self):
        try:
            return func(self)
        except (select.error, socket.error, pymongo.errors.AutoReconnect) as e:
            self.__mongo = None
            return func(self)

    return wrap


class SupplierMySQL(object):
    '''供应商mysql操作'''

    def __init__(self):
        self.__db_pool = {}

    def __getattr__(self, db):
        if db not in setting.DB_KEY.values():
            raise AttributeError('%s 属性不存在' % (db,))
        if db in self.__db_pool:
            return self.__db_pool[db]
        mysql = db_mysql(**setting.DATABASES['mysql'][1])
        mysql.select_db(db)
        self.__db_pool[db] = mysql
        return mysql

    def __del__(self):
        try:
            for k in self.__db_pool:
                del self.__db_pool[k]
        except:
            pass


class DbClass(object):

    def __init__(self):
        self.__silva = None
        self.__mongo = None
        self.__supplier = None
        self.__del = set()

    @property
    def silva(self):
        if not self.__silva:
            self.__silva = db_mysql(**setting.DATABASES['mysql'][0])
            self.__del.add(self.silva)
        return self.__silva

    @property
    def supplier(self):
        if not self.__supplier:
            self.__supplier = SupplierMySQL()
            self.__del.add(self.supplier)
        return self.__supplier

    @property
    @_catch_mongo_error
    def mongo(self):
        if not self.__mongo:
            conn = pymongo.MongoClient(setting.DATABASES['mongo'][0])
            self.__mongo = conn.get_default_database()
            self.__del.add(conn)
            self.__del.add(self.mongo)
        return self.__mongo

    def __del__(self):
        for k in self.__del:
            try:
                del k
            except:
                pass


class DbSession(object):
    """针对多线程调用Db封装，多线程/进程调用安全处理"""

    def __init__(self):
        self.thread_safe = True
        self.process_safe = False
        self.session_queue = {}

    @property
    def __session_name(self):
        if self.thread_safe and self.process_safe:
            name = multiprocessing.current_process().name + '_' \
                   + threading.current_thread().name
        elif self.process_safe:
            name = multiprocessing.current_process().name
        else:
            name = threading.current_thread().name
        return name

    def __getattr__(self, attr):
        name = self.__session_name
        if name not in self.session_queue:
            self.session_queue[name] = DbClass()
        return getattr(self.session_queue[name], attr)
