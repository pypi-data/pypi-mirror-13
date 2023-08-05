#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
通信协议加密解密库
"""

import base64
import urllib
import json
import collections
import gzip
import time

from cStringIO import StringIO
from Crypto.Cipher import AES
from hashlib import md5

DEFAULT_SALT_KEY = ''


def url_params_decode(query):
    d = {}
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


def urldecode(querystr):
    if querystr.find('?') > 0:
        query = querystr[querystr.find('?')+1:]
    else:
        query = querystr

    return url_params_decode(query)


def gz(in_text):
    """压缩为gz格式
    """
    buf = StringIO()
    f = gzip.GzipFile(mode="wb", fileobj=buf)
    f.write(in_text)
    f.close()
    cdata = buf.getvalue()
    return cdata


def ungz(in_text):
    """gz格式解压缩
    """
    inbuffer = StringIO(in_text)
    f = gzip.GzipFile(mode="rb", fileobj=inbuffer)
    rdata = f.read()
    return rdata


def aes_decrypt(ciphertext, a_key):
    """
    AES密文解密
    ciphertext: 密文
    a_key: 密钥（HEX格式编码） 例如：'4F6DEF26E1E6917F2A4F27D754B70B6D'
    解密后的数据(未做编码)
    """

    a_key = a_key.decode('HEX')

    unpad = lambda s: s[0:-ord(s[-1])]
    _mode = AES.MODE_ECB
    decryptor = AES.new(a_key, _mode)
    plain = decryptor.decrypt(ciphertext)
    return unpad(plain)


def v1_encrypt(in_text, a_key):
    """
    协议文本加密：
    in_text:待加密文本
    a_key:密钥,16的整数倍
    密文，已被base64编码1次。
    原文：4033910000000000
    密钥：kuaijiejiudiangu
    加密后十六进制串：1d1402643cd679aeb3d79d253ba11421b360cbba1927b756106b81f86ede6ce1
    """
    bs = AES.block_size
    pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    _mode = AES.MODE_ECB
    aesor = AES.new(a_key, _mode)
    out_text = aesor.encrypt(pad(in_text))
    out_text = base64.b64encode(out_text)
    return out_text


def v1_decrypt(in_text, a_key):
    """
    协议文本解密：
    intext:密文，已被base64编码过
    key: 密钥
    解密后的明文（未做编码）
    原文：4033910000000000
    密钥：
    加密后十六进制串：1d1402643cd679aeb3d79d253ba11421b360cbba1927b756106b81f86ede6ce1
    """
    unpad = lambda s: s[0:-ord(s[-1])]
    in_text = base64.b64decode(in_text)

    _mode = AES.MODE_ECB
    aesor = AES.new(a_key, _mode)
    out_text = aesor.decrypt(in_text)

    return unpad(out_text)


def gz_encrypt(in_text, a_key):
    """
    压缩并加密数据
    intext:
    key:
    """
    return v1_encrypt(gz(in_text), a_key)


def gz_decrypt(in_text, a_key):
    """
    解密并解压数据
    """
    return ungz(v1_decrypt(in_text, a_key))


def gz_encrypt_json(indata, key):
    """
    字典转换为json，再压缩，再加密
    """
    if isinstance(indata, str) or isinstance(indata, unicode):
        intext = indata
    else:
        intext = json.dumps(indata, ensure_ascii=False)

    return gz_encrypt(intext, key)


def gz_decrypt_json(in_text, a_key):
    """
    解密，解压缩，并转换json为字典
    """
    def unicode2utf8(data):
        """
        转换输入对象为utf8格式
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
    out_text = gz_decrypt(in_text, a_key)
    return unicode2utf8(json.loads(out_text))


def url_encrypt(in_data, a_key):
    """
    键值对用urlencode编码后加密
    """
    in_text = urllib.urlencode(in_data)
    return v1_encrypt(in_text, a_key)


def url_decrypt(intext, key):
    """
    解密后，把urlencode编码的内容转换为键值对字典
    """
    out_text = v1_decrypt(intext, key)
    return url_params_decode(out_text)


def http_sign(data, stime):
    """
    对请求数据进行协议签名生成
    """
    md5_er = md5()
    md5_er.update(data + stime + DEFAULT_SALT_KEY)
    sign = md5_er.hexdigest()[5:10]
    del md5_er
    return sign


def http_check_sign(data, stime, sign):
    """
    检查协议前面是否正确
    """
    signok = http_sign(data, stime)
    if signok.lower() != sign.lower():
        print "http_check_sign ERROR data[...]time[%s]\nsignok[%s]sign[%s]" % (stime, signok, sign)
    return signok.lower() == sign.lower()


def http_request(url, data, key='', mode=''):
    """
    http 请求方法，支持明文和密文方式。
    密文方式会返回字典数据
    明文方式会返回文本数据
    """
    if key == '':
        key = DEFAULT_SALT_KEY

    if mode == 'plain':  # 不加密
        outtext = data
    else:
        outtext = gz_encrypt_json(data, key)

    stime = time.strftime('%Y%m%d%H%M%S', time.localtime())
    sign = http_sign(outtext, stime)

    import requests
    r = requests.post(url, data={'data': outtext, 'time': stime, 'sign': sign})
    if r.status_code != 200:
        return False, "post [%s] http_code[%d] <> 200" % (url, r.status_code)

    content = r.content
    if mode == 'plain':
        return True, content

    rtext = gz_decrypt_json(content)
    rst = (True, rtext)
    return rst


if __name__ == "__main__":
    pass