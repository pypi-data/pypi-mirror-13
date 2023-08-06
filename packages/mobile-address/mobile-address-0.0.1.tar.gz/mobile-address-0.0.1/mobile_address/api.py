#!/usr/bin/env python
# coding=utf-8
# *************************************************
# File Name    : src/api.py
# Author       : Cole Smith
# Mail         : tobewhatwewant@gmail.com
# Github       : whatwewant
# Created Time : 2016年02月12日 星期五 21时47分11秒
# *************************************************
import re
import requests

#
class MobileAddress(object):
    def __init__(self, phone=None):
        # TAOBAO API
        self._url = r'http://tcc.taobao.com/cc/json/mobile_tel_segment.htm?tel={}'

        self._phone = phone
        self._data = {}

        # resolve data
        self._resolve()

    def _phone_match(self):
        _reg = '^0?1[3|4|5|7|8][0-9]\\d{8}$'
        if not re.match(_reg, self._phone):
            return False
        return True

    def _request(self):
        assert self._phone != None
        assert isinstance(self._phone, str)
        assert self._phone_match()
        return requests.get(self._url.format(self._phone))

    def _resolve(self):
        req = self._request()
        if not req.ok:
            raise req.status_code
        raw_data = req.text\
                      .replace('__GetZoneResult_ = ', '')\
                      .replace('\r\n', '')\
                      .replace(' ', '')\
                      .replace('{', '')\
                      .replace('}', '')\
                      .replace('\'', '')\
                      .replace('\t', '')
        if not raw_data:
            raise Exception('未能查到该手机的归属地')
        # real data
        # type dict
        # {
        #    "mts": "1860598",
        #    "province": "福建",
        #    "catName": "中国联通",
        #    "telString": "18605981756",
        #    "areaVid": "30519",
        #    "ispVid": "137815084",
        #    "carrier": "福建联通"
        # }
        for _ in raw_data.split(','):
            self._data[_.split(':')[0]] = _.split(':')[1]
        return self._data

    def get_full(self):
        assert self._data != {}
        return self._data

    def get_province(self):
        assert self._data != {}
        # assert self._data.get('province', None)
        return self._data.get('province', '未知')

    def get_carrier_name(self):
        assert self._data != {}
        return self._data.get('catName', '未知')

    def get_carrier(self):
        assert self._data != {}
        return self._data.get('carrier', '未知')
