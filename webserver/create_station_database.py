#!/bin/sh

from django.core.management import setup_environ
import settings

setup_environ(settings)

import os,re,math
from peko.models import *

info_file= 'METAR.txt'

country=['Argentina']


def convert(data):
	mult=1
	temp=data.split('-')
	grad=float(temp[0])
	hemisf=temp[1][-1]
	if hemisf == 'W' or hemisf=='S':
		mult=float(-1.0)
	minutes=float(re.findall('\d*',temp[1])[0])
	return [mult*(grad+minutes/60.0), hemisf,mult*(grad+minutes/60.0)*math.pi/180.0]

def get_station(data):	

	if data[11]=='':
		altitude=10.0		#If there's no data at all we asume the station is @10m
	else:
		altitude=float(data[11])
	city1=data[3]
	city2=data[5]
	[latitude, hemisf,latrad]=convert(data[7])
	[longitude, medisf,longrad]=convert(data[8])
	name=line[0]
	metar=data[14]
	factor=float(data[15])	
	return 	station(code=name,country=city2,city=city1,latitude=latitude,longitude=longitude,latrad=latrad,longrad=longrad,	hemisf=hemisf, medisf=medisf, altitude=altitude, metar=metar, factor= 1)


#abrir metar en /info
f=open('./info/'+info_file)
temp=f.readlines()
f.close()
#parsear datos de las estaciones en country
metar=dict()
for i in range(len(temp)):
	line=temp[i].split(';')
	if line[5] in country:
		get_station(line).save()		
		










