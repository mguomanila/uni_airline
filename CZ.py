#coding=utf-8
import requests
import sys
from bs4 import BeautifulSoup as bs4
import re
import traceback
import simplejson as json

from utility import CZ
from django.http import HttpResponse, HttpResponseBadRequest

def open_text():
    with open('CZ.txt') as f:
        for line in f:
            a, b = line.strip(',\n').split(': ')
            CZ._data.update({a.strip('\''): b.strip('\'')})

def main(prefix, docnum):
    #获取提单号
    # prefix= '784'
    # docnum = '27400365'
    open_text()
    CZ._data['ctl00$ContentPlaceHolder1$txtPrefix'] = prefix
    CZ._data['ctl00$ContentPlaceHolder1$txtNo'] = docnum
    r = requests.post(CZ.url+CZ.prefix+prefix+CZ.awbno+docnum+CZ.menuid+CZ.lang, data=CZ._data)
    content = bs4(r.content, 'html.parser')
    table = content.find_all('table')
    status = list(table[2].stripped_strings)
    flight = []
    for i in range(len(status)):
        if re.search(r'[\dA-Z]{4,10}', status[i]) and re.search(r'[-\d]{8,10}', status[i+1]):
            d = {
                'air_code': '%s' % status[i],
                '_dep_port': '%s' % status[i - 2],
                '_dest_port': '%s' % status[i - 1],
                'airline_comp': 'CZ',
            }
            flight.append(d)

    status = list(table[4].stripped_strings)
    j = 0
    for i in range(len(status)):
        if 'Cargo has been loaded' in status[i]:
            flight[j].update({'_atd': '%s' % status[i - 3]})
            flight[j].update({'_std': '%s' % status[i - 3]})
        if 'Flight has arrived' in status[i]:
            flight[j].update({'_ata': '%s' % status[i - 3]})
            flight[j].update({'_sta': '%s' % status[i - 3]})
            j += 1
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
    print main(prefix, docnum)