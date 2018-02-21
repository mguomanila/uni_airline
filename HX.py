#!/usr/bin/env python
# coding: utf-8
'''
:author: marlon
Module for HX
'''
import sys
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import re
import traceback
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from django.http import HttpResponse, HttpResponseBadRequest

