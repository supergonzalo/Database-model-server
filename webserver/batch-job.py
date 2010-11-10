#!/bin/sh

from django.core.management import setup_environ
import settings

import os

setup_environ(settings)

from peko.models import *

import datetime
from lib import Metar
from lib import etolib
import re, fnmatch
import urllib2
from BeautifulSoup import BeautifulStoneSoup

################################
import pickle

import sqlite3
import subprocess
################################

BASE_URL = "http://weather.noaa.gov/pub/data/observations/metar/cycles/"

def cday(date):			#Day of the year
	return float(date.strftime('%j'))
	
def tomonth(month):
	values={'Jan': 1,'Feb': 2,'Mar': 3,'Apr': 4,'May': 5,'Jun': 6,'Jul': 7,'Aug': 8,'Sep': 9,'Oct': 10,'Nov': 11,'Dec': 12}
	return values[month]
	
def present(filename):				#looks for a filename in a directory
	for file in os.listdir('./'):
		if fnmatch.fnmatch(filename,file):
			return True
	return False

log=list()


#cargar en library las estaciones a revisar

now=datetime.datetime.now()
print str(now)
now=datetime.datetime.now()-datetime.timedelta(0,0,0,0,0,1,0)
cycle='%02d'%(now.hour)
home=os.getcwd()
os.chdir('./info/reports/')
####################################################
if present(cycle+"Z.TXT"):
	proc = subprocess.Popen(["rm", cycle+"Z.TXT"])
	proc.communicate()
proc = subprocess.Popen(["wget", BASE_URL+cycle+"Z.TXT"])
print 'llamando wget %s' % BASE_URL+cycle+"Z.TXT"
proc.communicate()
####################################################
f=open(cycle+"Z.TXT")
metardata=f.readlines()
f.close()
os.chdir(home)
aux=dict()
for line in metardata:
	if line[0:4].isalpha():
		aux[line[0:4]]=line		#aux diccionario 'metarcode': reporte sin procesar
		
###########################################################


#si en metardata tengo dato nuevo para las estaciones que tengo en station list, guardarlo en measure

for station in station.objects.all():
	wund=0
	precipitation=str(0.0)
	if station.code in aux:

		print 'Procesando %s\n' % station.code
		try:
			obs = Metar.Metar(str(aux[station.code]))
			if obs.temp:
				daytemp= obs.temp.string("C").strip(' C')
			if obs.dewpt:
				dewpoint= obs.dewpt.string("C").strip(' C')
			if obs.wind_speed:
				if obs.wind().strip(' NWSEatknots')=='':
					wind='0'
				else:
					wind=obs.wind().strip(' NWSEatknots') #knots
			if obs.press:
				pressure= obs.press.string("mb").strip(' mb')
			if obs.precip_1hr:
				precipitation=obs.precip_1hr.string("in").strip(' in')
		except :
			print "Error retrieving METAR: %s\n"%station.code
			wund=1
	else:
		wund=1
	
	if wund==1:
		#buscar en weather underground
		city=str(station.city + ',' +station.country)
		print "Lets try %s en Weather Underground\n"% city
		try:
			city = city.replace(' ', '%20')
			url = "http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query=%s"%city
			page = urllib2.urlopen(url)
			soup = BeautifulStoneSoup(page)
			daytemp = soup.find("temp_c").string.strip(' C')
			wind= soup.find("wind_mph").string.strip(' mph')
			rh= soup.find("relative_humidity").string
			pressure= soup.find("pressure_mb").string.strip(' mb')
			dewpoint= soup.find("dewpoint_c").string.strip(' C')
			wund=0
		except:
			print "-------> Error obteniendo datos"
	if wund ==0:

		etowind=etolib.etownd([station.code,now.year,cday(now),cycle,daytemp,dewpoint,wind,float(pressure),str(precipitation)])
		try:
			measure.objects.get(date=now, cycle=cycle,code=station)
			m=measure(date=now, cycle=cycle, temperature=daytemp, dewpoint=dewpoint,windsp=wind, pressure= pressure, precipitation=precipitation,etowind= etowind, code=station)
			m.save()
			
		except:
			m=measure.objects.create(date=now, cycle=cycle, temperature=daytemp, dewpoint=dewpoint,windsp=wind, pressure= pressure, precipitation=precipitation,etowind= etowind, code=station)



	
