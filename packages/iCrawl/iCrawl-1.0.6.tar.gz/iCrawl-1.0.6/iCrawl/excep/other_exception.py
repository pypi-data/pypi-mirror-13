#!/usr/bin/env python
# -*- coding:utf8 -*-


class OriginError(Exception):
    def __init__(self):
        pass

    def __del__(self):
        pass


class URLFailureException(OriginError):
    def __init__(self, url, respcode):
        self.url = url
        self.respcode = respcode

    def log(self):
        print('%s: %s' % (self.url, self.respcode))


class TimeoutError(OriginError):
    def __init__(self):
        pass

    def __del__(self):
        pass


class TimeFomatError(Exception):
    def __init__(self):
        pass

    def __del__(self):
        pass


class FlowNotFoundError(OriginError):
    def __init__(self, error):
        self.error_msg = error
        pass

    def __del__(self):
        pass

    def log(self):
        print('%s' % self.error_msg)


class ArgumentNotRightError(OriginError):
    def __init__(self, error):
        self.error_msg = error
        pass

    def __del__(self):
        pass

    def log(self):
        print('%s' % self.error_msg)