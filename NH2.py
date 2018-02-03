#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module 2 for NH
'''
import sys
from bs4 import BeautifulSoup as bs4
import re
import traceback
import simplejson as json
from datetime import datetime
from utility import NH, Others
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from django.http import HttpResponse, HttpResponseBadRequest

from contextlib import contextmanager
from django.views.decorators.cache import cache_page
from copy import deepcopy


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class WebWait(object):
    @contextmanager
    def wait_for_page_load(self, driver, class_name, timeout=30):
        old_page = driver.find_element_by_class_name(class_name)
        yield
        WebDriverWait(driver, timeout).until(EC.staleness_of(old_page))


def update(flight):
    '''
    this is a call from utility.Others.detailed()
    :param flight:
    :return:
    '''
    prefix = flight[0]['prefix']
    docnum = flight[0]['docnum']
    NH.flight = main(prefix, docnum)
    new_flight = deepcopy(flight)
    # merge NH flight with other flights:
    for step in range(len(flight)):
        for nh_step in range(len(NH.flight)):
            if 'CA' in flight[step]['air_code'] \
                    and flight[step]['_dep_port'] == NH.flight[nh_step]['_dep_port'] \
                    and not nh_step:
                new_flight[step].update(NH.flight[nh_step])
            if nh_step > 0:
                # made an assumption here:
                # flight is unique -> that is there is only one flight
                new_flight.insert(step+nh_step, NH.flight[nh_step])
        break  # no need to continue
    return new_flight


def sanitize(txt):
    return txt.replace('\t', '').replace('\r', '')


def main(prefix, docnum):
    try:
        driver = webdriver.PhantomJS(desired_capabilities=Others.dcap,
                                     service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        driver.implicitly_wait(30)
        driver.get(NH.host2)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'search')))
        driver.execute_script("$('[name=code01]').val('%s')" % prefix)
        driver.execute_script("$('[name=code02]').val('%s')" % docnum)
        driver.find_element_by_xpath("//span[contains(text(), 'Search')]").click()
        driver.switch_to.window(driver.window_handles[1])
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'flightListScrollMain')))
        # WebWait().wait_for_page_load(driver, 'flightListScrollMain')
        content = bs4(driver.page_source, 'html.parser')
        # for debugging only - erase when not needed
        driver.save_screenshot('./Log/NH_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
    except Exception, e:
        driver.save_screenshot(
            './Log/NH_except_%s-%s_%s.png' % (prefix, docnum, datetime.today().strftime('%Y%m%d_%H%M%S')))
        traceback.print_exc(file=sys.stdout)
    finally:
        driver.quit()

    portlet = list(content.find_all('div', class_='portlet-body')[2].stripped_strings) # assumed 2 is booking flight
    d = {}
    port, aircode = False, 0
    flight = []
    for i in range(len(portlet)):
        if re.search(r'^[A-Z]{3}$', portlet[i]) and not port:
            d['_dep_port'] = sanitize(portlet[i])
            port = True
        elif re.search(r'^[A-Z]{3}$', portlet[i]) and port:
            d['_dest_port'] = sanitize(portlet[i])
            port = False
        if 'STD' in portlet[i]:
            d['_std'] = NH.arrange_time(re.search(r'[a-zA-Z\d\s\-\|\:]{19}\(STD\)', sanitize(portlet[i])).group()[:-5])
            d['_sta'] = NH.arrange_time(re.search(r'[a-zA-Z\d\s\-\|\:]{19}\(STA\)', sanitize(portlet[i])).group()[:-5])
        if 'ATD' in portlet[i]:
            d['_atd'] = NH.arrange_time(re.search(r'[a-zA-Z\d\s\-\|\:]{19}\(ATD\)', sanitize(portlet[i])).group()[:-5])
            d['_ata'] = NH.arrange_time(re.search(r'[a-zA-Z\d\s\-\|\:]{19}\(ATA\)', sanitize(portlet[i])).group()[:-5])
        if 'ETD' in portlet[i]:
            d['_etd'] = NH.arrange_time(re.search(r'[a-zA-Z\d\s\-\|\:]{19}\(ETD\)', sanitize(portlet[i])).group()[:-5])
            d['_eta'] = NH.arrange_time(re.search(r'[a-zA-Z\d\s\-\|\:]{19}\(ETA\)', sanitize(portlet[i])).group()[:-5])
        if re.search(r'[A-Z\d]{6}', portlet[i]) and aircode == 0:
            d['air_code'] = portlet[i]
            aircode += 1
        elif re.search(r'[A-Z\d]{6}', sanitize(portlet[i])) and aircode != 0:
            d['airline_comp'] = 'NH'
            flight.append(d)
            d = {}
            d['air_code'] = portlet[i]
            aircode += 1
        if i == len(portlet)-1:
            d['airline_comp'] = 'NH'
            flight.append(d)

    return flight


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