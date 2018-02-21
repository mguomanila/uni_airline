#!/usr/bin/env python
# coding=utf-8
import requests
import sys
from bs4 import BeautifulSoup as bs4
import re
import simplejson as json
import traceback
from utility import AA, CM
from django.core.cache import cache
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page

from django.http import HttpResponse, HttpResponseBadRequest

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def main(prefix, docnum):
    '''
    :prefix = '230'
    :docnum = '97462013'
    '''
    search = prefix + '-' + docnum
    headers = requests.head(CM.url+search+CM.lang).headers
    nexturl = CM.host + headers['Location']

    key = prefix + docnum
    cached_content = cache.get(key)
    if cached_content is None:
        r = requests.get(nexturl)
        soup = bs4(r.content, 'html.parser')

        airline_content = [string for string in soup.stripped_strings
                            if re.match(r'\d{2}/\d{2}/\d{2}', string)
                            or re.match(r'^\D{3}$', string)
                            or 'Departure' in string
                            or 'Arrived' in string
                            or 'Flight' in string
                            or 'CM' in string]

        len_airline_content = len(airline_content)
        content = []
        # reverse the table, early first
        for i in range(len_airline_content-1, -1, -1):
            if 'Arrived' in airline_content[i]:
                content.append('%s' % str(airline_content[i+1]))
                content.append('%s' % AA.check_time(str(airline_content[i-1]).replace('.', '')))
            if 'Departure' in airline_content[i]:
                content.append('%s' % str(airline_content[i+3]).replace(' ', ''))
                content.append('%s' % str(airline_content[i+1]))
                content.append('%s' % AA.check_time(str(airline_content[i-1]).replace('.', '')))

        clean_content = []
        for i in range(len(content)):
            if 'CM' in content[i] and 'CM' not in content[i+3]:
                # mean arrival/departure pair
                # there should be 5 levels of information
                clean_content.append(content[i:i+5])
            if 'CM' in content[i] and 'CM' in content[i+3]:
                # extra flight info
                # save only 3 levels of information
                clean_content.append(content[i:i+3]+['', ''])

        flight = []
        for i in range(len(clean_content)-1, -1, -1):
            flight.append({
                'air_code': '%s' % clean_content[i][0],
                '_std': '%s' % '',
                '_sta': '%s' % '',
                '_etd': '%s' % '',
                '_eta': '%s' % '',
                '_atd': '%s' % clean_content[i][2],
                '_ata': '%s' % clean_content[i][4],
                '_dep_port': '%s' % clean_content[i][1],
                '_dest_port': '%s' % clean_content[i][3],
                'airline_comp': 'CA'
            })
        cached_content = flight
        cache.set(key, cached_content, 60 * 60)  # cache for one hour
    return cached_content


@cache_page(CACHE_TTL)
def index(request, prefix, docnum):
    try:
        return HttpResponse(json.dumps(main(prefix, docnum)), content_type='text/json')
    except:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest('Try again...')

#获取提单号
if __name__ == '__main__':
    a = sys.argv[1]
    
    if a:
        prefix = a[0:3]
        docnum = a[3:11]

    main(prefix, docnum)