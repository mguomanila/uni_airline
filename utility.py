#!/usr/bin/env python
# coding=utf-8
'''
implementation of common utilities and libraries
@author marlon
@copyright 2017 Unilogistics(Xiamen) Co., Ltd
'''
import requests
import simplejson as json
import re
from copy import deepcopy
from datetime import datetime, date
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Others(object):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
    )

    @classmethod
    def detailed(cls, flight):
        new_flight = deepcopy(flight)
        # travel thru every airline once
        for context in flight:
            if 'CA' in context['air_code']:
                from CA import update as CA_update
                new_flight = CA_update(flight, context)
            if 'NH' in context['air_code']:
                from NH2 import update as NH2_update
                new_flight = NH2_update(new_flight, context)
        return new_flight


class CA(object):
    url = 'http://www.airchinacargo.com/en/search_order.php'
    _data = {
        'orders11':'999',
        'orders1': '请输入8位数字',
        'orders12':'999',
        'orders2':'请输入8位数字',
        'orders13': '999',
        'orders3': '请输入8位数字',
        'section': '0-0001-0003-0081',
        'orders9': '78oi' # checkcode
        #'usercheckcode': '8wp8'
    }
    _headers = {
        'Connection': 'Keep-Alive',
        'Cookie': '',
        'Referer': 'http://www.airchinacargo.com/en/search_order.php',
        'User-Agent':  "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        'Host': 'www.airchinacargo.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    start = False
    depart_count = 0
    receive_count = 0


class AA(object):
    data = {
        'track3AirwayBills[1].awbCode': '',
        'track3AirwayBills[1].awbNumber': '',
        'track3AirwayBills[2].awbCode': '',
        'track3AirwayBills[2].awbNumber': '',
        'track3Search': 'Track',
        'trackingPath': 'track3'
    }
    tracking = 'https://www.aacargo.com/AACargo/tracking/'
    flight = []
    url = 'http://www.aacargo.com/'
    track = tracking + 'masterAirWayBillDetails?airwayBillId='
    headers = {
        'Connection': 'Keep-Alive',
        'Cookie': '',
        'Host': 'www.aacargo.com',
        'Referer': tracking,
        'User-Agent':  "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        'Accept': '*/*'
    }
    flight_info_track_url = u'https://www.aacargo.com/AACargo/FlightFo/getHistoryFlightInfo?flightNumberStr='
    flight_date = u'&flightDate='
    flight_origin = u'&flightOrigin='

    @classmethod
    def treat_pm(cls, t):
        if 'P' in t and re.search(r'\d{2}/\d{2}/\d{4}\s\d:\d{2}', t):
            c = int(t[11:12])
            c += 12
            t = t[:11] + str(c) + t[12:]
        elif 'P' in t and '12' not in t[11:13] and re.search(r'\d{2}/\d{2}/\d{4}\s\d{2}:', t):
            c = int(t[11:13])
            c += 12
            t = t[:11] + str(c) + t[13:]

        return t.replace('.', '')[:-3]

    @classmethod
    def check_time(cls, t):
        # arrange year in standard form
        '''
        u'12/18/2017 4:08:00 P.M.' -> '2017/12/18 16:08:00'
        u'12/17/2017 6:20:00 P.M.' -> '2017/12/17 00:12:00'
        :param t:
        :return:
        '''
        if t == '' or t is None:
            return ''
        else:
            return format(datetime.strptime(t, '%m/%d/%Y %I:%M:%S %p').strftime('%Y-%m-%d %H:%M:%S'))

    @classmethod
    def arrange_time(cls, *t):
        '''
        u'November 7, 2017'  +  u'11:11 AM' -> '2017/11/07 11:11:00'
        u'November 7, 2017'  +  u'11:11 PM' -> '2017/11/07 23:11:00'
        :param t:
        :return:
        '''
        if t == '' or t is None:
            return ''
        else:
            t = list(t)
            time = ''
            for context in t:
                time += context + ' '
            time = time.strip()
            return cls.check_time(datetime.strptime(time, '%B %d, %Y %I:%M %p').strftime('%m/%d/%Y %I:%M:%S %p'))

    @classmethod
    def check_sched(cls, *args):
        '''
        checks if value is not None concatenates and returns, otherwise returns ''
        :param args: list of arguments
        :return: string
        u'12/19/2017'  +   u'09:00 PM'  =>
        '''
        txt = ''
        if len(args) > 0:
            for a in args:
                if a is not None:
                    txt += a + ' '
                else:
                    return ''
        txt = txt.strip()
        if re.search(r'\d{1,2}/\d{1,2}/\d{4}\s?\d{1,2}:\d{1,2}\s?[A-Z.]{2,4}', txt):
            if len(txt) == 19:
                txt = txt[:-3] + ':00' + txt[-3:]
            if len(txt) == 21:
                txt = txt[:-5] + ':00' + txt[-5:]
        return cls.check_time(txt)

    @classmethod
    def get_url_date(cls, dat):
        '''
        1514264400000L -> 11/05/2017
        :param dat:
        :return:
        '''
        return date.fromtimestamp(long(dat)/1000).strftime('%m/%d/%Y')

    @classmethod
    def detailed(cls, flight):
        update_flight = []
        for fl in list(flight):
            if 'AA' in fl['airline_comp']:
                response = requests.get(cls.flight_info_track_url+fl['flightNumber']
                                        +cls.flight_date+cls.get_url_date(fl['departureDate'])
                                        +cls.flight_origin+fl['flightOrigin'],
                                        headers=cls.headers)
                update_flight.append(json.loads(response.content))
        return cls.arrange_flight(update_flight, flight)

    @classmethod
    def arrange_flight(cls, update_flight, flight):
        temp_flight = deepcopy(flight)
        for content in update_flight:
            d = {
                'air_code': '%s' % ('AA' + content['flightNumber']),
                '_etd': '%s' % cls.arrange_time(content['fmtDepartedDate'], content['fmtEstimatedDepartedTime']),
                '_eta': '%s' % cls.arrange_time(content['fmtArrivalDate'], content['fmtEstimatedArrivalTime']),
                '_atd': '%s' % cls.arrange_time(content['fmtDepartedDate'], content['fmtDepartedTime']),
                '_ata': '%s' % cls.arrange_time(content['fmtArrivalDate'], content['fmtArrivalTime']),
                '_dep_port': '%s' % content['originAirportCde'],
                '_dest_port': '%s' % content['destinationAirportCde'],
            }
            for i in range(len(flight)):
                if d['air_code'] == flight[i]['air_code']:
                    temp_flight[i].update(d)  # update flight info
        return temp_flight


class KL(object):
    @classmethod
    def get_formatted_time(cls, t, year):
        std, sta, etd, eta, atd, ata = '', '', '', '', '', ''
        ata = t['arrivalDate']['dateLT'] + ' ' + year
        atd = t['departureDate']['dateLT'] + ' ' + year
        if atd and ata:
            atd = format(datetime.strptime(atd, '%d %b %H:%M %Y').strftime('%Y-%m-%d %H:%M:%S'))
            ata = format(datetime.strptime(ata, '%d %b %H:%M %Y').strftime('%Y-%m-%d %H:%M:%S'))
        return [std, sta, etd, eta, atd, ata]


class EK(object):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
    )

    @classmethod
    def replace_mon(cls, s):
        return s.replace('JAN', '01')\
            .replace('FEB', '02')\
            .replace('MAR', '03')\
            .replace('APR', '04')\
            .replace('MAY','05')\
            .replace('JUN', '06')\
            .replace('JUL', '07')\
            .replace('AUG', '08')\
            .replace('SEP', '09')\
            .replace('OCT', '10')\
            .replace('NOV', '11')\
            .replace('DEC', '12')

    @classmethod
    def format_content(cls, t):
        '''
        t = u'EK9871/29 DEC 2017, CAN-DWC, STD 29 DEC 2017-08:55, ETD 29 DEC 2017-08:55, STA 29 DEC 2017-13:30, ETA 29 DEC 2017-13:30'
        :param t: text
        :return:
        '''
        air, port, std, sta, etd, eta, atd, ata = '', '', '', '', '', '', '', ''
        for content in t.split(', '):
            if re.search(r'[A-Z0-9]{5,8}/', content):
                air = content.split('/')[0]
            elif re.search(r'[A-Z]{3}-[A-Z]{3}', content):
                port = content.split('-')
            elif 'STD' in content:
                std = format(datetime.strptime(cls.replace_mon(content), 'STD %d %m %Y-%H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            elif 'STA' in content:
                sta = format(datetime.strptime(cls.replace_mon(content), 'STA %d %m %Y-%H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            elif 'ETD' in content:
                etd = format(datetime.strptime(cls.replace_mon(content), 'ETD %d %m %Y-%H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            elif 'ETA' in content:
                eta = format(datetime.strptime(cls.replace_mon(content), 'ETA %d %m %Y-%H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            elif 'ATD' in content:
                atd= format(datetime.strptime(cls.replace_mon(content), 'ATD %d %m %Y-%H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            elif 'ATA' in content:
                ata = format(datetime.strptime(cls.replace_mon(content), 'ATA %d %m %Y-%H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            if not std or not sta:
                std = etd
                sta = eta
        return [air, port, std, sta, etd, eta, atd, ata]

    @classmethod
    def pop(cls, d):
        temp = deepcopy(d)
        if not temp['_std']:
            temp.pop('_std')
        if not temp['_sta']:
            temp.pop('_sta')
        if not temp['_etd']:
            temp.pop('_etd')
        if not temp['_eta']:
            temp.pop('_eta')
        if not temp['_atd']:
            temp.pop('_atd')
        if not temp['_ata']:
            temp.pop('_ata')
        return temp

    @classmethod
    def arrange(cls, flight_update):
        # cleansed from repeated data
        new_flight = []
        temp = deepcopy(flight_update)

        for seq in range(len(flight_update)-1, 0,  -1):
            if flight_update[seq]['air_code'] != flight_update[seq - 1]['air_code']:
                new_flight.append(temp[seq])
            else:
                temp[seq-1].update(temp[seq])
        new_flight.append(temp[seq-1])  # append the last one!
        return new_flight

    @classmethod
    def waiting(cls, s, n=None):
        MUL = 10 ** 6
        start = time.time()
        if n:
            for i in xrange(n):
                cls.waiting(s)
        else:
            for i in xrange(int(s) * MUL):
                pass
        end = time.time()
        print 'time in %s' % ((end - start) * 10 ** 3)


class CM(object):
    '''
    china is blocked
    '''
    host = 'http://eservices.copaair.com'
    url = 'http://eservices.copaair.com/webtrackingcyc/default.aspx?'
    g1 = 'g1='  # + prefix + '-' + docnum +
    lang = '&theme=cargo&lang=en&langkeepThis=true'


class CZ(object):
    _data = {}
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"
    url = 'http://tang.cs-air.com/EN/WebFace/Tang.WebFace.Cargo/AgentAwbBrower.aspx?'
    prefix = 'awbprefix='
    awbno = '&awbno='
    menuid = '&menuid=1'
    lang = '&lan=en-us'


class KZ(object):
    @classmethod
    def check_time(cls, t):
        # arrange year in standard form
        '''
        u'12/18/2017 4:08:00 P.M.' -> '2017/12/18 16:08:00'
        u'12/17/2017 6:20:00 P.M.' -> '2017/12/17 00:12:00'
        :param t:
        :return:
        '''
        if 'P.M.' in t and len(t[11:]) == 12:
            c = int(t[11:12])
            c += 12
            t = t[:11] + str(c) + t[12:]
        return format(datetime.strptime(t.replace('.', ''), '%m/%d/%Y %H:%M:%S %p').strftime('%Y-%m-%d %H:%M:%S'))


class NH(object):
    host = 'https://shar.ana.co.jp'
    host2 = 'http://www.anacargo.jp/en/int/index.html'
    action1 = 'https://cargo.ana.co.jp/anaicoportal/portal/trackshipments'
    action2 = 'https://cargo.ana.co.jp/anaicoportal/portal/searchFlights'
    action3 = 'https://cargo.ana.co.jp/anaicoportal/portal/trackshipments?trkTxnValue='
    _data = {
        'awbType': 'MAWB',
        'dispatch': 'retrieveMAWBSearchResult',
        'guestEntry': 'shipmentStatus',
        'hawbNumber1': '',
        'hawbNumber2': '',
        'hawbNumber3': '',
        'hawbNumber4': '',
        'hawbNumber5': '',
    }
    #resp = requests.get(host)
    #resp.headers['Cookie'] = resp.headers['Set-Cookie']
    #resp.headers.pop('Set-Cookie')
    #_headers = resp.headers

    @classmethod
    def arrange_time(cls, t):
        '''
        u'06-Jan 2018 | 06:28'
        :param t:
        :return:
        '''
        return datetime.strptime(t, '%d-%b %Y | %H:%M').strftime('%Y-%m-%d %H:%M:%S')


class CV(object):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (X11; Linux x86_64) " \
                                                "AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87"


class QR(object):
    action = 'http://www.qrcargo.com/doTrackShipmentsAction'
    ref = 'http://www.qrcargo.com/trackshipment?docNumber='
    host = 'www.qrcargo.com'
    dtype = 'MAWB'
    doctype = '&docType='
    docpre = '&docPrefix='


    # url = ('http://www.qrcargo.com/trackshipment?docNumber=92876803&docType=MAWB&docPrefix=157')
    _headers = {
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
        'Host': host,
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
    }


    @classmethod
    def get_port(cls, p):
        '''
        :param p: listed raw string
        :return: [dep_port, dest_port] listed port
        '''
        if len(p) == 2:
            dest_port = re.search(r'[A-Z]{3}', p[0]).group()
            dep_port = re.search(r'[A-Z]{3}', p[1]).group()
        else:
            dep_port = re.search(r'[A-Z]{3}', p[0]).group()
            dest_port = ''
        return [dep_port, dest_port]

    @classmethod
    def get_formatted_time(cls, t):
        '''
        :param t  listed time in raw format
        :return [std, sta, etd, eta, atd, ata] listed string time in correct format
        '''
        # todo include only atd/ata, ... etd/eta...sta/std will add later
        if len(t)==2:
            ata = cls.replace_mon(re.search(r'[0-9]{2}-[a-zA-Z]{3}-[0-9]{4}\s[0-9]{2}:[0-9]{2}', t[0]).group())
            atd = cls.replace_mon(re.search(r'[0-9]{2}-[a-zA-Z]{3}-[0-9]{4}\s[0-9]{2}:[0-9]{2}', t[1]).group())
            atd = format(datetime.strptime(atd, '%d-%m-%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            ata = format(datetime.strptime(ata, '%d-%m-%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            std = etd = atd
            sta = eta = ata
        else:
            atd = cls.replace_mon(re.search(r'[0-9]{2}-[a-zA-Z]{3}-[0-9]{4}\s[0-9]{2}:[0-9]{2}', t[0]).group())
            atd = format(datetime.strptime(atd, '%d-%m-%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S'))
            etd = std = atd
            sta = eta = ata = ''

        return [std, sta, etd, eta, atd, ata]

    @classmethod
    def get_aircode(cls, li):
        return re.search(r'[A-Z]{2}\s[0-9]{3,4}', li[0]).group()

    @classmethod
    def replace_mon(cls, s):
        return s.upper().replace('JAN', '01').replace('FEB', '02').replace('MAR', '03').replace('APR', '04').replace(
            'MAY', '05').replace('JUN', '06').replace('JUL', '07').replace('AUG', '08').replace('SEP', '09').replace(
            'OCT', '10').replace('NOV', '11').replace('DEC', '12')


class KL(object):
    action = 'https://afklcargo.com/resources/tnt/singleAwbDetails'
