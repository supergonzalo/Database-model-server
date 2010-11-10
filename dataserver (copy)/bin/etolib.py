import math, sys, sqlite3, os

###################################### Psychrometric constant 

def gammma (p=101.3):
#Calculates gamma based on atm pressure
	return (0.665e-3)*p


###################################### Slope Vapour Pressure Curve 

def delta (t=20):

	return 4098*edt(t)/((t+237.3)**2)

###################################### (Aux) saturation vapour pressure

def edt(t):
	return 0.6108*math.exp(17.27*t/(t+237.3))

###################################### Inverse distance Sun-Earth

def dr(j):
	return 1+0.033*math.cos(2*math.pi*j/365)

###################################### Solar Declination

def dmin(j):
	return (0.409*math.sin(2*math.pi*j/365-1.39))

###################################### Sunset hour angle

def ws(j, lat):
	p=-math.tan(lat)*math.tan(dmin(j))
	if abs(p)>1:
		p=1
	return math.acos(p)

###################################### Extraterrestrial radiation

def ra(j,lat):

	return 24*60*0.082*dr(j)*(ws(j,lat)*math.sin(lat)*math.sin(dmin(j))+math.cos(lat)*math.cos(dmin(j))*math.sin(ws(j,lat)))/math.pi

###################################### Daylight hours

def N(j,lat):

		return 24*ws(j,lat)/math.pi

###################################### Solar radiation Rs

def rs(krs,tmax,tmin,ra):
	

	return (krs*ra*(abs(tmax-tmin))**0.5)

###################################### RS0

def rso(z,j,lat):

	return (0.75+2*z/100000)*ra(j,lat)

###################################### Rnl 

def rnl(tmed,ex_rad,rs,rso):

	return (tmed*(0.34-0.14*ex_rad)**0.5)*(1.35*rs/rso-0.35)


###################################### Rn

def rn(rns,rnl):
	return rns-rnl


def etownd(foo):	
	hourly=list()
	tmean=float(foo[4])
	windspeed=float(foo[6])*0.5144		#Es knots to m/s
	es=edt(tmean)
	ea=edt(float(foo[5]))
	deltatmean=delta(tmean)
	gamma=gammma(foo[7])
	etowh= gamma*(900.0/24.0)*windspeed*(es-ea)/((deltatmean+gamma*(1+0.34*windspeed))*(tmean+273.0)) # mm/hour
	if etowh < 0:
		etowh=0.0
	return etowh

def eto(foo): #foo es una lista de tuplas con los datos de la estacion (daily)
#	[0(codigo, pais, ciudad, lat, latrad, hemisf, long, longrad, medisf,
#   altura, codigo, factor), 1tmax, 2tmin,3tmed,4 etowind, 5precipitacion, 6dia, 
#   7windmedio, 8presion,9year]


	krs=0.18		#0.16 interior, 0.19 coast, Rs=0.7Ra-4 island
	j=float(foo[6])
	wmed=foo[7]
	tmax=foo[1]
	tmin=foo[2]
	tmed=foo[3]
	etowind=foo[4]
	lat=float(foo[0][4])
	z=float(foo[0][9])
	factor=float(foo[0][11])	
	p=float(foo[8])/10.0	#mb to hp
	d=delta(tmed)
	g=gammma(p)
	esuba= edt(tmed)
	DT=d/(d+g*(1+0.34*wmed))
	dr(j)
	dmin(j)
	ws(j, lat)
	ext_radiation=ra(j,lat)
	N(j,lat)
	surface_rad=rs(krs,tmax,tmin,ext_radiation) #Mean surface radiation
	pot_rad=rso(z,j,lat)
	#rnl(tmed,esuba,surface_rad,pot_rad)
	radiation=rn(pot_rad,surface_rad)
	#print radiation
	etorad=DT*(0.408*radiation)	
	#print "ETORAD=%s" % etorad
	if etorad<0:
		etorad=0
	
	#print "\nETO WindTODAY: " +str(etowind)+"\nETOradTODAY: " +str(etorad)+"\nETOTODAY: " +str(float(etorad)+float(etowind))+"\nEstimada: " +str(0.0023*(tmed+17.8)*ext_radiation*(tmax-tmin)**(0.5))
#codigo text,year real, day real,temperature real, dewpoint real, windsp real, pressure real, precipitation real, etowind real, etorad real, eto real, water real
	return [foo[0][0],foo[9],j,tmed,0,wmed,p,foo[5],etowind,etorad,etowind+etorad,0]
	
