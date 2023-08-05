#!/usr/bin/env python
# -*- coding:utf8 -*-

"""
抓取工具的坐标处理功能
"""

import math
import json

from math import sqrt, sin, atan2, cos
from iCrawl.fixture.key_martix import ABCKEY

base10to36 = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A')+26)]


def dec2hex(num):
    """
        10进制转换成36进制
        @param num: 10进制数字
        @return: 36进制字符串
    """

    mid = []
    while True:
        num, rem = divmod(num, 36)
        mid.append(base10to36[rem])
        if num == 0:
            break
    return ''.join([str(_x) for _x in mid[::-1]])

base36to10 = {'1': 1, '0': 0, '3': 3, '2': 2, '5': 5, '4': 4, '7': 7, '6': 6, '9': 9, '8': 8, 'A': 10,
              'C': 12, 'B': 11, 'E': 14, 'D': 13, 'G': 16, 'F': 15, 'I': 18, 'H': 17, 'K': 20, 'J': 19,
              'M': 22, 'L': 21, 'O': 24, 'N': 23, 'Q': 26, 'P': 25, 'S': 28, 'R': 27, 'U': 30, 'T': 29,
              'W': 32, 'V': 31, 'Y': 34, 'X': 33, 'Z': 35}


def hex2dec(stri):
    """
        36进制转换成10进制
        @param stri: 36进制字符串
        @return: 10进制数字
    """
    num = 0
    stri = stri[::-1]
    for k in stri:
        num += base36to10[k] * pow(36, stri.index(k))
    return num


def decode_mapbar_latlnt(latlon):
    """图吧地图的经纬度解密
        @param latlon: 图吧经纬度36进制字符串
        @return: 10进制经度，10进制纬度
    """
    if not latlon or latlon.strip() == '':
        return [0.0, 0.0]
    latlon = latlon.strip()
    tmp, org, max_num_pos, max_num = 0, '', -1, 0
    try:
        for k in range(len(latlon)):
            tmp = ord(latlon[k]) - ord('A')
            if tmp >= 10:
                tmp -= 7
            org += dec2hex(tmp)
            if tmp > max_num:
                max_num_pos = k
                max_num = tmp
        diff = int(org[0:max_num_pos], 16)
        _sum = int(org[max_num_pos+1:], 16)
        lnt = (diff + _sum - 3409) / 2.0
        lat = (_sum - lnt) / 100000.0
        lnt /= 100000.0
    except:
        return [0.0, 0.0]
    return [lat, lnt]


def decode_mapabc_latlnt(llstr):
    """
        图盟地图的经纬度解密
        @param llstr: 图盟经纬度36进制字符串
        @return: 10进制经度或纬度
    """
    llstr = llstr.strip()
    keyposition = 0
    last4chr = llstr[-4:]
    for k in range(len(last4chr)):
        keyposition |= (ord(last4chr[k]) & 3) << (k * 2)
    keygroup = ABCKEY[keyposition]
    firsts = []
    for c in llstr[:-4]:
        firsts.append(ord(c))
    fixed = (not keygroup[0] and 23) or (keygroup[0] and 53) or ((not keygroup[0] and 23) or (keygroup[0] and 53))
    for k in range(len(firsts)):
        firsts[k] -= fixed
        firsts[k] -= keygroup[k + 1]
    try:
        llone = float(''.join(chr(one) for one in firsts))
    except:
        llone = 0.0
    return llone


def convert_g2b(glat, glnt):
    """
        通过百度map接口，将谷歌经纬度转换成百度经纬度
        @param glat: 谷歌纬度
        @param glnt: 谷歌经度
        @return blat, blnt: 百度纬，经度元组
    """
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    x = float(glnt)
    y = float(glat)
    z = sqrt(x * x + y * y) + 0.00002 * sin(y * x_pi)
    theta = atan2(y, x) + 0.000003 * cos(x * x_pi)
    blnt = z * cos(theta) + 0.0065
    blat = z * sin(theta) + 0.006
    return blat, blnt


def convert_b2g(blat, blnt):
    """
        通过百度map接口，将百度经纬度转换成谷歌经纬度
        @param blnt: 百度纬度
        @param blat: 百度经度
        @return blat, blnt: 谷歌纬，经度元组
    """
    x_pi = 3.14159265358979324 * 3000.0 / 180.0

    x = float(blnt) - 0.0065
    y = float(blat) - 0.006
    z = sqrt(x * x + y * y) - 0.00002 * sin(y * x_pi)
    theta = atan2(y, x) - 0.000003 * cos(x * x_pi)
    glnt = z * cos(theta)
    glat = z * sin(theta)
    return glat, glnt


def cal_distance(lat1, lon1, lat2, lon2):
    """
        通过计算，获取两谷歌座标之间的直线距离
        @param lat1: 坐标纬度
        @param lon1: 坐标经度
        @param lat2: 坐标纬度
        @param lon2: 坐标经度
        @return :直线距离，单位米
    """
    if type(lat1) == str:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

    a = 6378137.0
    b = 6356752.314245
    f = 1 / 298.257223563

    lnt_radians = math.radians(lon2 - lon1)

    u1 = math.atan((1 - f) * math.tan(math.radians(lat1)))
    u2 = math.atan((1 - f) * math.tan(math.radians(lat2)))

    sin_u1 = math.sin(u1)
    cos_u1 = math.cos(u1)
    sin_u2 = math.sin(u2)
    cos_u2 = math.cos(u2)

    cos_sq_alpha = float()
    sin_sigma = float()
    cos2_sigma_m = float()
    cos_sigma = float()
    sigma = float()

    l = lnt_radians
    iter_limit = 100
    while True:
        sin_lambda = math.sin(l)
        cos_lambda = math.cos(l)
        sin_sigma = math.sqrt((cos_u2 * sin_lambda) * (cos_u2 * sin_lambda) +
                              (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda) *
                              (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda))
        if sin_sigma == 0:
            return 0
        cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cos_u1 * cos_u2 * sin_lambda / sin_sigma
        cos_sq_alpha = 1 - sin_alpha * sin_alpha
        cos2_sigma_m = cos_sigma - 2 * sin_u1 * sin_u2 / cos_sq_alpha
        c = f / 16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
        lambda_p = l
        l = lnt_radians + (1 - c) * f * sin_alpha * \
                          (sigma + c * sin_sigma * (cos2_sigma_m + c * cos_sigma *
                                                    (-1 + 2 * cos2_sigma_m * cos2_sigma_m)))
        if (iter_limit == 0) or ((math.fabs(l - lambda_p) > 1e-12) and (iter_limit > 0)):
            break
        iter_limit -= - 1
    if iter_limit == 0:
        return 0
    u_sq = cos_sq_alpha * (a * a - b * b) / (b * b)
    a = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    b = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
    delta_sigma = b * sin_sigma * \
                  (cos2_sigma_m + b / 4 * (cos_sigma * (-1 + 2 * cos2_sigma_m * cos2_sigma_m) -
                                           b / 6 * cos2_sigma_m * (-3 + 4 * sin_sigma * sin_sigma) *
                                           (-3 + 4 * cos2_sigma_m * cos2_sigma_m)))
    return b * a * (sigma - delta_sigma)

BD_URL = 'http://api.map.baidu.com/place/v2/search'


def get_baidu_coordinates(ap_key, name, city=None, flag=False):
    """获取百度坐标
    flag为True时返回转换后的谷歌坐标系
    lat, lnt
    """
    data = {'ak': ap_key, 'query': name, 'output': 'json',
            'page_size': 1, 'page_num': 0, 'scope': 1,
            'region': city if city else '全国'
            }
    try:
        import requests as _requests
    except ImportError:
        _requests = None
    if _requests:
        map_info = _requests.get(BD_URL, params=data)
        try:
            html_text = json.loads(map_info.content)
            if html_text['status'] != 0:
                lat, lnt = 0.0, 0.0
            else:
                location = html_text['results'][0]['location']
                lat = float(location['lat'])
                lnt = float(location['lng'])
        except KeyError:
            lat, lnt = 0.0, 0.0
        except IndexError:
            lat, lnt = 0.0, 0.0
        if flag and lat != 0.0:
            return convert_b2g(lat, lnt)
        return lat, lnt
    else:
        return 0.0, 0.0

if __name__ == '__main__':
    pass