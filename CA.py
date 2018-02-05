# coding=utf-8
'''
@author marlon
Module for AA
'''

import requests
import sys
from bs4 import BeautifulSoup as bs4
import simplejson as json
from copy import deepcopy
import traceback

from utility import CA
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

from django.http import HttpResponse, HttpResponseBadRequest


def update(flight, context):
    '''
    this is a call from utility.Others.detailed()
    :param flight: dict
    :return:
    '''
    prefix = context['prefix']
    docnum = context['docnum']
    CA.flight = main(prefix, docnum)
    new_flight = deepcopy(flight)
    # merge CA flight with other flights:
    for step in range(len(flight)):
        if flight[step] == context:
            for ca_step in range(len(CA.flight)):
                # add all flights that were tracked.
                new_flight.insert(step+ca_step+1, CA.flight[ca_step])
            break  # no need to continue
    return new_flight


def main(prefix, docnum):
    '''
    取得中国航空信息
    '''
    CA._data['orders0'] = docnum
    CA._data['orders10'] = prefix

    key = prefix + docnum
    cached_content = cache.get(key)
    if cached_content is None:
        try:
            r = requests.post(CA.url, data=CA._data, headers=CA._headers)
        except:
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)

        context = bs4(r.content, 'html.parser')
        table = list(context.find_all('table')[-1].stripped_strings)
        flight_info = []
        for seq in range(len(table)):
            if 'Status' in table[seq]:
                CA.start = True
            if CA.start:
                if 'departed' in table[seq]:
                    CA.depart_count += 1
                    CA.receive_count = 0
                elif CA.depart_count==1:
                    if 'CA' in table[seq]:
                        flight_info.append((table[seq], table[seq + 1], table[seq - 7]))
                elif CA.depart_count>1:
                    if 'CA' in table[seq]:
                        flight_info.pop()
                        flight_info.append((table[seq], table[seq + 1], table[seq - 7]))
                if 'received' in table[seq]:
                    CA.receive_count += 1
                    CA.depart_count = 0
                elif CA.receive_count==1:
                    if 'CA' in table[seq]:
                        flight_info.append((table[seq], table[seq + 1], table[seq - 7]))
                elif CA.receive_count>1:
                    if 'CA' in table[seq]:
                        flight_info.pop()
                        flight_info.append((table[seq], table[seq + 1], table[seq - 7]))

        flight = []
        for seq in range(len(flight_info)):
            if not seq%2:  # even 0, 2, 4 departure
                d = {
                    'air_code': '%s' % flight_info[seq][0].split('/')[0],
                    '_std': '%s' % flight_info[seq][1].strip() + ':00' or '',
                    '_etd': '%s' % '',
                    '_eta': '%s' % '',
                    '_atd': '%s' % flight_info[seq][1].strip() + ':00' or '',
                    '_dep_port': '%s' % flight_info[seq][2].strip()[:3] or '',
                    'airline_comp': 'CA'
                }
                flight.append(d)
            else:  # arrival
                d.update({
                    '_sta': '%s' % flight_info[seq][1].strip() + ':00' or '',
                    '_ata': '%s' % flight_info[seq][1].strip() + ':00' or '',
                    '_dest_port': '%s' % flight_info[seq][2].strip()[:3] or '',
                })
        cached_content = flight
        cache.set(key, cached_content, 60 * 60)  # cache for one hour
    return cached_content


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@cache_page(CACHE_TTL)
def index(request, prefix, docnum):
    try:
        return HttpResponse(json.dumps(main(prefix, docnum)), content_type='text/json')
    except:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest('Try again...')


# 获取提单号
if __name__ == '__main__':
    a = sys.argv[1]
    if 'a' in locals():
        prefix = a[0:3]
        docnum = a[3:11]

    main(prefix, docnum)
