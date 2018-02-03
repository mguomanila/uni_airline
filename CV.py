#coding=utf-8
import requests
import sys
from bs4 import BeautifulSoup as bs4

from django.http import HttpResponse, HttpResponseBadRequest


def main(prefix, docnum):
    # prefix= '172'
    # docnum = '11141114'
    payload = {"awbnumber":prefix+'-'+docnum,"requester":"CV","airwaybillsubmit":"ok"}
    
    r = requests.post('http://cdmp.champ.aero/ttwfe/search.do', payload)
    soup = bs4(r.content, 'html.parser')
    
    #读取所有航班号、起始、目的港及计划起飞、降落，实际起飞降落
    lis = []
    
    for ul in soup.find_all("ul", class_="mlsInfo airplaneWidth"):
        for li in ul.find_all('li'):
            if li.find('ul'):
                break
            lis.append(li)
        count = 1
    
    for li in lis:
        if li.text.encode("utf-8").strip() != '':
            if count == 4 or count == 8:
                print li.text.encode("utf-8").strip() + '<hr />'
            else:
                print li.text.encode("utf-8").strip() + '<br />'
            count += 1
    
    #追踪信息
    trackinfo = soup.find('table', class_='mlsTable')
    
    print str(trackinfo).replace('class="mlsTable"', 'class="table table-bordered table-condensed"')


def index(request, prefix, docnum):
    try:
        return HttpResponse(main(prefix, docnum))
    except:
        HttpResponseBadRequest('Try again...')


#获取提单号
if __name__ == '__main__':
    a = sys.argv[1]
    if a:
        prefix = a[0:3]
        docnum = a[3:11]
    try:
        main(prefix, docnum)
    except:
        exit(1)