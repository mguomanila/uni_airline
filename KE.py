#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for KE
'''
import sys
import requests
from bs4 import BeautifulSoup as bs4
import re
from datetime import datetime


def get_aircode(li):
    return li[0].split('/')[0].strip()


def replace_mon(s):
    return s.upper().replace('JAN', '01').replace('FEB', '02').replace('MAR', '03').replace('APR', '04').replace('MAY', '05').replace('JUN', '06').replace('JUL', '07').replace('AUG', '08').replace('SEP', '09').replace('OCT', '10').replace('NOV', '11').replace('DEC', '12')


def get_formatted_time(t):
    '''
    :param t  listed time in raw format
    :return [std, sta, etd, eta, atd, ata] listed string time in correct format
    '''
    # todo include only atd/ata, ... etd/eta...sta/std will add later
    context = t[2]
    if len(context) == 0:
        return ['', '', '', '', '', '']
    atd = context[4] + '/' + context[7] +'/'+datetime.today().strftime('%Y')# date + time
    ata = context[8]+'/'+datetime.today().strftime('%Y')
    atd = format(datetime.strptime(replace_mon(atd), '%d%m/%H:%M/%Y').strftime('%Y-%m-%d %H:%M:%S'))
    ata = format(datetime.strptime(replace_mon(ata), '%d%m/%H:%M/%Y').strftime('%Y-%m-%d %H:%M:%S'))
    return ['', '', '', '', atd, ata]


def get_port(p):
    '''
    :param p: listed raw string
    :return: [dep_port, dest_port] listed port
    '''
    return re.search(r'[A-Z]{3}/[A-Z]{3}', p[1]).group().split('/')

def arrange_flight_info(table):
    '''
    :param table:
    :return flight:
    '''
    table_flightsched = table[0]
    table_flightcontent = table[1]
    flight = []
    for i in range(0, len(table_flightsched), 2):
        flight.append([table_flightsched[i], table_flightsched[i+1]])
    # assumed arrangement of table2 is multiple of 11
    # change this if the airlines changed.
    temp = []
    for m in range(len(flight)):
        for o in range(11):
            # append only group of 11 items
            if (m*11+o)<len(table_flightcontent):
                temp.append(table_flightcontent[m*11+o])
            else: break
        flight[m].append(temp)
        temp = []

    return flight


def filter_flight_info(table):
    '''
    :param table: raw table list
    :return: list flight content
    '''
    flight_content = []
    temp = []
    for i in range(len(table)):
        if 'Flight Schedule' in table[i]:
            n = i + 1
            while 'Piece/Weight' not in table[n]:
                temp.append(table[n])
                n += 1
            flight_content.append(temp) # flight schedule
            temp = []
        if 'Routing Information' in table[i] and 'Status' in table[i+16]:
            n = i+16+1
            while 'Cargo Status' not in table[n]:
                temp.append(table[n])
                n += 1
            flight_content.append(temp)  # Routing Information
            temp = []
    return arrange_flight_info(flight_content)


def post(flight_content):
    '''
    :param flight_content:
    :return: printout flight content
    '''
    print 'air KE length %d' % len(flight_content[0]) #
    for content in flight_content:
        _std, _sta, _etd, _eta, _atd, _ata = get_formatted_time(content)
        _dep_port, _dest_port = get_port(content)
        print 'air_code %s' % get_aircode(content)
        print '_std %s' % _std
        print '_sta %s' % _sta
        print '_etd %s' % _etd
        print '_eta %s' % _eta
        print '_atd %s' % _atd
        print '_ata %s' % _ata
        print '_dep_port %s' % _dep_port
        print '_dest_port %s' % _dest_port
        print 'airline_comp %s' % 'KE'


def main(prefix, docnum):
    '''
    :param prefix:
    :param docnum:
    :return: string flight information for php to process
    '''
    # prefix= '064'
    # docnum = '93433966'
    _data = {"pid": "5", "version": "eng", "awb_no": prefix + docnum, "multiAwbNo": prefix + docnum}
    resp = requests.post('http://cargo.koreanair.com/ecus/trc/servlet/TrackingServlet?version=eng', data=_data)
    site_content = bs4(resp.content, 'html.parser')

    # filter only 'Routing Information'
    table = [content.stripped_strings for content in site_content.find_all('table') if 'Routing Information' in content.stripped_strings]
    tab = [list(text) for text in table if text is not None]
    for m in range(len(tab)):
        for content in tab[m]:
            if 'Booking Confirmed' in content:
                table = tab[m]
                break
    # cleanup
    flight_content = filter_flight_info(table)

    # send the information to php
    post(flight_content) # yahoo!


if __name__ == '__main__':
    a = sys.argv[1]
    if a:
        prefix = a[0:3]
        docnum = a[3:11]
    try:
        main(prefix, docnum)
    except:
        exit(1)