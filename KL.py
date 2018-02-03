#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for KL
'''
import sys
import requests
import simplejson as json
import traceback
from utility import KL

from django.http import HttpResponse, HttpResponseBadRequest


def main(prefix, docnum):
    '''
        :param prefix:
        :param docnum:
        :return: string flight information for php to process
        '''
    _params = {
        'awbId': prefix + '-' + docnum
    }
    resp = requests.get(KL.action, params=_params)
    data = json.loads(resp.content)
    flight = []
    year = data['summary']['date'][-4:]
    for content in data['booking']:
        _std, _sta, _etd, _eta, _atd, _ata = KL.get_formatted_time(content, year)
        d = {
            'air_code': '%s' % content['carrier'] + content['flightNumber'],
            '_std': '%s' % _std,
            '_sta': '%s' % _sta,
            '_etd': '%s' % _etd,
            '_eta': '%s' % _eta,
            '_atd': '%s' % _atd,
            '_ata': '%s' % _ata,
            '_dep_port': '%s' % content['from'],
            '_dest_port': '%s' % content['to'],
            'airline_comp': 'KE'
        }
        flight.append(d)
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
    try:
        main(prefix, docnum)
    except:
        traceback.print_exc(file=sys.stdout)
        exit(1)