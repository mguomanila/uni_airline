#!/usr/bin/env python
# coding=utf-8
'''
@author marlon
implementation of serialized/deserialized by the API
'''
from rest_framework import serializers
from .models import BookingStatus


class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStatus
        fields = ('MASTERNO', 'JOBNUM', 'PORTPOL', 'PORTDEL', 'SHIPNAME', 'ETD', 'ETA', 'ETD', 'STD', 'STA', 'ATD', 'ATA')
