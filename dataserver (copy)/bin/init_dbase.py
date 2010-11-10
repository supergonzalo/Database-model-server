import os,re,math,sqlite3

info_file= 'METAR.txt'
model_file='model.TXT'

def convert(data):
	mult=1
	temp=data.split('-')
	grad=float(temp[0])
	hemisf=temp[1][-1]
	if hemisf == 'W' or hemisf=='S':
		mult=float(-1.0)
	minutes=float(re.findall('\d*',temp[1])[0])
	return [mult*(grad+minutes/60.0), hemisf,mult*(grad+minutes/60.0)*math.pi/180.0]

def get_station(data):	#creates a dictionary with climate station info
	#data = line.split(';')
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
	return {'latitude':latitude ,'hemisf':hemisf, 'longitude':longitude, 'medisf': medisf,'latrad':latrad,'longrad':longrad, 'altitude':altitude,'city':city1,'country':city2,'code':name,'metar':metar,'factor':factor}

#abrir reporte en /reports
os.chdir('../')
home=os.getcwd()
f=open(home+'/info/'+model_file)
model=f.readlines()
f.close()
	
#abrir metar en /info
f=open(home+'/info/'+info_file)
temp=f.readlines()
f.close()
#parsear datos
metar=dict()
for i in range(len(temp)):
	line=temp[i].split(';')
	metar[line[0]]=get_station(line)		
		
#para cada central en el reporte, obtener datos de la central en metar

stations=dict()

for line in model:
	if line[0:4] in metar:
		stations[line[0:4]]=metar[line[0:4]]

#crear stations.db en /db

conn = sqlite3.connect(home+'/db/peko')

c = conn.cursor()

# Create tables
c.execute('''create table stations(codigo text, country text, city text, lat real, latrad real, hemisf real,
long real, longrad real, medisf real, altitude real, metar text, factor real)''')
c.execute("""create table rsm (codigo text,year real, day real,temperature real, dewpoint real, windsp real, pressure real, precipitation real, etowind real, etorad real, eto real, water real)""")

#crear centrales y guardar centrales con sus datos en stations.db

for element in stations:
	a=stations[element]
	t=[a['code'],a['country'],a['city'],a['latitude'],a['latrad'],a['hemisf'],a['longitude'],a['longrad'],a['medisf'],a['altitude'],a['metar'],a['factor']]		
	buff="create table %s(year real, day real, cycle real,temperature real, dewpoint real, windsp real, pressure real, precipitation real, etowind real)"%a['code']
	c.execute(buff)
	c.execute("""insert into stations values (?,?,?,?,?,?,?,?,?,?,?,?)""",t)

conn.commit()
c.close()
os.chdir(home+'/bin')



