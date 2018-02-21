#!/usr/bin/env python
# coding=utf-8
'''
:author: marlon
Module for QR
'''
import requests
import sys
import simplejson as json
from bs4 import BeautifulSoup as bs4
import traceback

from utility import QR
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

from django.http import HttpResponse, HttpResponseBadRequest

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def main(prefix, docnum):
    # prefix = '157'
    # docnum = '92876803'
    QR._headers['Cookie'] = requests.get('http://'+QR.host).headers.get(
        'Set-Cookie',
        'BIGipServerqrcargo-webportal-pool=1261771692.20480.0000;'
    ) + ' __utmt=1; __utma=76335189.2071932267.1517376664.1517376664.1517376664.1;' \
        ' __utmb=76335189.1.10.1517376664; __utmc=76335189;' \
        ' __utmz=76335189.1517376664.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
    QR._headers['Referer'] = QR.ref + docnum + QR.doctype + QR.dtype + QR.docpre + prefix
    cargoTrackingRequest = {
        "cargoTrackingRequestSOs": [{
            "documentType": QR.dtype,
            "documentPrefix": prefix,
            "documentNumber": docnum}]
    }

    resp = requests.post(QR.action, data=json.dumps(cargoTrackingRequest), headers=QR._headers)
    content = bs4(resp.content, 'html.parser')
    table = list(content.find_all('table')[-1].stripped_strings)  # assuming last one is impt
    flight_content = []
    temp = []
    for i in range(len(table)):
        if 'ARR' in table[i]:
            temp.append(table[i+3])
        if 'DEP' in table[i]:
            temp.append(table[i+3])
            flight_content.append(temp)
            temp = []

    flight = []
    for content in flight_content:
        _std, _sta, _etd, _eta, _atd, _ata = QR.get_formatted_time(content)
        _dep_port, _dest_port = QR.get_port(content)
        flight.append({
             'air_code':  '%s' % QR.get_aircode(content),
             '_std': '%s' % _std,
             '_sta': '%s' % _sta,
             '_etd': '%s' % _etd,
             '_eta': '%s' % _eta,
             '_atd': '%s' % _atd,
             '_ata': '%s' % _ata,
             '_dep_port': '%s' % _dep_port,
             '_dest_port': '%s' % _dest_port,
             'airline_comp': '%s' % 'QR',
        })
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
    try:
        main(prefix, docnum)
    except:
        exit(1)