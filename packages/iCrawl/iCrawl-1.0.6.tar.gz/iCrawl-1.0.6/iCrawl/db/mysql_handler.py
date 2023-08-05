#!/usr/bin/env python
# -*- coding:utf8 -*-

import sys
import Queue
import functools
import weakref
import threading
import traceback

import mysql_operator as db_operator
from iCrawl.excep.mysql_exception import *

MINLIMIT = 10
MAXLIMIT = 40


class ConnectionPool(object):
    """
    数据库连接池
    """

    def __init__(self, name, minlimit=MINLIMIT, maxlimit=MAXLIMIT, **kwargs):
        """
        数据库连接池初始化
        name: 连接名字
        minlimit: 最小连接数
        maxlimit: 最大连接数
        kwargs: 参数
        """
        self.name = name
        self.minlimit = minlimit
        self.maxlimit = maxlimit
        self.kwargs = kwargs
        self.queue = Queue.Queue(self.maxlimit)
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
        连接一个数据库
        如果当前连接池是空的，新建一个数据库连接
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
                conn = db_operator.dblib.connect(**self.kwargs)
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
                self.queue.put(db_operator.dblib.connect(**self.kwargs))
                self._live_connections += 1
        self.record_peak()

    def release(self, conn):
        """
        conn: 释放一个连接
        """
        self.pop_open_connection(conn)
        with self._lock:
            try:
                conn.rollback()
            except db_operator.dblib.OperationalError:
                print "connection seems closed, drop it."
            else:
                self.queue.put(conn)
            finally:
                pass
        self.clear_idle()


def get_class_attrs(cls):
    return [attr for attr in dir(cls) if not attr.startswith('_')]


class DataBaseConnector(object):
    """
    数据库连接类
    threading.local()这个方法用来保存一个全局变量, 但是这个全局变量只有在当前线程才能访问, 并且各自线程互不干扰
    """

    _instance_lock = threading.Lock()
    _current = threading.local()
    _lock = threading.Lock()
    _delegate = None

    def __init__(self, connection_handler=None, delegate=False):
        """
        当delegate为true时, 开启委托模式
        Global DataBaseConnector with specific connection handler
        call DataBaseConnector.connect to passing the mysql connection to this handler
        and use DataBaseConnector.db access
        current database connection wrapper class.
        connection_handler is a param
        """
        self._connection_handler = connection_handler
        self.connection_pools = {}
        with DataBaseConnector._instance_lock:
            DataBaseConnector._instance = self
        self._current.conn = self._current.conn_name = self._current.handler = None
        self.set_delegate(delegate)

    def __getattr__(self, attr):
        if not self._delegate or (attr.startswith('_') or not hasattr(self._current, "handler")):
            return self.__getattribute__(attr)
        else:
            return getattr(self._current.handler, attr)

    def set_delegate(self, delegate):
        """
        委托为真时将一个类的方法注入另一个对象，让它变成她的方法
        delegate: 委托
        """
        if delegate:
            if set(get_class_attrs(self._connection_handler)).intersection(set(get_class_attrs(self))):
                raise ClassAttrNameConflictError("If open delegate,ConnectionHandler's attr name "
                                                 "should not appear in DataBaseConnector")
            self._delegate = True
        else:
            self._delegate = False

    def add_database(self, database, minlimit=MINLIMIT, maxlimit=MAXLIMIT, **kwargs):
        """
        database: 数据库名字
        kwargs: 连接的参数
        """
        override = kwargs.pop("override", False)
        if not override and database in self.connection_pools:
            msg = "Alreay exist connection '%s',override or rename it." % database
            print msg
            # raise ConnectionNameConflictError(msg)
        else:
            self.connection_pools[database] = ConnectionPool(database, minlimit, maxlimit, **kwargs)

    def connect(self, conn_name, curstype='TUPLE', auto_commit=False):
        """
        Mapping current connection handler's method to DataBaseConnector
        """
        if not hasattr(self._current, "handler") or self._current.handler is None:
            self._current.conn = self.connection_pools[conn_name].connect()
            self._current.conn_name = conn_name
            self._current.handler = self._connection_handler(conn_name, self._current.conn, curstype, auto_commit,
                                                             db=self.connection_pools[conn_name].kwargs['db'])
            self._current.conn._cursor = weakref.proxy(self._current.handler.cursor)
        else:
            try:
                self._current.conn.ping()
                self._current.handler.cursor._connection = weakref.proxy(self._current.conn)
            except Exception as e:
                print e
                self._current.conn = db_operator.dblib.connect(**self.connection_pools[conn_name].kwargs)
                self._current.handler = self._connection_handler(conn_name, self._current.conn, curstype, auto_commit,
                                                                 db=self.connection_pools[conn_name].kwargs['db'])
            self._current.conn._cursor = weakref.proxy(self._current.handler.cursor)

    def release(self):
        """
        释放连接资源
        """
        conn = self._current.conn
        self.connection_pools[self._current.conn_name].release(conn)
        self._current.handler.close()
        del self._current.handler, self._current.conn

    @property
    def conn(self):
        """
        返回一个弱引用对象
        """
        return weakref.proxy(self._current.conn)

    @property
    def handler(self):
        """
        返回一个弱引用对象
        """
        return weakref.proxy(self._current.handler)

    @staticmethod
    def instance():
        """
        返回一个数据库连接实例
        """
        if not hasattr(DataBaseConnector, "_instance"):
            with DataBaseConnector._instance_lock:
                if not hasattr(DataBaseConnector, "_instance"):
                    DataBaseConnector._instance = DataBaseConnector()
        return DataBaseConnector._instance

dbc = DataBaseConnector(db_operator.HotelDataBaseHandler, delegate=True)


def use_db(dbname, curstype='TUPLE', auto_commit=False):
    """
    数据库选择装饰器
    """
    def with_db(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            if dbname not in dbc.connection_pools:
                raise ConnectionNotFoundError("Not found connection for '%s', use dbc.add_database add the connection")
            dbc.connect(dbname, curstype, auto_commit)
            try:
                res = func(*args, **kwargs)
            except Exception as e:
                print e
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print ('Business error: %s' % ','.join(err_messages))
                res = None
            finally:
                dbc.release()
            return res
        return _wrapper
    return with_db

if __name__ == "__main__":
    pass