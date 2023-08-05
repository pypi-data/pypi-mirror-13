#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
日志工具
"""

import sys
import os
import logging

from logging import config
from logging.handlers import TimedRotatingFileHandler


def get_module_path(filename):
    """Find the relative path to its module of a python file if existing.
    filename
      string, name of a python file
    """
    filepath = os.path.abspath(filename)
    prepath = filepath[:filepath.rindex('/')]
    postpath = '/'
    if prepath.count('/') == 0 or not os.path.exists(prepath + '/__init__.py'):
        flag = False
    else:
        flag = True
    while True:
        if prepath.endswith('/lib') or prepath.endswith('/bin') or prepath.endswith('/site-packages'):
            break
        elif flag and (prepath.count('/') == 0 or not os.path.exists(prepath + '/__init__.py')):
            break
        else:
            for f in os.listdir(prepath):
                if '.py' in f:
                    break
            else:
                break
            postpath = postpath.replace(postpath, prepath[prepath.rindex('/'):].split('-')[0].split('_')[0] + postpath)
            prepath = prepath[:prepath.rindex('/')]
    return postpath.lstrip('/') + filename.split('/')[-1].replace('.pyc', '').replace('.py', '') + '/'


def get_module_name(filename):
    """Find the modulename from filename.
    filename
      string, name of a python file
    """
    return filename.split('/')[-1].replace('.pyc', '').replace('.py', '')


def _cu(arg, encoding='utf8'):
    """将对象转换成字符串
        @param arg: 输入字符串
        @param return: 输出对象
    """
    if isinstance(arg, unicode):
        return arg
    elif isinstance(arg, str):
        try:
            return arg.decode(encoding)
        except:
            import chardet
            det = chardet.detect(arg)
            if det['encoding']:
                return arg.decode(det['encoding'], 'ignore')
            else:
                return arg.decode('gbk', 'ignore')
    else:
        return unicode(arg)


def logger():
    logging.config.fileConfig('../conf/logging.conf')
    return logging.getLogger('crawl')


def clogger(cfile, loggername):
    logging.config.fileConfig(cfile)
    return logging.getLogger(loggername)


def clog(category, logname, level='INFO', backup_count=15, to_stdout=True):
    """生成日志输出的方法和对象
        @param category 日志路径
        @param logname 日志名称
        @param level 日志输出级别 (可选)
        @param backup_count 日志轮询备份记录 (可选)
        @param to_stdout 是否屏幕输出 (可选)
        @return _wraper 返回日志方法
        @return logger 返回日志对象
    """
    path = os.path.join(category, logname + '.log')
    if not os.path.exists(path[:path.rindex('/')]):
        os.makedirs(path[:path.rindex('/')])

    # Initialize logger
    _logger = logging.getLogger(logname)
    frt = '%(asctime)s|%(process)d.%(thread)d|%(filename)s:%(lineno)d|%(levelname)s|%(message)s'
    frt = logging.Formatter(frt)
    if path:
        _handler = TimedRotatingFileHandler(path, 'D', 1, backup_count)
        _handler.suffix = "%Y%m%d"
        _handler.setFormatter(frt)
        _handler._name = logname + '_p'
        already_in = False
        for _hdr in _logger.handlers:
            if _hdr._name == logname + '_p':
                already_in = True
                break
        if not already_in:
            _logger.addHandler(_handler)
    if to_stdout:
        _handler = logging.StreamHandler(sys.stdout)
        _handler.setFormatter(frt)
        _handler._name = logname + '_s'
        already_in = False
        for _hdr in _logger.handlers:
            if _hdr._name == logname + '_s':
                already_in = True
        if not already_in:
            _logger.addHandler(_handler)
    if level == 'NOTEST':
        level == logging.NOTSET
    elif level == 'DEBUG':
        level == logging.DEBUG
    elif level == 'WARNING':
        level == logging.WARNING
    elif level == 'ERROR':
        level == logging.ERROR
    elif level == 'CRITICAL':
        level == logging.CRITICAL
    else:
        level == logging.INFO
    _logger.setLevel(level)

    return _logger


class Bcolors:
    """定义常用颜色"""
    HEADER = '\033[95m'  # 红粉
    OKBLUE = '\033[94m'  # 暗蓝
    OKGREEN = '\033[92m'  # 银光绿
    WARNING = '\033[93m'  # 黄
    FAIL = '\033[91m'  # 红
    ENDC = '\033[0m'  # 白

    def __init__(self):
        pass


if __name__ == '__main__':
    pass