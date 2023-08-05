#!/usr/bin/env python
# -*- coding:utf8 -*-

import time
import datetime
from threading import Lock

from iCrawl.base.work import Workflows

WORKNUM = 30
QUEUETYPE = 'P'
WORKTYPE = 'GEVENT'


class SpiderOrigin(Workflows):
    __lasttime = datetime.datetime.now()
    __lock = Lock()
    totaltime = 0
    stat = None

    def __init__(self, worknum=WORKNUM, queuetype=QUEUETYPE, worktype=WORKTYPE, timeout=-1):
        super(SpiderOrigin, self).__init__(worknum=worknum, queuetype=queuetype, worktype=worktype)
        self.timeout = timeout
        self.prepare()
        self.dones = set()

    def prepare(self):
        pass

    def fetch_datas(self, flow, *args, **kwargs):
        """
        抓取酒店数据
        """
        try:
            self.extract_flow()
            start = time.time()
            self.fire(flow, *args, **kwargs)
            if self.timeout > -1:
                def check(self, timeout):
                    time.sleep(timeout)
                    self.exit()
                    print 'Time out of %s. ' % str(self.timeout)
                import threading
                wather = threading.Thread(target=check, args=(self, self.timeout - (time.time() - start)))
                wather.setDaemon(True)
                wather.start()
            self.wait_complete()
            if hasattr(self, 'onway') and self.onway:
                self.onway(None, forcexe=True)
            self.dones.add(flow)
            end = time.time()
            self.totaltime = end - start
            return True
        except Exception as e:
            print e
            return False

    @staticmethod
    def clear_data_one(self, one):
        """
        清洗数据
        """
        pass

    @staticmethod
    def implement_data_one(self, *args, **kwargs):
        """
        补充酒店数据
        """
        pass

    @classmethod
    def uniquetime(cls, timespan=1, lasttime=None):
        if lasttime is None:
            with cls.__lock:
                cls.__lasttime = cls.__lasttime + datetime.timedelta(seconds=timespan)
                return cls.__lasttime
        else:
            cls.__lasttime = max(cls.__lasttime, lasttime)

    def statistic(self):
        """
        统计
        """
        for flow in self.dones:
            it = self.tinder(flow)
            print '==============Statistics of flow %s==============' % flow
            self.stat = dict()
            self.stat['total'] = {'succ': 0, 'fail': 0, 'timeout': 0}
            self.stat[it.__name__] = {}
            self.stat[it.__name__]['succ'] = it.succ
            self.stat[it.__name__]['fail'] = it.fail
            self.stat[it.__name__]['timeout'] = it.timeout
            self.stat['total']['succ'] = self.stat['total']['succ'] + it.succ
            self.stat['total']['fail'] = self.stat['total']['fail'] + it.fail
            self.stat['total']['timeout'] = self.stat['total']['timeout'] + it.timeout
            print it.__name__, 'succ: ', it.succ
            print it.__name__, 'fail: ', it.fail
            print it.__name__, 'timeout: ', it.timeout
            while hasattr(it, 'next'):
                self.stat[it.next.__name__] = {}
                self.stat[it.next.__name__]['succ'] = it.next.succ
                self.stat[it.next.__name__]['fail'] = it.next.fail
                self.stat[it.next.__name__]['timeout'] = it.next.timeout
                self.stat['total']['succ'] = self.stat['total']['succ'] + it.next.succ
                self.stat['total']['fail'] = self.stat['total']['fail'] + it.next.fail
                self.stat['total']['timeout'] = self.stat['total']['timeout'] + it.next.timeout
                print it.next.__name__, 'succ: ', it.next.succ
                print it.next.__name__, 'fail: ', it.next.fail
                print it.next.__name__, 'timeout: ', it.next.timeout
                it = it.next
            print 'total succ: ', self.stat['total']['succ']
            print 'total fail: ', self.stat['total']['fail']
            if float(self.stat['total']['fail']) / float(self.stat['total']['succ']) > 0.5:
                print 'too many'
                # send a email or msg to adminstrator
            print 'total timeout: ', self.stat['total']['timeout']
            print 'total time: ', self.totaltime

    @staticmethod
    def now():
        return datetime.datetime.now()

    def __del__(self):
        pass

if __name__ == '__main__':
    pass