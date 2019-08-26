import urllib2
import json

def get_location(name):
	name = name.lower()
	url = 'http://maps.googleapis.com/maps/api/geocode/json?address='+str(name)+'&sensor=false'
	open_url = urllib2.urlopen(url)
	openjs = json.load(open_url)

	locs = []

	lat = 0
	lon = 0

	for i in openjs['results']:
		for j, k in i.items():
			if j == 'geometry':
				for l, m in k.items():
					if l == 'location':
						lat += m['lat']
						lon += m['lng']

	return lat, lon

print(get_location('bangalore'))
print(get_location('hyderabad'))

with open('weather_token.txt', 'r') as wk:
	weather_token = wk.read()

def get_location(name):
	name = name.lower()
	url = 'http://api.openweathermap.org/data/2.5/weather?q='+str(name)+'&appid='+str(weather_token)
	open_url = urllib2.urlopen(url)
	open_w = json.load(open_url)
	ll = [i[1] for i in open_w['coord'].items()]
	lat = ll[0]
	lon = ll[1]
	return lat, lon

print(get_location('bangalore'))
print(get_location('hyderabad'))