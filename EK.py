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
import simplejson as json
from utility import EK

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.cache import cache

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def main(prefix, docnum):
    '''
    :param prefix:
    :param docnum:
    :return:
    '''
    key = prefix + docnum
    cached_content = cache.get(key)
    if cached_content is None:
        try:
            driver = webdriver.PhantomJS(desired_capabilities=EK.dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
            driver.implicitly_wait(30)
            driver.get('https://skychain.emirates.com/skychain/app?service=page/nwp:Trackshipmt')
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, '$Submit')))
            driver.execute_script("$('#txtPrefix').val('%s')" % prefix)
            driver.execute_script("$('#txtNumber').val('%s')" % docnum)
            driver.find_element_by_name('$Submit').click()
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'trackShiptable1')))
            content = bs4(driver.page_source, 'html.parser')
            # for debugging only - erase when not needed
            driver.save_screenshot('./Log/EK_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
        except Exception, e:
            driver.save_screenshot('./Log/except_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
            traceback.print_exc(file=sys.stdout)
        finally:
            driver.quit()
        table = content.find_all('table', class_='table collapsible-table border-table')[-1]  #  assuming last one is impt
        table = list(table.stripped_strings)
        flight = []
        for i in range(len(table)):
            if 'Arrived' in table[i] or 'Departed' in table[i] or 'Booking Confirmed' in table[i]:
                air, port, _std, _sta, _etd, _eta, _atd, _ata = EK.format_content(table[i+1])
                d = {
                    'air_code': '%s' % air,
                    '_std': '%s' % _std,
                    '_sta': '%s' % _sta,
                    '_etd': '%s' % _etd,
                    '_eta': '%s' % _eta,
                    '_atd': '%s' % _atd,
                    '_ata': '%s' % _ata,
                    '_dep_port': '%s' % port[0],
                    '_dest_port': '%s' % port[1],
                    'airline_comp': 'EK'
                }
                flight.append(EK.pop(d))
        cached_content = EK.arrange(flight)
        cache.set(key, cached_content, 60 * 60)  # cache for one hour
    return cached_content


@cache_page(CACHE_TTL)
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