#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for KZ
'''
import sys
import requests
import re
from bs4 import BeautifulSoup as bs4
import traceback
import simplejson as json

from utility import KZ
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

from django.http import HttpResponse, HttpResponseBadRequest

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def main2index(prefix, docnum):
    data = {}
    data['uc:txtGuia'] = '%s-%s' % (prefix, docnum)
    cookies = {
        u'__utma': u'226526552.1720680984.1513820696.1513820696.1513820696.1',
        u'__utmz': u'226526552.1513820696.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        u'__utmc': u'226526552', u'__utmt': u'1',
        u'__utmb': u'226526552.1.10.1513820696'
    }
    action = u'http://www.copacargo.com/homepage.aspx?lang=en'
    method = ''
    return main(action, method, data, cookies)


def main(action, method, data, cookies):
    # url = 'http://eservices.copaair.com/webtrackingcyc/default.aspx?g1=230-97462805&theme=cargo&lang=en&langkeepThis=true&'
    data['g1'] = data['uc:txtGuia'] + '&theme='
    data['theme'] = 'cargo' + '&lang='
    data['lang'] = 'en' + '&langkeepThis='
    data['langkeepThis'] = 'true' + '&'
    url = 'http://eservices.copaair.com/webtrackingcyc/default.aspx?g1='+data['g1'] + '' +data['theme'] + data['lang'] + data['langkeepThis']
    resp = requests.post(url)
    context = bs4(resp.content, 'html.parser')
    table = context.find_all('table')[1]
    text = []
    for tag in list(table):
        if type(tag)==type(table):
            #if re.search(r'\d{2}/\d{2}/\d{4}.*\nDelivered', tag.text):
            #   text.append(re.search(r'\d{2}/\d{2}/\d{4}.*\nDelivered.*', tag.text).group())
            if re.search(r'\d{2}/\d{2}/\d{4}.*\nArrived', tag.text):
                text.append(re.search(r'\d{2}/\d{2}/\d{4}.*\nArrived.*', tag.text).group())
            if re.search(r'\d{2}/\d{2}/\d{4}.*\nDeparture', tag.text):
                text.append(re.search(r'\d{2}/\d{2}/\d{4}.*\nDeparture.*', tag.text).group())
            #if re.search(r'Flight:\s?CM\s?\d{3,4}', tag.text):
            #    text.append(re.search(r'Flight:\s?CM\s?\d{3,4}', tag.text).group())
    airline, temp, temp2 = [], [], {}
    i = 0
    for txt in text:
        if 'Departure' in txt:
            if re.search(r'\w{2}\s?\d{3,4}', txt):
                temp.append(re.search(r'\w{2}\s?\d{3,4}', txt).group()) # air_code
            else:
                temp.append('')
            if re.search(r'\d{1,2}/\d{1,2}/\d{4}\s?\d{1,2}:\d{1,2}:\d{1,2}\s?[A-Z.]{4}', txt):
                temp.append(re.search(r'\d{1,2}/\d{1,2}/\d{4}\s?\d{1,2}:\d{1,2}:\d{1,2}\s?[A-Z.]{4}', txt).group())  # _std
            else:
                temp.append('')
            if re.search(r'[A-Z]{3}', txt):
                temp.append(re.search(r'[A-Z]{3}', txt).group())  # _dep_port
            else:
                temp.append('')
            temp2['Departure'] = temp
            temp = []
        if 'Arrived' in txt:
            if re.search(r'\d{1,2}/\d{1,2}/\d{4}\s?\d{1,2}:\d{1,2}:\d{1,2}\s?[A-Z.]{4}', txt):
                temp.append(re.search(r'\d{1,2}/\d{1,2}/\d{4}\s?\d{1,2}:\d{1,2}:\d{1,2}\s?[A-Z.]{4}', txt).group())  # _sta
            else:
                temp.append('')
            if re.search(r'[A-Z]{3}', txt):
                temp.append(re.search(r'[A-Z]{3}', txt).group())  # _dest_port
            else:
                temp.append('')
            temp2['Arrived'] = temp
            temp = []
        if 'Arrived' in temp2 and 'Departure' in temp2:
            airline.append(temp2)
            temp2 = {}

    array = []
    # json response
    for i in range(len(airline)):
        d = {
            'air_code': '%s' % airline[i]['Departure'][0],
            '_std': '%s' % '',
            '_sta': '%s' % '',
            '_etd': '%s' % '',
            '_eta': '%s' % '',
            '_atd': '%s' % KZ.check_time(airline[i]['Departure'][1]),
            '_ata': '%s' % KZ.check_time(airline[i]['Arrived'][0]),
            '_dep_port': '%s' % airline[i]['Departure'][-1],
            '_dest_port': '%s' % airline[i]['Arrived'][-1],
            'airline_comp': 'KZ'
        }
        array.append({'%s' % i: d})
    return {'KZ': array} #json


@cache_page(CACHE_TTL)
def index(requests, prefix, docnum):
    try:
        return HttpResponse(json.dumps(main2index(prefix, docnum)), content_type='text/json')
    except:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest('Try again...')