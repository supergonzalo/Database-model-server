#!/bin/sh

from django.core.management import setup_environ
import settings

setup_environ(settings)

from peko.models import *
import datetime
from lib import etolib

backlog=3								#Cantidad de dias hacia atras que se van a procesar.
now=datetime.datetime.now()

for stat in station.objects.all():
	
	start=now-datetime.timedelta(backlog,0,0,0,0,0,0)
	
	while start < now:
		#try:	
			
		etolib.eto(station.objects.filter(code=stat)[0],start)
		start=start+datetime.timedelta(1,0,0,0,0,0,0)
		#except:
		#	pass
