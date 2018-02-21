#coding=utf-8
import requests
import sys
from bs4 import BeautifulSoup as bs4

from utility import NH

def main(prefix, docnum):
    # 获取提单号
    # prefix = '001'
    # docnum = '76496254'
    # 2017年11月28日 10:23:52 maintenance - service unavailable
    NH._data['mawbPrefix'] = prefix
    NH._data['mawbPrefix1'] = prefix
    NH._data['mawbSuffix'] = docnum
    NH._data['mawbSuffix1'] = docnum
    trkTxnValue = '%s-%s' % (prefix, docnum)
    resp = requests.get(NH.action3+trkTxnValue, data=NH._data)
    content = bs4(r.content, 'html.parser')


if __name__ == '__main__':
    a = sys.argv[1]
    if a:
        prefix = a[0:3]
        docnum = a[3:11]

    main(prefix, docnum)