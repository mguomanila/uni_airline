#!/usr/bin/env python
# coding=utf-8
'''
@author marlon
implementation of ViewSet
'''
from rest_framework import viewsets
import AA as AA_track

global query
query = ''

def queryset(prefix, docnum):
    query = AA_track.main(prefix, docnum)
    return AAApiViewSet


class AAApiViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for listing and creating viewsets
    '''
    global query
    queryset = query
