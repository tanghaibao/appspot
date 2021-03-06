#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import sys
import traceback

from django.core.management import setup_environ
sys.path.append("/home/bao/public_html/")
from bao import settings
setup_environ(settings)

from bao.athaliana.models import Syntelog 

import csv
reader = csv.DictReader(open("data/data.csv"))
   
for i, row in enumerate(reader):
    if i % 1000 == 0: print >>sys.stderr, i, "records loaded"
    
    try:
        Syntelog.objects.get_or_create(**row)
    except:
        print row

