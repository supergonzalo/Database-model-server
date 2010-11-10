import datetime
import os
from metar import Metar
import pickle
import urllib2
from BeautifulSoup import BeautifulStoneSoup
import sqlite3
import subprocess
import re, fnmatch
import etolib



def cday(date):			#Day of the year
	return float(date.strftime('%j'))
	
def tomonth(month):
	if month=='Jan': return 1
	if month=='Feb': return 2
	if month=='Mar': return 3
	if month=='Apr': return 4
	if month=='May': return 5
	if month=='Jun': return 6
	if month=='Jul': return 7
	if month=='Aug': return 8
	if month=='Sep': return 9
	if month=='Oct': return 10
	if month=='Nov': return 11
	if month=='Dec': return 12
	
def present(filename):				#looks for a filename in a directory
	for file in os.listdir('./'):
		if fnmatch.fnmatch(filename,file):
		
			return True
	return False

log=list()

BASE_URL = "http://weather.noaa.gov/pub/data/observations/metar/cycles/"
os.chdir('../')
home=os.getcwd()
#cargar en library las estaciones a revisar

now=datetime.datetime.now()
print str(now)
now=datetime.datetime.now()-datetime.timedelta(0,0,0,0,0,1,0)
cycle='%02d'%(now.hour)
os.chdir(home+'/reports')
if present(cycle+"Z.TXT"):
	proc = subprocess.Popen(["rm", cycle+"Z.TXT"])
	proc.communicate()
proc = subprocess.Popen(["wget", BASE_URL+cycle+"Z.TXT"])
print 'llamando wget %s' % BASE_URL+cycle+"Z.TXT"
proc.communicate()
f=open(cycle+"Z.TXT")
metardata=f.readlines()
f.close()
os.chdir(home)
aux=dict()
for line in metardata:
	if line[0:4].isalpha():
		aux[line[0:4]]=line		#aux diccionario 'metarcode': reporte

try:
	connc = sqlite3.connect(home+'/db/peko')
	c = connc.cursor()
	rows=c.execute('select * from stations').fetchall()
except:
	print "Problema accediendo a la base de datos de estaciones"
contador=0

for row in rows:
	contador=contador+1
	obs=''
	precipitation=str(0.0)
		
	if row[0] in aux:
		print 'Procesando %s (%s/%s)' % (row[0],contador,len(rows))
		try:
			#Tengo nuevos datos metar
			#report = line.strip()
			#print 'Metar a estudiar:%s'%aux[row[0]]
			obs = Metar.Metar(str(aux[row[0]]))
			#print "station: %s" % obs.station_id
			# The 'time' attribute is a datetime object
			#if obs.time:
			#	print "time: %s" % obs.time.ctime()
			# The 'temp' and 'dewpt' attributes are temperature objects
			if obs.temp:
				daytemp= obs.temp.string("C")
			if obs.dewpt:
				dewpoint= obs.dewpt.string("C")
				
			# The wind() method returns a string describing wind observations
			# which may include speed, direction, variability and gusts.
			if obs.wind_speed:
				wind=obs.wind() #knots
			# The 'press' attribute is a pressure object.
			if obs.press:
				pressure= obs.press.string("mb")
			# The 'precip_1hr' attribute is a precipitation object.
			if obs.precip_1hr:
				precipitation=obs.precip_1hr.string("in")
		except :
			print "Error retrieving METAR: ",row[0],"\n"
		

	if obs=='':				#No data, lets ask WUNDERGROUND
		city=str(row[2] + ',' +row[1])
		print "Lets try %s \n"% city
		try:
			city = city.replace(' ', '%20')
			url = "http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query=%s"%city
			page = urllib2.urlopen(url)
			soup = BeautifulStoneSoup(page)
			daytemp = soup.find("temp_c").string
			wind= soup.find("wind_mph").string
			rh= soup.find("relative_humidity").string
			pressure= soup.find("pressure_mb").string
			dewpoint= soup.find("dewpoint_c").string
			obs='WUNDERGROUND'
			#armar estructura de datos
		except:
			print "-------> Error in SOUP"
		
	if daytemp != None and obs!='':
		try:
			daytemp=re.findall('\d{1,3}.\d{1,3}|\d{1,3}',str(daytemp))[0]
		except:
			print 'daytemp %s' % daytemp
		try:
			dewpoint=re.findall('\d{1,3}.\d{1,3}|\d{1,3}',str(dewpoint))[0]
		except:
			dewpoint=float(daytemp)*0.9
		try:
			wind=float(re.findall('\d{1,3}.\d{1,3}|\d{1,3}',str(wind))[0])
			if obs == 'WUNDERGROUND':
				wind=wind*0.869	#mph to knots
		except:
			wind=0.1
		try:
			pressure=re.findall('\d{1,4}.\d{1,4}|\d{1,4}',str(pressure))[0]
		except:
			pressure=1013
		try:
			precipitation=re.findall('\d{1,4}.\d{1,4}|\d{1,4}',str(precipitation))[0]
			precipitation=float(precipitation)*254.0
		except:
			precipitation=0
		etowind=etolib.etownd([row[0],now.year,cday(now),cycle,daytemp,dewpoint,wind,float(pressure),str(precipitation)])
		command='select * from %s where year=%s and day=%s and cycle=%s'%(row[0],now.year,cday(now),cycle)
		c.execute(command)
		if c.fetchone():
			command="delete from %s where year=%s and day=%s and cycle=%s"%(str(row[0]),now.year,cday(now),cycle)
			c.execute(command)
		command="insert into %s values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"%(row[0],now.year,cday(now),cycle,daytemp,dewpoint,wind,pressure,str(precipitation), etowind)
		c.execute(command)
		connc.commit()

if cycle=='00':
	print 'calcular la eto diaria'
	
	stat=c.execute('select * from stations').fetchall()
	for each in stat:
		day=int(cday(now))-1
		try:
		
			buff="select max (temperature) from (select * from %s where year=%s and day=%s)"%(each[0],now.year,day)
			maxtemp=float(c.execute(buff).fetchone()[0])
			buff="select avg (temperature) from (select * from %s where year=%s and day=%s)"%(each[0],now.year,day)
			medtemp=float(c.execute(buff).fetchone()[0])
			buff="select min (temperature) from (select * from %s where year=%s and day=%s)"%(each[0],now.year,day)
			mintemp=float(c.execute(buff).fetchone()[0])
			buff="select avg (windsp) from (select * from %s where year=%s and day=%s)"%(each[0],now.year,day)
			medwind=float(c.execute(buff).fetchone()[0])
			buff="select avg (pressure) from (select * from %s where year=%s and day=%s)"%(each[0],now.year,day)
			medpress=float(c.execute(buff).fetchone()[0])
			buff="select sum (etowind) from (select * from %s where year=%s and day=%s)"%(each[0],now.year,day)
			etowind=float(c.execute(buff).fetchone()[0])
			buff="select sum (precipitation) from (select * from %s where year=%s and day=%s)"%(each[0],now.year,day)
			precipitation=float(c.execute(buff).fetchone()[0])
		except:
		
			print "DATA ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
		rsmrow=etolib.eto([each, maxtemp, mintemp, medtemp, etowind, precipitation, day, medwind, medpress,now.year])
		c.execute('select * from rsm where codigo=? and year=? and day=?',(each[0],now.year,day))
		if c.fetchone():
			c.execute('delete from rsm where codigo=? and year=? and day=?',(each[0],now.year,day))
		c.execute("insert into rsm values (?,?,?,?,?,?,?,?,?,?,?,?)",rsmrow)
		print "Terminado: %s"%each[0]
		connc.commit()
c.close()
print str(datetime.datetime.now())
os.chdir(home+'/bin/')
