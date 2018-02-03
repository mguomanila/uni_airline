#!/usr/bin/env python
#coding=utf-8
'''
:author: marlon
Models
'''
from django.conf import settings
from django.db import models

class BookingStatus(models.Model):
    JOBNUM = models.CharField(max_length=30, blank=True)
    MASTERNO = models.CharField(max_length=30, blank=True)
    PORTPOL = models.CharField(max_length=30, blank=True)
    PORTDEL = models.CharField(max_length=30, blank=True)
    SHIPNAME = models.CharField(max_length=30, blank=True)

    ETD = models.DateField(blank=True, null=True)
    ETA = models.DateField(blank=True, null=True)
    STD = models.DateField(blank=True, null=True)
    STA = models.DateField(blank=True, null=True)
    ATD =  models.DateField(blank=True, null=True)
    ATA = models.DateField(blank=True, null=True)
    CREATEDDATETIME = models.DateField(auto_now_add=True)
    MODIFIEDDATETIME = models.DateField(auto_now=True)

    def __str__(self):
        return 'BookingStatus'