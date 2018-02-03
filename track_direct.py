#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
https://connect.track-trace.com/aircargo
name = "number" value = prefix + docnum
name = "page" value="full"
name = "options"
name = "v", value="N"
name ="commit", value="Track direct"
'''
import requests

def main(prefix, docnum):
    url = 'http://www.track-trace.com/aircargo'
    _data = {
        'number': '%s' % (prefix+docnum),
        'page': 'full',
        'options': '',
        'v': 'N',
        'commit': 'Track direct',
    }
    _headers = {
        'Connection': 'Keep-Alive',
        'Cookie': '',
        'Host': 'www.track-trace.com',
        'Referer': 'http://www.track-trace.com',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        'Accept': '*/*'
    }
    try:
        response = requests.post(url, data=_data, headers=_headers)
