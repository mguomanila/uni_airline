#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for EK
new implementation
'''
import requests
from bs4 import BeautifulSoup as bs4

def main(action, method, data, cookies):
    '''
    :param prefix:
    :param docnum:
    :return:
    '''
    r = requests.post(action, data=data, cookies=cookies)
    content = bs4(r.content)
    info = soup.find_all('table', attrs={'name': 'trackShiptable'})