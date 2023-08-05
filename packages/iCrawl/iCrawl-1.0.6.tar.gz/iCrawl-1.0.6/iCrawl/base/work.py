#!/usr/bin/env python
# -*- coding:utf8 -*-

import sys
import time
import types
import ctypes
import weakref
import traceback
import threading
import functools
import gevent

from Queue import Queue
from gevent import monkey
from gevent import Timeout

from iCrawl.excep.other_exception import TimeoutError, FlowNotFoundError, ArgumentNotRightError
from iCrawl.base.queue import BeanstalkdQueue, GPriorjoinQueue, TPriorjoinQueue

TID = threading._get_ident()


class MyLocal(threading.local):
    def __init__(self, **kwargs):
        # self.__dict__ = dict(self.__dict__, **kwargs)
        self.__dict__.update(**kwargs)


class Onceworker(threading.Thread):
    """
    一次执行基类
    """
    def __init__(self):
        """
        初始化多线程
        """
        super(Onceworker, self).__init__()
        self.__method = None
        self.__args = None
        self.__kwargs = None
        self.__callback = None
        self.__idle = True
        self.__doing = True

    def is_idle(self):
        return self.__idle

    def set_parameter(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    def get_parameter(self):
        return self.__args, self.__kwargs

    def set_method(self, method):
        self.__method = method

    def get_method(self):
        return self.__method

    def set_callback(self, callback):
        self.__callback = callback

    def get_callback(self):
        return self.__callback

    def exit(self):
        self.__doing = False

    def run(self):
        """
        多线程执行
        """
        while self.__doing:
            if self.__method:
                self.__idle = False
                if self.__callback:
                    self.__callback(self.__method(*self.__args, **self.__kwargs))
                else:
                    self.__method(*self.__args, **self.__kwargs)
                self.__method = None
                self.__callback = None
                self.__idle = True
            else:
                time.sleep(0.1)


class Workpool(threading.Thread):
    """
    线程池
    """
    def __init__(self, maxsize):
        self.__maxsize = maxsize
        self.idleworkers = Queue(self.__maxsize)
        self.allworkers = []
        self.flag = True
        for k in range(self.__maxsize):
            worker = Onceworker()
            worker.run()
            self.idleworkers.put(worker)

    def get(self):
        if self.idleworkers.empty():
            return None
        else:
            return self.idleworkers.get()

    def put(self, worker):
        while not worker.isIdle():
            time.sleep(0.1)
        self.idleworkers.put(worker)
        self.allworkers.remove(worker)

    def exit(self):
        for worker in self.allworkers:
            worker.exit()

    def __del__(self):
        self.exit()


def with_workpool(wp, callback=None):
    def wrapped(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            worker = wp.get()
            worker.method = fun
            worker.callback = callback
            worker.setParameter(args, kwargs)
            wp.put(worker)
        return wrapper
    return wrapped

RETRY = 0
TIMELIMIT = 0
_continuous = True


def initflow(which):
    """
    需要被初始化执行的函数的标签装饰器
    """
    def wrap(fun):
        # 把标签作为被装饰后的函数的一个属性
        fun.label = which

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapped
    return wrap


def index(key):
    """
    需要翻页的函数装饰器
    """
    def wrap(fun):
        # 把页数作为被装饰后的函数的一个属性
        fun.index = key

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapped
    return wrap


def retry(num=1):
    """
    需要重复执行的函数装饰器
    """
    def wrap(fun):
        # 把重复次数作为被装饰后的函数的一个属性
        fun.retry = num

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapped
    return wrap


def nextfunc(method, *args, **kwargs):
    """
    标记下一步将要执行哪一个函数的函数装饰器
    """
    def wrap(fun):
        try:
            method.args = args
            method.kwargs = kwargs
            fun.next = weakref.proxy(method)
        except Exception as e:
            print e
            method.__func__.args = args
            method.__func__.kwargs = kwargs
            fun.next = method

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapped
    return wrap


def dispatch(flag=False):
    """
    函数分发装饰器
    """
    def wrap(fun):
        # 把是否分发作为被装饰后的函数的一个属性
        fun.dispatch = flag

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapped
    return wrap


def timelimit(seconds=TIMELIMIT):
    """
    函数执行时间限制装饰器
    """
    def wrap(fun):
        # 把限制时间作为被装饰后的函数的一个属性
        fun.timelimit = seconds

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapped
    return wrap


def priority(level=0):
    """
    函数优先级别装饰器
    """
    def wrap(fun):
        # 把优先级别作为被装饰后的函数的一个属性
        fun.priority = level

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapped
    return wrap


def assure(method):
    method.succ = 0
    method.fail = 0
    method.timeout = 0
    if hasattr(method, 'retry'):
        pass
    else:
        method.retry = RETRY
    if hasattr(method, 'timelimit'):
        pass
    else:
        method.timelimit = TIMELIMIT
    if hasattr(method, 'priority'):
        pass
    else:
        method.priority = None


class Nevertimeout(object):
    def __init__(self):
        pass

    def cancel(self):
        pass


def geventwork(workqueue):
    while _continuous:
        if workqueue.empty():
            time.sleep(0.1)
        else:
            timer = Nevertimeout()
            _priority, method_id, times, args, kwargs = workqueue.get()
            method = ctypes.cast(method_id, ctypes.py_object).value
            try:
                if method.timelimit > 0:
                    timer = Timeout(method.timelimit, TimeoutError)
                    timer.start()
                result = method(*args, **kwargs)
                if result is None:
                    method.succ += 1
                elif hasattr(method, 'next'):
                    if isinstance(result, types.GeneratorType):
                        try:
                            if hasattr(method, 'index'):
                                _index = result.next()
                                if _index is not None and times == 0:
                                    if type(method.index) == int:
                                        indexargs = list(args)
                                        indexargs[method.index] = _index
                                        indexargs = tuple(indexargs)
                                        indexkwargs = dict(kwargs, **{})
                                    elif type(method.index) == str:
                                        indexargs = tuple(list(args))
                                        indexkwargs = dict(kwargs, **{method.index: _index})
                                    else:
                                        raise ArgumentNotRightError("Incorrect arguments.")
                                    workqueue.put((_priority, method_id, 0, indexargs, indexkwargs))
                            for retvar in result:
                                if retvar:
                                    if type(retvar) == dict:
                                        workqueue.put((method.next.priority, id(method.next), 0, (), retvar))
                                    else:
                                        workqueue.put((method.next.priority, id(method.next), 0, retvar, {}))
                            method.succ += 1
                        except TimeoutError:
                            if times < method.retry:
                                times += 1
                                workqueue.put((_priority, method_id, times, args, kwargs))
                            else:
                                method.timeout += 1
                        except Exception as e:
                            print e
                            if times < method.retry:
                                times += 1
                                workqueue.put((_priority, method_id, times, args, kwargs))
                            else:
                                method.fail += 1
                                t, v, b = sys.exc_info()
                                err_messages = traceback.format_exception(t, v, b)
                                print err_messages
                    else:
                        if type(result) == dict:
                            workqueue.put((method.next.priority, id(method.next), 0, (), result))
                        else:
                            workqueue.put((method.next.priority, id(method.next), 0, result, {}))
                        method.succ += 1
                else:
                    print str(result)
                    method.succ += 1
            except TimeoutError:
                if times < method.retry:
                    times += 1
                    workqueue.put((_priority, method_id, times, args, kwargs))
                else:
                    method.timeout += 1
            except Exception as e:
                print e
                if times < method.retry:
                    times += 1
                    workqueue.put((_priority, method_id, times, args, kwargs))
                else:
                    method.fail += 1
                    t, v, b = sys.exc_info()
                    err_messages = traceback.format_exception(t, v, b)
                    print err_messages
            finally:
                workqueue.task_done()
                timer.cancel()
                del timer


class Foreverworker(threading.Thread):
    """
    永久执行
    """
    def __init__(self, workqueue):
        """
        初始化多线程运行的方法和方法参数

        @param workqueue: 方法
        """
        super(Foreverworker, self).__init__()
        self.__workqueue = workqueue

    def run(self):
        """
        多线程执行
        """
        geventwork(self.__workqueue)


class Workflows(object):
    """
    任务流
    """

    def __init__(self, worknum, queuetype, worktype):
        """
        初始化的时候，根据不同的参数使用不同的队列
        """
        if worktype == 'GEVENT':
            monkey.patch_all(Event=True)
            gid = threading._get_ident()
            threading._active[gid] = threading._active[TID]
            del threading._active[TID]
            prior_join_queue = GPriorjoinQueue
        else:
            prior_join_queue = TPriorjoinQueue
        self.__flowcount = {'inner': set(), 'outer': set()}
        self.__worknum = worknum
        self.__queuetype = queuetype
        self.__worktype = worktype
        if not hasattr(self, 'clsname'):
            self.clsname = str(self.__class__).split(".")[-1].replace("'>", "")
        try:
            if self.__queuetype == 'P':
                self.queue = prior_join_queue()
            else:
                self.queue = BeanstalkdQueue(tube=str(id(self)))
        except KeyError:
            print 'Wrong type of queue, please choose P or B or start your beanstalkd service.'
        self.workers = []
        self.__flows = {}

        if self.__worktype == 'GEVENT':
            for k in range(worknum):
                if self.__queuetype == 'P':
                    worker = functools.partial(geventwork, self.queue)
                else:
                    worker = functools.partial(geventwork, BeanstalkdQueue(tube=str(id(self))))
                self.workers.append(worker)
        else:
            for k in range(worknum):
                if self.__queuetype == 'P':
                    worker = Foreverworker(self.queue)
                else:
                    worker = Foreverworker(BeanstalkdQueue(tube=str(id(self))))
                self.workers.append(worker)

    def tinder(self, flow):
        return self.__flows[flow]['tinder']

    def terminator(self, flow):
        return self.__flows[flow]['terminator']

    def add_follow(self, flow, currmethod, nextmethod):
        flag = False
        if self.__flows[flow]['tinder'] is None:
            self.__flows[flow]['tinder'] = currmethod
            self.__flows[flow]['terminator'] = currmethod
        it = self.__flows[flow]['tinder']
        assure(currmethod)
        assure(nextmethod)
        if it == nextmethod:
            flag = True
            if currmethod.priority is None:
                currmethod.priority = nextmethod.priority + 1
            self.__flows[flow]['steps'] += 1
            self.__flows[flow]['hasprior'] = self.__flows[flow]['hasprior'] and (currmethod.priority is not None)
        elif it == currmethod:
            flag = True
            self.__flows[flow]['steps'] = 2
            self.__flows[flow]['hasprior'] = (currmethod.priority is not None) and (nextmethod.priority is not None)
        else:
            self.__flows[flow]['steps'] += 1
            while hasattr(it, 'next'):
                it = it.next
                if it == currmethod:
                    self.__flows[flow]['hasprior'] = self.__flows[flow]['hasprior'] and \
                        (nextmethod.priority is not None)
                    flag = True
        if flag:
            currmethod.next = nextmethod
            if currmethod.next == self.__flows[flow]['tinder']:
                self.__flows[flow]['tinder'] = currmethod
            else:
                self.__flows[flow]['terminator'] = currmethod.next
            self.__flowcount['outer'].add(flow)
            it = self.__flows[flow]['tinder']
            if not self.__flows[flow]['hasprior']:
                num = 1
                it.priority = self.__flows[flow]['steps'] - num
                while hasattr(it, 'next'):
                    it = it.next
                    num += 1
                    it.priority = self.__flows[flow]['steps'] - num
                self.__flows[flow]['hasprior'] = True
        else:
            raise FlowNotFoundError("Not fine the flow.")

    def delete_follow(self, flow, currmethod):
        flag = False
        it = self.__flows[flow]['tinder']
        if it == currmethod:
            flag = True
        else:
            while hasattr(it, 'next'):
                it = it.next
                if it == currmethod:
                    flag = True
                    break
        if flag and hasattr(currmethod, 'next'):
            if self.__flows[flow]['terminator'] == currmethod.next:
                self.__flows[flow]['terminator'] = currmethod
            if self.__flows[flow]['terminator'] == self.__flows[flow]['tinder']:
                self.__flowcount['outer'].remove(flow)
                del self.__flows[flow]
            delattr(currmethod, 'next')
        else:
            raise FlowNotFoundError("Not fine the flow.")

    def extract_flow(self):
        def imitate(original, partial):
            if hasattr(partial, '__name__'):
                pass
            else:
                partial.__name__ = str(original).split(' at ')[0].split(' of ')[0].split('<function ')[-1].\
                    split('.')[-1].replace(' ', '').replace('>', '')
            partial.succ = 0
            partial.fail = 0
            partial.timeout = 0
            if hasattr(original, 'index'):
                partial.index = original.index
            if hasattr(original, 'retry'):
                partial.retry = original.retry
            else:
                partial.retry = RETRY
            if hasattr(original, 'timelimit'):
                partial.timelimit = original.timelimit
            else:
                partial.timelimit = TIMELIMIT
            if hasattr(original, 'priority'):
                partial.priority = original.priority
            else:
                partial.priority = None
        if self.__flowcount['inner']:
            print "Inner workflow can be set once and has been set."
        else:
            for it in dir(self):
                it = eval('self.'+it)
                if hasattr(it, 'label') and hasattr(it, 'next'):
                    self.__flows[it.label] = {'tinder': it, 'terminator': it}
            for flow in self.__flows.values():
                flow['hasprior'] = True
                flow['steps'] = 1
                p = flow['tinder']
                b = functools.partial(p)
                imitate(p, b)
                flow['hasprior'] = flow['hasprior'] and (b.priority is not None)
                flow['tinder'] = b
                self.__flowcount['inner'].add(p.label)
                while hasattr(p, 'next') and hasattr(p.next, 'args') and hasattr(p.next, 'kwargs'):
                    p = p.next
                    flow['steps'] += 1
                    if hasattr(p, 'dispatch') and p.dispatch:
                        b.next = p(self, *p.args, **p.kwargs)
                    else:
                        b.next = functools.partial(p, self, *p.args, **p.kwargs)
                    b = b.next
                    imitate(p, b)
                    flow['hasprior'] = flow['hasprior'] and (b.priority is not None)
                    flow['terminator'] = b
            for flow in self.__flows.values():
                if not flow['hasprior']:
                    it = flow['tinder']
                    num = 1
                    it.priority = flow['steps'] - num
                    while hasattr(it, 'next'):
                        it = it.next
                        num += + 1
                        it.priority = flow['steps'] - num
                    flow['hasprior'] = True
            print "Inner workflow is set."

    def fire(self, flow, *args, **kwargs):
        if self.__flows[flow]['tinder'] is not None:
            self.queue.put((self.__flows[flow]['tinder'].priority,
                            id(self.__flows[flow]['tinder']), 0, args, kwargs))
            for worker in self.workers:
                if self.__worktype == 'GEVENT':
                    gevent.spawn(worker)
                else:
                    worker.setDaemon(True)
                    worker.start()
        else:
            raise FlowNotFoundError('There is no work flow.')

    def exit(self):
        self.queue.task_done(force=True)

    def wait_complete(self):
        self.queue.join()

if __name__ == '__main__':
    pass