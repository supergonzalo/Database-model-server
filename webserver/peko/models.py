from django.db import models

# Create your models here.

class station(models.Model):
	code=models.CharField(max_length=5)
	country=models.CharField(max_length=30)
	city=models.CharField(max_length=30)
	latitude=models.FloatField()
	longitude=models.FloatField()
	latrad=models.FloatField()
	longrad=models.FloatField()
	hemisf=models.CharField(max_length=3)
	medisf=models.CharField(max_length=3)
	altitude=models.FloatField()
	metar=models.CharField(max_length=5)
	factor=models.FloatField()
	def __unicode__(self):
	        return self.code



class measure(models.Model):
	date=models.DateField()
	cycle=models.PositiveSmallIntegerField()
	temperature=models.FloatField()
	dewpoint=models.FloatField()
	windsp=models.FloatField()
	pressure=models.FloatField()
	precipitation=models.FloatField()
	etowind=models.FloatField()
	code=models.ForeignKey(station)



class rsm(models.Model):
	code=models.ForeignKey(station)
	date=models.DateField(primary_key=True)
	temperature=models.FloatField()
        dewpoint=models.FloatField()
        windsp=models.FloatField()
        pressure=models.FloatField()
        precipitation=models.FloatField()
        etowind=models.FloatField()
	etorad=models.FloatField()
	eto=models.FloatField()
	water=models.FloatField()


