#!/usr/bin/env python
# -*- coding=utf-8 -*-
'''
:author: marlon
Module for AA
'''
import requests
import sys
import simplejson
from bs4 import BeautifulSoup as bs4
from HTMLParser import HTMLParseError
import traceback
import simplejson as json

from utility import AA
from utility import Others
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

from django.http import HttpResponse, HttpResponseBadRequest


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def main(prefix, docnum):
    '''
    :param prefix:
    :param docnum:
    :return: None
    '''
    AA.data['track3AirwayBills[0].awbCode'] = prefix
    AA.data['track3AirwayBills[0].awbNumber'] = docnum

    try:
        response = requests.post(AA.tracking, data=AA.data, headers=AA.headers)
        search_id = bs4(response.content, 'html.parser').find('div', 'topActions').input['value']
    except HTMLParseError:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    # get airwayBillId
    try:
        response = requests.get(AA.track + search_id)
    except:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    data = simplejson.loads(response.content)
    flight = []
    for items in data["bookedFlightDetailsList"]:
        if isinstance(items, dict):
            d = {
                'prefix': '%s' % prefix,
                'docnum': '%s' % docnum,
                'airline_comp': '%s' % items['airlineIATACode'],
                'air_code': '%s' % (items['airlineIATACode'] + str(items['flightNumber'])),
                'flightNumber': '%s' % items['flightNumber'],
                'departureDate': '%s' % items['departureDate'],
                'flightOrigin': '%s' % items['departureStationCode'],
                '_sta': '%s' % AA.check_sched(items['scheduledArrivalDate'], items['scheduledArrivalTime']),
                '_std': '%s' % AA.check_sched(items['scheduledDepartureDate'], items['scheduledDepartureTime']),
                '_dep_port': '%s' % items['departureStationCode'],
                '_dest_port': '%s' % items['scheduledArrivalAirport']
            }
            flight.append(d)
    return AA.detailed(Others.detailed(flight))


@cache_page(CACHE_TTL)
def index(request, prefix, docnum):
    try:
        return HttpResponse(json.dumps(main(prefix, docnum)), content_type='text/json')
    except:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(json.dumps([{'air_code':'Try again...'}]), content_type='text/json')


if __name__ == '__main__':
    # 获取提单号
    a = sys.argv[1]
    if a:
        prefix = a[0:3]
        docnum = a[3:11]
    main(prefix, docnum)