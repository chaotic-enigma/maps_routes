import json
import dash
import urllib2
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

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

with open('map_token.txt', 'r') as tk:
	map_token = tk.read()

home_user = 'bommanahalli'
dest_1 = 'lakkasandra'
dest_2 = 'domlur'
dest_3 = 'marathahalli'
dest_4 = 'doddakannelli'
dest_5 = 'jayanagar'

destinations = [dest_1, dest_2, dest_3, dest_4, dest_5]

def map_locations(home, dest):
	initial_lat, initial_lon = get_location(home)
	final_lat, final_lon = get_location(dest)
	return initial_lat, initial_lon, final_lat, final_lon

def get_route(home, dest):
	initial_lat, initial_lon, final_lat, final_lon = map_locations(home, dest)

	mapurl = 'https://api.mapbox.com/directions/v5/mapbox/driving/'+str(initial_lon)+','+str(initial_lat)+';'+str(final_lon)+','+str(final_lat)+'?geometries=geojson&access_token='+str(map_token)
	openmap = urllib2.urlopen(mapurl)
	mapjs = json.load(openmap)

	lons = []
	lats = []

	for ks in  mapjs['routes']:
		for k, v in ks.items():
			if k == 'geometry':
				for eachk, eachv in v.items():
					if eachk == 'coordinates':
						for eachloc in eachv:
							lons.append(eachloc[0])
							lats.append(eachloc[1])

	return lats, lons

dest_locations = []
for dest in destinations:
	dest_locations.append(get_route(home_user, dest))

def weather_details(name):
	name = name.lower()
	url = 'http://api.openweathermap.org/data/2.5/weather?q='+str(name)+'&appid='+str(weather_token)
	open_url = urllib2.urlopen(url)
	open_w = json.load(open_url)

	weather_type = open_w['weather'][0]['description']

	temp = open_w['main']['temp']
	celsius = temp - 273
	celsius = round(celsius, 2)

	ws = open_w['wind']['speed']

	return str(name).title() + '  ' + str(weather_type) + '  ' + str(celsius) + ' C  ' + str(ws) + ' mph'

def highlight_multiple_paths():
	locations = []
	for item in range(len(dest_locations)):
		lats, lons = dest_locations[item]
		locations.append(
			go.Scattermapbox(
				lat=lats,
				lon=lons,
				mode='lines',
				line=dict(width=2),
				marker=go.Marker(
					size=5
				),
				text=weather_details(destinations[item]),
				hoverinfo='text'
			)
		)

	layout = go.Layout(
		height=700,
	  autosize=True,
	  showlegend=False,
	  hovermode='closest',
	  geo=dict(
		  projection=dict(type="equirectangular"),
	  ),
	  mapbox=dict(
	    accesstoken=map_token,
	  	bearing=1,
			center=dict(
				lat=12.8984,
				lon=77.6179
			),
			pitch=0,
			zoom=12,
			style='mapbox://styles/chaotic-enigma/cjixdsyk9aem62rm9vh45thvd'
		),
	)

	return {'data' : locations, 'layout' : layout}

app.layout = html.Div([
	dcc.Graph(id='multipaths', figure=highlight_multiple_paths())
])

if __name__ == '__main__':
	app.run_server(debug=True)
