#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for EK
'''
import sys
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import traceback
import re
import simplejson as json
from utility import CV

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from django.http import HttpResponse, HttpResponseBadRequest


def main(prefix, docnum):
    try:
        driver = webdriver.PhantomJS(desired_capabilities=CV.dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        driver.implicitly_wait(30)
        driver.get('https://cvtnt.champ.aero/trackntrace')
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, 'search-button')))
        driver.execute_script("$('#awbnum').val('%s-%s')" % (prefix, docnum))
        driver.find_element_by_id('search').click()
        driver.find_element_by_id('search-button').click()
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'panel-body')))
        content = bs4(driver.page_source, 'html.parser')
        # for debugging only - erase when not needed
        driver.save_screenshot('./Log/CV_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
    except Exception, e:
        driver.save_screenshot('./Log/except_CV_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
        traceback.print_exc(file=sys.stdout)
    finally:
        driver.quit()

    script = [data for data in content.find_all('script') if 'CDATA' in str(data)][-1]
    for txt in script.stripped_strings:
        _, data = re.search(r'([a-zA-Z\d]+)\s=\s({.*})', txt).groups()
    a = re.search(r"('.+':'.+')", data).groups()[-1].split(',')
    dumps = {}
    for c in a:
        dumps.update(dict({re.search(r"'(.+)':'?(.+)'?", c).groups()}))
    d = {
        'air_code': '%s' % ,
        '_std': '%s' % '',
        '_sta': '%s' % '',
        '_etd': '%s' % '',
        '_eta': '%s' % '',
        '_atd': '%s' % ,
        '_ata': '%s' % ,
        '_dep_port': '%s' % ,
        '_dest_port': '%s' % ,
        'airline_comp': 'CV'
    }

def index(request, prefix, docnum):
    try:
        return HttpResponse(json.dumps(main(prefix, docnum)), content_type='text/json')
    except:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest('Try again...')


if __name__ == '__main__':
    # 获取提单号
    a = sys.argv[1]
    if a in locals():
        prefix = a[0:3]
        docnum = a[3:11]
    main(prefix, docnum)