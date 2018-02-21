#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for CZ
'''
import sys
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import re
import simplejson as json
import traceback
from utility import CZ, EK

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from django.http import HttpResponse, HttpResponseBadRequest


def main(prefix, docnum):
    try:
        driver = webdriver.PhantomJS(
                           desired_capabilities=CZ.dcap,
                            service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        driver.implicitly_wait(30)
        driver.get('http://tang.cs-air.com/index.aspx')
        driver.find_element_by_link_text('AWB Tracking').click()
        driver.execute_script("$('#awbprefix').val('%s')" % prefix)
        driver.execute_script("$('#awbnumber').val('%s')" % docnum)
        driver.find_element_by_id('btnQueryAWB').click()
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_panelCombine')))
        content = bs4(driver.page_source, 'html.parser')
        driver.save_screenshot(
            './Log/CZ_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
    except Exception, e:
        driver.save_screenshot('./Log/except_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
        traceback.print_exc(file=sys.stdout)
    finally:
        driver.quit()
    table = content.find_all('table')
    status = list(table[2].stripped_strings)
    flight = []
    for i in range(len(status)):
        if re.search(r'[\dA-Z]{4, 10}', status[i]) and re.search(r'[-\d]{10}', status[i+1]):
            d = {
                'air_code': '%s' % status[i],
                '_dep_port': '%s' % status[i - 2],
                '_dest_port': '%s' % status[i - 1],
                'airline_comp': 'CZ',
            }
            flight.append(d)

    status = list(table[4].stripped_strings)
    j = 0
    for i in range(len(status)):
        if 'Cargo has been loaded' in status[i]:
            flight[j].update({'_atd': '%s' % status[i - 3]})
        if 'Cargo has been loaded' in status[i]:
            flight[j].update({'_ata': '%s' % status[i - 3]})
            j += 1
    return flight


def index(request, prefix, docnum):
    try:
        return HttpResponse(json.dumps(main(prefix, docnum)), content_type='text/json')
    except:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest('Try again...')


if __name__ == '__main__':
    a = sys.argv[1]
    if a:
        prefix = a[0:3]
        docnum = a[3:11]
    print main(prefix, docnum)