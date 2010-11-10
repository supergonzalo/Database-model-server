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
		

