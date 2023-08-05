#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
用途:常用辅助处理功能
"""

import os
import traceback
import collections
import Levenshtein


def unicode2utf8(data):
    """
        转换输入对象为utf8格式
        @param data: 输入对象
        @return : 输出结果
    """
    if isinstance(data, unicode):
        return data.encode('utf8')
    if isinstance(data, str):
        return data
    elif isinstance(data, collections.Mapping):
        return dict(map(unicode2utf8, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(unicode2utf8, data))
    else:
        return data


def get_xml_text(node, tag):
    """
        获取XML标签的内容
        @param node: XML节点
        @param tag: 目标XML标签
        @return : 返回内容
    """
    retvar = ''
    if node.find(tag) is not None:
        retvar = node.find(tag).text
        if isinstance(retvar, unicode):
            retvar = retvar.encode('utf8')

    if retvar is None:
        retvar = ''
    return retvar.strip()


def trim_html_tag(arg_str):
    """
        将HTML标签去空白，去换行符
        @param arg_str: 要处理的字符串
        @return :  返回过滤后的内容
    """
    out_str = ''
    inflag = 0
    for s in arg_str:
        if s == '<':
            inflag = 1
            continue
        if s == '>':
            inflag = 0
            continue
        if inflag == 1:
            continue
        out_str += s

    while out_str.find('  ') > 0:
        out_str = out_str.replace('  ', '')
    out_str = out_str.replace('\r', '')
    out_str = out_str.replace('\n', '')

    return out_str.strip()


def load_json(jfile):
    """
        将json格式文件读取转换成json数据
        @param jfile: json格式数据文件
        @return : 返回json数据
    """
    import json
    if not os.path.exists(jfile) or not os.path.isfile(jfile):
        return {}
    jstr = open(jfile, 'rt').read()
    if not jstr.strip().startswith('{') or not jstr.strip().endswith('}'):
        print "[%s] file is not a json file." % jfile
        return {}
    try:
        jcfg = json.loads(jstr)
        return unicode2utf8(jcfg)
    except Exception as e:
        print e
        traceback.print_exc()
        return


def save_json(jcfg, jfile):
    """
        将json格式数据转换成字符串输出到文件
        @param jcfg: json格式数据
        @param jfile: 输出文件
    """
    import json
    try:
        jstr = json.dumps(jcfg, ensure_ascii=False, sort_keys=True, indent=2)
        open(jfile, 'wt').write(jstr)
    except Exception as e:
        print e
        traceback.print_exc()
        return


def get_str_value(str_arg, start, end):
    """
        字符串截取
        @param str_arg: 源字符串
        @param start: 起始位置
        @param end: 结束位置
        @return :  截取内容
    """
    s = str_arg.find(start)
    if s < 0:
        return ""
    e = str_arg[s + len(start):].find(end)
    if e < 0:
        return str_arg[s + len(start):].strip()
    return str_arg[s + len(start):][:e].strip()


def urldecode(querystr):
    import urllib
    d = {}
    if querystr.find('?') > 0:
        query = querystr.split('?', 1)[1]
    else:
        query = querystr

    if query.find('=') < 0:
        return d
    try:
        a = query.split('&')
        for s in a:
            if s.find('='):
                try:
                    k, v = map(urllib.unquote_plus, s.split('=', 1))
                    if k in d:
                        if isinstance(d[k], list):
                            d[k].append(v)
                        else:
                            d[k] = [d[k], v]
                    else:
                        d[k] = v
                except KeyError:
                    d[k] = v
    except Exception as e:
        print e
        return d
    return d


def clean_text(txt):
    """
    清除异常字符
    """
    if txt is None:
        txt = ""
    if len(txt) > 0:
        txt = txt.replace("\n", "").replace("\r", "").replace(" ", "")
    return txt


def is_same_hotel(kwargs):
    """
    根据几个关键字判断是否同一家店
    """
    name_ratio = Levenshtein.ratio(kwargs['name1'], kwargs['name2'])
    tel_ratio = Levenshtein.ratio(kwargs['tel1'], kwargs['tel2'])
    address_ratio = Levenshtein.ratio(kwargs['address1'], kwargs['address2'])

    if (name_ratio + tel_ratio) / 2.0 > 0.85\
            or (name_ratio + address_ratio) / 2.0 > 0.85\
            or (tel_ratio + address_ratio) / 2.0 > 0.85:
        return True
    return False


def is_same_hotel099(kwargs):
    """
    根据几个关键字判断是否同一家店
    """
    name_ratio = Levenshtein.ratio(kwargs['name1'], kwargs['name2'])
    tel_ratio = Levenshtein.ratio(kwargs['tel1'], kwargs['tel2'])
    address_ratio = Levenshtein.ratio(kwargs['address1'], kwargs['address2'])

    if (name_ratio + address_ratio) / 2.0 > 0.99\
            or (tel_ratio + address_ratio) / 2.0 > 0.99:
        return True
    return False


def is_same_hotel100(kwargs):
    """
    地址一摸一样
    """
    address_ratio = Levenshtein.ratio(kwargs['address1'].replace(' ', ''), kwargs['address2'].replace(' ', ''))

    if address_ratio == 1.0:
        return True
    return False

if __name__ == "__main__":
    pass