#!/bin/sh

from django.core.management import setup_environ
import settings
setup_environ(settings)
from peko.models import *
import datetime

backlog=5                                 
deadline=datetime.datetime.now()-datetime.timedelta(backlog,0,0,0,0,0,0)
measure.objects.all().filter(date__lt=deadline).delete()
