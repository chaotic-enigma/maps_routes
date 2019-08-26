import json
import dash
import urllib2
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

scenic_style = 'mapbox://styles/chaotic-enigma/cjixdsyk9aem62rm9vh45thvd'

default = 'http://ip-api.com/json'
open_d = urllib2.urlopen(default)
default_js = json.load(open_d)
default_city = default_js['city']

app.layout = html.Div([
	html.H4('Path Finder', style={'textAlign' : 'center'}),
	# html.H6('select style', style={'textAlign' : 'center', 'margin-top' : 40}),
	html.Div([
		html.Div([
			dcc.Input(id='home', placeholder='Home: ', type='text', value=default_city, size=35)
		], className='four columns'),
		html.Div([
			dcc.Input(id='dest', placeholder='Destination: ', type='text', value='', size=35)
		], className='four columns'),
		html.Div([
			dcc.Dropdown(
				id='select-style',
				options=[
					{'label' : 'Basic', 'value' : 'basic'},
					{'label' : 'Outdoors', 'value' : 'outdoors'},
					{'label' : 'Light', 'value' : 'light'},
					{'label' : 'Streets', 'value' : 'streets'},
					{'label' : 'Scenic', 'value' : scenic_style}
				],
				value=scenic_style,
			)
		], className='two columns'),
	], className='row',	style={'textAlign' : 'center'}),
	# html.Hr(),
	html.Div([
		html.Div([
			html.Div([
				html.H5('Travelling mode:', style={'textAlign' : 'center'}),
			]),
			html.Div([
				dcc.RadioItems(
					id='select-mode',
					options=[
						# {'label' : 'Traffic', 'value' : 'traffic'},
						{'label' : 'Driving', 'value' : 'driving'},
						{'label' : 'Cycling', 'value' : 'cycling'},
						{'label' : 'Walking', 'value' : 'walking'},
					],
					value='driving',
					# labelStyle={'display': 'inline-block'}
				),
			])
		], className='three columns', 
		style={'textAlign' : 'center'}),
		html.Div([
			dcc.Graph(id='maplayout')
		], className='nine columns')
	], className='row'),
	html.Div(id='error')
])

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

def map_locations(home, dest):
	initial_lat, initial_lon = get_location(home)
	final_lat, final_lon = get_location(dest)
	return initial_lat, initial_lon, final_lat, final_lon

with open('map_token.txt', 'r') as tk:
	map_token = tk.read()

def get_route(home, dest, travelling_mode):
	initial_lat, initial_lon, final_lat, final_lon = map_locations(home, dest)

	mapurl = 'https://api.mapbox.com/directions/v5/mapbox/' + str(travelling_mode) + '/' + str(initial_lon) + ',' + str(initial_lat) + ';' + str(final_lon) + ',' + str(final_lat) + '?geometries=geojson&access_token=' + str(map_token)
	openmap = urllib2.urlopen(mapurl)
	mapjs = json.load(openmap)

	lons = []
	lats = []

	for ks in mapjs['routes']:
		for k, v in ks.items():
			if k == 'geometry':
				for eachk, eachv in v.items():
					if eachk == 'coordinates':
						for eachloc in eachv:
							lons.append(eachloc[0])
							lats.append(eachloc[1])

	return lats, lons

# print(get_route('bagepalli', 'hindupur', 'driving'))

@app.callback(
	Output('maplayout', 'figure'),
	[Input('home', 'value'), Input('select-style', 'value'), 
		Input('dest', 'value'), Input('select-mode', 'value')]
)
def path_finder(home, style_name, dest, travelling_mode):
	try:
		lats, lons = get_route(home, dest, travelling_mode)
		data = go.Data([
			go.Scattermapbox(
				lat=lats,
				lon=lons,
				mode='lines',
				line=dict(width=2),
				marker=dict(
					size=5,
				),
        text='{} to {} : {}'.format(str(home).title(), str(dest).title(), str(travelling_mode).title()),
        hoverinfo='text'
			)
		])

		layout = go.Layout(
			height=550,
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
					lat=lats[0],
					lon=lons[0]
				),
				pitch=0,
				zoom=5,
				style=style_name
			),
		)

		return {'data' : data, 'layout' : layout}

	except Exception as e:
		print(str(e))
		return html.Div([
			html.H5('Unsuccessful')
		])

external_css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
for css in external_css:
	app.css.append_css({'external_url' : css})

external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
for js in external_js:
	app.scripts.append_script({'external_url' : js})

if __name__ == '__main__':
	app.run_server(debug=True)
