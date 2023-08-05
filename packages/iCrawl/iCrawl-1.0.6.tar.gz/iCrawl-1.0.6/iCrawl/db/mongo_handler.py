#!/usr/bin/env python
# -*- coding:utf8 -*-

import sys
import Queue
import pymongo
import functools
import weakref
import threading
import traceback

from iCrawl.excep.mysql_exception import *


class Mongo(object):

    def __init__(self):
        pass

    def connect(self, **kwargs):
        """
        链接mongodb
        """
        if len(kwargs) <= 0:
            return None
        config = kwargs.copy()
        client = pymongo.MongoClient(config['host'], config['port'])
        if 'user' in config and config['user'] is not None and config['user'] != '':
            client.the_database.authenticate(config['user'], config['passwd'], source=config['db'])
        return client[config['db']]


class MongoPool(object):
    """
    Mongo连接池
    """

    def __init__(self, name, **kwargs):
        """
        Mongo连接池初始化
        name: 连接名字
        kwargs: 参数
        """
        self.name = name
        self.kwargs = kwargs
        self.minlimit = 1
        self.maxlimit = 5
        self.queue = Queue.Queue(5)
        self._lock = threading.Lock()
        self._live_connections = 0
        self._peak_connections = 0
        self._open_connections = []

    def __repr__(self):
        return "<%s of %s>" % (self.__class__.__name__, self.name)

    @property
    def live_connections(self):
        """
        返回当前活跃的连接数
        """
        return self._live_connections

    def record_peak(self):
        """
        记录最大值
        """
        with self._lock:
            if self._peak_connections < self._live_connections:
                self._peak_connections = self._live_connections

    def clear_idle(self):
        """
        清除实例
        """
        while self.queue.qsize() > self.minlimit:
            connect = self.queue.get()
            connect.close()
            del connect
            with self._lock:
                self._live_connections -= 1

    def connect(self):
        """
        连接一个Mongo
        如果当前Mongo连接池是空的，新建一个Mongo连接
        否则返回一个存在的连接
        """
        if self.queue.empty():
            self._connect()
            conn = self.queue.get()
        else:
            conn = None
            try:
                conn = self.queue.get()
                conn.ping()
            except Exception as e:
                print e
                del conn
                new_mongo = Mongo()
                conn = new_mongo.connect(**self.kwargs)
        self.record_open_connection(conn)
        return conn

    def record_open_connection(self, conn):
        """
        conn: 一个连接实例
        每次打开的连接实例记录在_open_connections中
        """
        with self._lock:
            self._open_connections.append(conn)

    def pop_open_connection(self, conn):
        """
        conn: 一个连接实例
        从_open_connections移走该实例, 可能会引起内存异常
        """
        print self._open_connections
        with self._lock:
            try:
                self._open_connections.remove(conn)
            except Exception:
                raise ConnectionNotInPoolError("Connection seems not belong to %s" % self.__repr__())

    def _connect(self):
        """
        打开一个新的连接, 超过最大连接数时抛出异常
        """
        with self._lock:
            if self.live_connections >= self.maxlimit:
                raise ConnectionPoolOverLoadError("Connections of %s reach limit!" % self.__repr__())
            else:
                new_mongo = Mongo()
                self.queue.put(new_mongo.connect(**self.kwargs))
                self._live_connections += 1
        self.record_peak()

    def release(self, conn):
        """
        conn: 释放一个连接
        """
        self.pop_open_connection(conn)
        self.clear_idle()


def get_class_attrs(cls):
    return [attr for attr in dir(cls) if not attr.startswith('_')]


class MongoConnector(object):
    """
    Mongo数据库连接类
    threading.local()这个方法用来保存一个全局变量, 但是这个全局变量只有在当前线程才能访问, 并且各自线程互不干扰
    """

    _instance_lock = threading.Lock()
    _current = threading.local()
    _lock = threading.Lock()

    def __init__(self):
        self.mongo_pools = {}
        with MongoConnector._instance_lock:
            MongoConnector._instance = self
        self._current.conn = None
        self._current.conn_name = None

    def __getattr__(self, attr):
        # 如果属性是私有的或者没有handler属性，直接从实例返回这个对象的属性
        if attr.startswith('_') or not hasattr(self._current, "handler"):
            return self.__getattribute__(attr)
        else:
            return getattr(self._current.handler, attr)

    def add_mongo(self, mongo_name, **kwargs):
        """
        mongo_name: 数据库名字
        kwargs: 连接的参数
        """
        if mongo_name in self.mongo_pools:
            print "Alreay exist connection '%s',override or rename it." % mongo_name
        else:
            self.mongo_pools[mongo_name] = MongoPool(mongo_name, **kwargs)

    def connect(self, mongo_name):
        if not hasattr(self._current, "conn") or self._current.conn is None:
            self._current.conn = self.mongo_pools[mongo_name].connect()
            self._current.conn_name = mongo_name
        else:
            new_mongo = Mongo()
            self._current.conn = new_mongo.connect(**self.mongo_pools[mongo_name].kwargs)
            self._current.conn_name = mongo_name

    def release(self):
        """
        释放连接资源
        """
        conn = self._current.conn
        self.mongo_pools[self._current.conn_name].release(conn)

    @property
    def conn(self):
        """
        返回一个弱引用对象
        """
        return weakref.proxy(self._current.conn)

    @staticmethod
    def instance():
        """
        返回一个数据库连接实例
        """
        if not hasattr(MongoConnector, "_instance"):
            with MongoConnector._instance_lock:
                if not hasattr(MongoConnector, "_instance"):
                    MongoConnector._instance = MongoConnector()
        return MongoConnector._instance

mongo = MongoConnector()


def use_mongo(mongo_name):
    """
    mongo数据库选择装饰器
    """
    def with_db(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            if mongo_name not in mongo.mongo_pools:
                raise ConnectionNotFoundError("Not found connection for '%s', use dbc.add_database add the connection")
            mongo.connect(mongo_name)
            try:
                res = func(*args, **kwargs)
            except Exception as e:
                print e
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print ('Business error: %s' % ','.join(err_messages))
                res = None
            # finally:
            #     mongo.release()
            return res
        return _wrapper
    return with_db


def load_mongo(mongodb, conf):
        uses = conf['use'].split(',')
        for one in uses:
            one = str(one)
            mongodb.add_mongo(
                one,
                host=conf[one]['host'],
                port=conf[one]['port'],
                user=conf[one]['user'],
                passwd=conf[one]['passwd'],
                db=conf[one]['db'],
            )


@use_mongo("innmall225")
def query_one_rate(hid):
    """
    查询一条mongodb记录
    """
    rate = mongo.conn.hotel_member_rate
    return rate.find_one({'hid': hid})

if __name__ == "__main__":

    pass