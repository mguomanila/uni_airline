#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for CA
'''
import sys
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import re
import traceback
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class CA(object):
    _data = {
        'orders11':'999',
        'orders1': '请输入8位数字',
        'orders12':'999',
        'orders2':'请输入8位数字',
        'orders13': '999',
        'orders3': '请输入8位数字',
        'section': '0-0001-0003-0081',
        'orders9': '78oi' # checkcode
        #'usercheckcode': '8wp8'
    }
    _headers = {
        'Connection': 'Keep-Alive',
        'Cookie': '',
        'Referer': 'http://www.airchinacargo.com/en/search_order.php',
        'User-Agent':  "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        'Host': 'www.airchinacargo.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    json = {}


def main(prefix, docnum):
    '''
    取得中国航空信息
    '''
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
    )
   try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        driver.implicitly_wait(30)
        driver.get('http://www.airchinacargo.com')
   except Exception, e:
       driver.save_screenshot('Log/except_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
       traceback.print_exc(file=sys.stdout)
   finally:
       driver.quit()