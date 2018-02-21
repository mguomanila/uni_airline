#!/usr/bin/env python
#coding=utf-8
'''
:author: marlon
'''
from django.conf.urls import url

import AA
import CA, CM, CV
import CZ, EK, HU, KE
import KL, KZ
import track_trace
import QR, NH2


urlpatterns = [
    url(r'^AA/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', AA.index),  # OK
    url(r'^CA/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', CA.index),   # OK
    url(r'^CM/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', CM.index),  # OK
    url(r'^CV/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', CV.index),
    url(r'^CZ/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', CZ.index),  # OK
    url(r'^EK/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', EK.index),  # OK
    url(r'^HU/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', HU.index),
    url(r'^QR/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', QR.index), # OK
    url(r'^KE/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', KE.main),
    url(r'^KL/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', KL.index),  # site not working!
    url(r'^KZ/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', KZ.index),  # OK
    url(r'^track/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', track_trace.index),
    url(r'^NH/(?P<prefix>[0-9]{3})-(?P<docnum>[0-9]{8})', NH2.index), # OK 
]
