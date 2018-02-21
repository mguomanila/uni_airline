#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for HU
'''
import sys
import requests

from django.http import HttpResponse, HttpResponseBadRequest


class HU(object):
    _data = {
        '__EVENTARGUMENT': '',
        '__EVENTTARGET': 'ctl00$MainContent$lkbtnSearch',
        '__EVENTVALIDATION': '/wEdAAinMZKMudXpgVxNmUQifGNBUpob6QWV+0ePPLKLuMoYVEQ4/URILBjbRkpP3t4OA9razJ2OHYyA0a0aGmVrmlg/8QVWSk56v7sD2gj6ScNtuVmyM3+BmLN/o0Tn8qpQ64uW1RSwj8vmkTRGqfQfMk4Rup6wYiszBYE6ppBEK3uq7GUUJEoH/6su8dDsWVrh6NAXZ1kN',
        '__VIEWSTATE': '/wEPDwUJNzk4NzkxNDA4D2QWAmYPZBYCAgIPZBYKAgEPFgIeB1Zpc2libGVoZAICDxYCHgRUZXh0BUg8bGk+PGEgaHJlZj0naHR0cHM6Ly93d3cuaG5hY2FyZ28uY29tL1BvcnRhbC9Mb2dpbi5hc3B4Jz7nmbvlvZU8L2E+PC9saT5kAgMPZBYCAgEPFgIeC18hSXRlbUNvdW50AggWEGYPZBYEZg8VBgAFX3NlbGYUL1BvcnRhbC9EZWZhdWx0LmFzcHgQN0E1MjVDN0ZFNDREOUZFQQzpl6jmiLfpppbpobUESG9tZWQCAw8WAh8CAv////8PZAIBD2QWBGYPFQYABV9zZWxmGS9Qb3J0YWwvU2VydmljZUd1aWRlLmFzcHgQNzIzMzcyQkY4QUUyRTU2Ngzkuqflk4HmnI3liqERUHJvZHVjdCAmIFNlcnZpY2VkAgMPFgIfAgL/////D2QCAg9kFgRmDxUGAAVfc2VsZhsvUG9ydGFsL05ld0luZm9ybWF0aW9uLmFzcHgQQjk4NTk4MDgyOEMzRThENQzmnIDmlrDotYTorq8ETmV3c2QCAw8WAh8CAv////8PZAIDD2QWBGYPFQYABV9zZWxmGy9Qb3J0YWwvVHJhbnNmZXJGbGlnaHQuYXNweBAwRDhDRkY4RUNBQTdBNzE1EuS4rei9rOiIseS9jeafpeivogxUcmFuc2l0IE5vdGVkAgMPFgIfAgL/////D2QCBA9kFgZmDxUGAAVfc2VsZhNqYXZhc2NyaXB0OnZvaWQoMCk7EDI4RUIwNDJDRDVGMEFDMjkM6Iiq54+t5p+l6K+iCFNjaGVkdWxlZAIBDxYCHwEFFTxzIGNsYXNzPSdhcnJvdyc+PC9zPmQCAw8WAh8CAgMWBgIBD2QWAmYPFQYABV9zZWxmGS9Qb3J0YWwvRmxpZ2h0U2VhcmNoLmFzcHgQMTIyMzhDQ0E4RDM5NUVDMgzoiKrnj63mn6Xor6IIU2NoZWR1bGVkAgIPZBYCZg8VBgAGX2JsYW5rImh0dHA6Ly9odS5pbm5vc2tlZC5jb20/bGFuZ19pZD1DSFMQNUU3MDA1NDU4MEE5QzYxNxXlhajnkIPoiKrnur/nvZHnu5zlm74ORmxpZ2h0IE5ldHdvcmtkAgMPZBYCZg8VBgAFX3NlbGZPL1N5c3RlbVNldHRpbmcvUG9ydGFsU2V0dGluZy9TZWFzb25GbGlnaHRzU2V0dGluZy5hc3B4P2FjdGlvbj12aWV3JnJ0eXBlPVBvcnRhbBBGOURFNEI2N0JFRjkyRTkwFeiIquePreWto+iKguaXtuWIu+ihqBFTZWFzb25hbCBTY2hlZHVsZWQCBQ9kFgRmDxUGDnNlbGVjdGVkIGhvdmVyBV9zZWxmFi9Qb3J0YWwvQXdiU2VhcmNoLmFzcHgQNjA2QzVCNjc5NkJDOEVCRAzotKfnianot5/ouKoIVHJhY2tpbmdkAgMPFgIfAgL/////D2QCBg9kFgRmDxUGAAVfc2VsZhUvUG9ydGFsL0ZlZWRiYWNrLmFzcHgQMzY1N0I1RjgxM0M0NDBCQgzlrqLmiLflj43ppogIRmVlZGJhY2tkAgMPFgIfAgL/////D2QCBw9kFgRmDxUGAAVfc2VsZhQvUG9ydGFsL0Fib3V0VXMuYXNweBAyRDlGODA0MzA3NDEzQjgwDOWFs+S6juaIkeS7rAhBYm91dCBVc2QCAw8WAh8CAv////8PZAIHD2QWBAIDDxYCHglpbm5lcmh0bWwFNjxsaSBjbGFzcz0iY3VycmVudF9uYXYiPjxzcGFuPjwvc3Bhbj44ODAtMzE3NTgyNDE8L2xpPmQCBA8WAh8DBaYUPGRpdiBjbGFzcz0ndGFiLWl0ZW0nPjx0YWJsZSBjbGFzcz0icmVzdWx0LWxpc3QgZmxpZ2h0LWxpc3QiPjx0cj48dGQgc3R5bGU9IndpZHRoOiAyMCUiPuiIqueoizwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOiBsZWZ0IiBjb2xzcGFuPSI1Ij5DQU4o5bm/5beeKeKGklBFSyjljJfkuqwp4oaSU1ZPKFNWTzIpPC90ZD48L3RyPjx0cj48dGQgc3R5bGU9IndpZHRoOiAyMCUiPuWTgeWQjTwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOiBsZWZ0IiBjb2xzcGFuPSI1Ij5DT05TT0w8L3RkPjwvdHI+PHRyPjx0ZCBzdHlsZT0id2lkdGg6IDIwJSI+5Lu25pWwPC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246IGxlZnQiPjU8L3RkPjx0ZCBzdHlsZT0id2lkdGg6IDIwJSI+6YeN6YePPC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246IGxlZnQiPjQ3PC90ZD48dGQgc3R5bGU9IndpZHRoOiAyMCUiPuS9k+enrzwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOiBsZWZ0Ij4wLjI1PC90ZD48L3RyPjwvdGFibGU+PGJyIC8+PHRhYmxlIGNsYXNzPSJyZXN1bHQtbGlzdCBzdGF0dXMtbGlzdCI+PHRoZWFkPjx0cj48dGQgc3R5bGU9IndpZHRoOjEwMHB4Ij7nq5nngrk8L3RkPjx0ZCBzdHlsZT0id2lkdGg6IDEyMHB4OyI+5pON5L2c5pe26Ze0IDwvdGQ+PHRkIHN0eWxlPSJ3aWR0aDogOTZweDsiPuaTjeS9nDwvdGQ+PHRkID7oiKrnj63kv6Hmga88L3RkPjx0ZCBzdHlsZT0id2lkdGg6IDMxcHg7Ij7ku7bmlbA8L3RkPjx0ZCBzdHlsZT0id2lkdGg6IDUycHg7Ij7ph43ph49LRzwvdGQ+PC90aGVhZD48L3RyPjx0cj48dGQ+Q0FOKOW5v+W3nik8L3RkPjx0ZD4yMDE2LTA1LTEzIDEzOjMzOjAxPC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+5bey5Yi25Y2VPC90ZD48dGQ+LS08L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij41PC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+NDc8L3RkPiA8L3RyPjx0cj48dGQ+UEVLKOWMl+S6rCk8L3RkPjx0ZD4yMDE2LTA1LTE0IDA5OjM0OjAwPC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+UkNGKOW3suaOpeaUtui0p+eJqSk8L3RkPjx0ZD7lt7Lkuo415pyIMTTml6UxNzozN+aUtuWIsEhVNzgwNuiIquePrei0p+eJqTwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOmNlbnRlcjsiPjU8L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij40NzwvdGQ+IDwvdHI+PHRyPjx0ZD5DQU4o5bm/5beeKTwvdGQ+PHRkPjIwMTYtMDUtMTUgMDA6MDE6MDI8L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij7lh7rlj5E8L3RkPjx0ZD5IVTc4MDYs5bm/5beeLeWMl+S6rCzotbfpo57ml7bpl7TvvJoyMDE2LTA1LTE0IDEyOjU3OjAwLOWIsOi+vuaXtumXtO+8mjIwMTYtMDUtMTQgMTU6NTg6MDA8L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij41PC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+NDc8L3RkPiA8L3RyPjx0cj48dGQ+UEVLKOWMl+S6rCk8L3RkPjx0ZD4yMDE2LTA1LTE3IDA3OjEyOjAwPC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+REVQKOW3suemu+a4ryk8L3RkPjx0ZD7nprvmuK/oiKrnj63vvJpIVTc5ODUvNeaciDE35pelL1BFSy1TVk8s6K6h5YiS5Ye65Y+RMTU6MDAs6K6h5YiS5Yiw6L6+MTg6MDU8L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij41PC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+NDc8L3RkPiA8L3RyPjx0cj48dGQ+U1ZPKFNWTzIpPC90ZD48dGQ+MjAxNi0wNS0xNyAxOToxNjowMDwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOmNlbnRlcjsiPlJDRijlt7LmjqXmlLbotKfniakpPC90ZD48dGQ+5bey5LqONeaciDE35pelMjA6MjnmlLbliLBIVTc5ODXoiKrnj63otKfniak8L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij41PC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+NDc8L3RkPiA8L3RyPjx0cj48dGQ+U1ZPKFNWTzIpPC90ZD48dGQ+MjAxNi0wNS0xNyAyMDoxOTowMDwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOmNlbnRlcjsiPk5GRCjmj5DotKfpgJrnn6UpPC90ZD48dGQ+5bey5LqONeaciDE35pelMjM6MjLpgJrnn6Xmj5DotKc8L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij41PC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+NDc8L3RkPiA8L3RyPjx0cj48dGQ+U1ZPKFNWTzIpPC90ZD48dGQ+MjAxNi0wNS0yMCAxNjoxMDowMDwvdGQ+PHRkIHN0eWxlPSJ0ZXh0LWFsaWduOmNlbnRlcjsiPkRMVijlt7Lmj5DotKcpPC90ZD48dGQ+5bey5LqONeaciDIw5pelMTk6MTPmj5DotKc8L3RkPjx0ZCBzdHlsZT0idGV4dC1hbGlnbjpjZW50ZXI7Ij41PC90ZD48dGQgc3R5bGU9InRleHQtYWxpZ246Y2VudGVyOyI+NDc8L3RkPiA8L3RyPiA8L3RhYmxlPjwvZGl2PjxwIHN0eWxlPSdtYXJnaW4tdG9wOiAzMHB4Oyc+PGEgaHJlZj0nL1BvcnRhbC9Db250YWN0LmFzcHg/aWQ9MycgdGFyZ2V0PSdfYmxhbmsnPuWmgumcgOi3n+i4qui/kOWNleivpue7hueKtuaAge+8jOivt+S4juaIkeS7rOiBlOezuzwvYT48L3A+ZAIID2QWBGYPFgIfAgINFhpmD2QWAmYPFQIjaHR0cDovL3d3dy50cmFjay10cmFjZS5jb20vYWlyY2FyZ28Y6Iiq56m65YWs5Y+45p+l6K+i5rGH5oC7ZAIBD2QWAmYPFQImaHR0cDovL3d3dy5jYXJnb3VwZGF0ZS5jb20vdHJhY2t0cmFjZS8RQ0hBTVDmn6Xor6Lns7vnu59kAgIPZBYCZg8VAhlodHRwOi8vd3d3LnN6YWlycG9ydC5jb20vDOa3seWcs+acuuWcumQCAw9kFgJmDxUCLmh0dHA6Ly93d3cueGlhbWVuYWlycG9ydC5jb20uY24vaGtoeS9oa2h5LmFzcHgM5Y6m6Zeo5py65Zy6ZAIED2QWAmYPFQIlaHR0cDovL3d3dy5wYWN0bC5jb20uY24vY24vaW5kZXguaHRtbAzmtabkuJzmnLrlnLpkAgUPZBYCZg8VAkdodHRwOi8vaHR0cHM6Ly9jaG9ydXMudGhhaWNhcmdvLmNvbS9za3ljaGFpbi9hcHA/c2VydmljZT1wYWdlL253cDpsb2dpbgzms7Dlm73lnLDpnaJkAgYPZBYCZg8VAhdodHRwOi8vODEuOTMuNS45NS9ob21lLwzlt7Tpu47lnLDpnaJkAgcPZBYCZg8VAh5odHRwOi8vamNvbm5lY3QuamFuZGVyaWprLmNvbS8P5p+P5p6XSkRS5Y2h6L2mZAIID2QWAmYPFQIgaHR0cDovL2pldC1haXJ3YXlzLmNvbS9pbmRleC5waHASSmV0LWFpcndheXMg5Y2h6L2mZAIJD2QWAmYPFQIaaHR0cDovL3d3dy5mb3J3YXJkYWlyLmNvbS8SRm9yd2FyZCBBaXIg5Y2h6L2mZAIKD2QWAmYPFQIsaHR0cDovL3d3dy5zaGVyY2FyZ28ucnUvZW5nL291cnNydi9mcmVlX2luZm8P6I6r5pav56eR5LuT5bqTZAILD2QWAmYPFQIcaHR0cDovL3d3dy5wdWxrb3ZvLWNhcmdvLnJ1LxLlnKPlvbzlvpfloKHku5PlupNkAgwPZBYCZg8VAhlodHRwOi8vd3d3LnNhdHNjYXJnby5jb20vD+aWsOWKoOWdoeS7k+W6k2QCAQ8WAh8CAg0WGmYPZBYCZg8VAiNodHRwOi8vd3d3LnRyYWNrLXRyYWNlLmNvbS9haXJjYXJnbwBkAgEPZBYCZg8VAiZodHRwOi8vd3d3LmNhcmdvdXBkYXRlLmNvbS90cmFja3RyYWNlLwVDSEFNUGQCAg9kFgJmDxUCGWh0dHA6Ly93d3cuc3phaXJwb3J0LmNvbS8QU2hlbnpoZW4gQWlycG9ydGQCAw9kFgJmDxUCLmh0dHA6Ly93d3cueGlhbWVuYWlycG9ydC5jb20uY24vaGtoeS9oa2h5LmFzcHgOWGlhbWVuIEFpcnBvcnRkAgQPZBYCZg8VAiVodHRwOi8vd3d3LnBhY3RsLmNvbS5jbi9jbi9pbmRleC5odG1sF1NoYW5naGFpIFB1ZG9uZyBBaXJwb3J0ZAIFD2QWAmYPFQJHaHR0cDovL2h0dHBzOi8vY2hvcnVzLnRoYWljYXJnby5jb20vc2t5Y2hhaW4vYXBwP3NlcnZpY2U9cGFnZS9ud3A6bG9naW4MVGhhaSBBaXJ3YXlzZAIGD2QWAmYPFQIXaHR0cDovLzgxLjkzLjUuOTUvaG9tZS8DV0ZTZAIHD2QWAmYPFQIeaHR0cDovL2pjb25uZWN0LmphbmRlcmlqay5jb20vC0phbiBkZSBSaWprZAIID2QWAmYPFQIgaHR0cDovL2pldC1haXJ3YXlzLmNvbS9pbmRleC5waHALSmV0LWFpcndheXNkAgkPZBYCZg8VAhpodHRwOi8vd3d3LmZvcndhcmRhaXIuY29tLwtGb3J3YXJkIEFpcmQCCg9kFgJmDxUCLGh0dHA6Ly93d3cuc2hlcmNhcmdvLnJ1L2VuZy9vdXJzcnYvZnJlZV9pbmZvCXNoZXJjYXJnb2QCCw9kFgJmDxUCHGh0dHA6Ly93d3cucHVsa292by1jYXJnby5ydS8NcHVsa292by1jYXJnb2QCDA9kFgJmDxUCGWh0dHA6Ly93d3cuc2F0c2NhcmdvLmNvbS8JU2luZ2Fwb3JlZGT5UXQzpnFiVoSeCMctDYMc0lL30g==',
        'ctl00$hdfCurrentNavText': '',
        'ctl00$hdfCurrentNavText_En': '',
        'ctl00$hdfPermissionValue': '',
        'ctl00$hidMsg': '',
        'ctl00$MainContent$txtVerifyCode': '7',
    }
    _headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Host': 'www.hnacargo.com',
        'Referer': 'http://www.hnacargo.com/Portal/AwbSearch.aspx',
    }

def index(request, prefix, docnum):
    try:
        return HttpResponse(main(prefix, docnum))
    except:
        HttpResponseBadRequest('Try again...')


def main(prefix, docnum):
    # prefix = '880'
    # docnum = '3175824'
    HU._data['ctl00$MainContent$txtAwbCode'] = prefix + '-' + docnum
    resp = requests.post('http://www.hnacargo.com/Portal/AwbSearch.aspx', data=HU._data, headers=HU._headers)


if __name__ == '__main__':
    a = sys.argv[1]
    if a:
        prefix = a[0:3]
        docnum = a[3:11]
    try:
        main(prefix, docnum)
    except:
        exit(1)