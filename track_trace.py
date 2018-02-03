#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
http://www.track-trace.com/aircargo
'''
import sys
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import traceback
import simplejson as json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.http import HttpResponse, HttpResponseBadRequest

import EK, EK2, AA2, KZ


def main(prefix, docnum):
    '''
    :param prefix:
    :param docnum:
    :return:
    '''
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
    )

    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        driver.implicitly_wait(30)
        driver.get('http://www.track-trace.com/aircargo')
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'aircargoform')))
        driver.execute_script("$('#number').val('%s-%s')" % (prefix, docnum))
        driver.find_element_by_name('commit').click()
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'retrieveContentDiv')))
        content = bs4(driver.page_source, 'html.parser')
        cookies = {d['name']: d['value'] for d in driver.get_cookies()}
        # for debugging only - erase when not needed
        driver.save_screenshot('./Log/%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
    except Exception, e:
        driver.save_screenshot('./Log/except_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
        traceback.print_exc(file=sys.stdout)
    finally:
        driver.quit()

    form = content.find('form')
    action = form['action']
    method = form['method']
    data = {}
    for d in form.find_all('input'):
        if d.get('value', None) is None:
            data[d['name']] = ''
        else:
            data[d['name']] = d['value']

    if 'skychain' in form['action']:
        return EK2.main(action, method, data, cookies)
    if 'aacargo' in form['action']:
        return AA2.main(action, method, data, cookies)
    if 'copacargo' in form['action']:
        return KZ.main(action, method, data, cookies)


def index(request, prefix, docnum ):
    try:
        return HttpResponse(json.dumps(main(prefix, docnum)), content_type='text/json')
    except:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest('Try again...')