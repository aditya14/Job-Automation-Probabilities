# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import dash_table
import dash_colorscales
from colour import Color

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# The Mapbox Access Token
mapbox_access_token = "pk.eyJ1IjoiYWRpMDAwMTQiLCJhIjoiY2p1dTdkbWY4MGVpaTQzbzFva2cweWxseCJ9.t96aiUa7p4oBmGy2XDtrkg"

df = pd.read_csv('automation_data.csv', sep=',', engine='python')
lat_long = pd.read_csv('statelatlong.csv', sep=',', engine='python')
categoryCode = pd.DataFrame(df['SOC'].str.slice(start=0, stop=2))   

jobs_criteria = df[lat_long['State']][(df.Probability >= 0.7) & (df.Probability <=1.0)].sum()
total = df[lat_long['State']].sum()
percentage = ((jobs_criteria/total)*100).values.astype(str)
lat_long['percentage'] = percentage

green = Color("#08db28")
colors = (list(green.range_to(Color("#db0808"),52)))

legend_range = ['<10%', '11-20%', '21-30%', '31-40%', '41-50%', '51-60%', '61-70%', '71-80%', '81-90%', '91-100%']

app.title = 'The Automation Wave'

# Main Div
app.layout = html.Div(
    children=[
        
        # Header
        html.Div([
            html.H1([
                'The Automation Wave'
            ],
                style = {
                    'textAlign': 'center',
                    'fontWeight': 'bold'
                }
            ),
            html.H4([
                'A visual analysis of how many jobs are getting automated away'
            ],
                style = {
                    'textAlign': 'center',
                }
            ),
        ], style = {
            'width': '100%;',
            'backgroundColor': '#0645aa',
            'color': '#f5f5f5',
            'padding': '10px'
        }),
        # Map and slider div
        html.Div(
            style = {
                'width': '100%',
            },
            children = [
                # Map Canvas
                html.Div([
                    dcc.Graph(
                        id = 'state-choropleth',
                        config={'scrollZoom': True},
                    )
                ]),
                html.Div ([
                    # Slider container
                    html.Div(
                        style = {
                            'width': '100%',
                            'height': '80px',
                            'backgroundColor': 'rgba(32,32,32,0.8)',
                            'padding': '20px 0px',
                            'color': '#f5f5f5',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'marginBottom': '20px',
                            'boxShadow': '1px 1px 3px rgba(32,32,32,0.8)',
                        },
                        children = [
                            # Range slider div
                            html.Div(
                                style = {
                                    'width': '95%',
                                    'height': '30px',
                                    'margin': 'auto',
                                },
                                children = [
                                    dcc.RangeSlider(
                                        id = "range-slider",
                                        min = 0,
                                        max = 1.0,
                                        value = [0.7,1.0],
                                        step = .01,
                                        marks = {
                                            0: {'label': '0.0', 'style': {'color': '#00FF00'}},
                                            0.1: {'label': '0.1', 'style': {'color': '#33ff00'}},
                                            0.2: {'label': '0.2', 'style': {'color': '#66ff00'}},
                                            0.3: {'label': '0.3', 'style': {'color': '#ccff00'}},
                                            0.4: {'label': '0.4', 'style': {'color': '#ccff00'}},
                                            0.5: {'label': '0.5', 'style': {'color': '#FFFF00'}},
                                            0.6: {'label': '0.6', 'style': {'color': '#FFCC00'}},
                                            0.7: {'label': '0.7', 'style': {'color': '#ff9900'}},
                                            0.8: {'label': '0.8', 'style': {'color': '#ff6600'}},
                                            0.9: {'label': '0.9', 'style': {'color': '#FF3300'}},
                                            1: {'label': '1.0', 'style': {'color': '#ff0000'}},
                                        },
                                        included = True,
                                        vertical = False,
                                        allowCross = False,
                                    ),
                                ]
                            ),
                            html.H4(id='slider-text'),
                        ]
                    ),
                    # Overview Div
                    html.Div(
                        style = {
                            'width': '100%',
                            'backgroundColor': 'rgba(235,235,235,0.8)',
                            'color': '#303030',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'boxShadow': '1px 1px 3px rgba(235,235,235,0.8)',
                        },
                        children = [
                            # Stats Inner Parent Div
                            html.Div([
                                html.H3(["Overview"], style = { 'padding': '20px', 'margin': '0', 'backgroundColor': '#0645aa', 'borderRadius': '10px 10px 0 0', 'color': '#f5f5f5'}),
                                # Stats Inner Flexbox 1
                                html.Div([
                                    # Stat Item 1
                                    html.Div([
                                        html.P("Total Jobs in the Dataset"),
                                        html.H4(id = 'total-jobs', style = {'fontWeight': 'bold'}),
                                    ], style={'width':'33%'}),
                                    # Stat Item 2
                                    html.Div([
                                        html.P("Total Jobs in Selected Range"),
                                        html.H4(id = 'range-jobs', style = {'fontWeight': 'bold'}),
                                    ], style={'width':'33%'}),
                                    # Stat Item 3
                                    html.Div([
                                        html.P("Most Affected State"),
                                        html.H4(id = 'top-state', style = {'fontWeight': 'bold'}),
                                    ], style={'width':'33%'}),
                                ], style = {
                                    'display': 'flex',
                                    'justifyContent': 'space-between',
                                    'textAlign': 'center',
                                    'padding': '20px',
                                    'alignItems': 'baseline'
                                }),
                                html.H3(["Most Affected Jobs"], style = { 'padding': '20px', 'margin': '0', 'backgroundColor': '#0645aa', 'color': '#f5f5f5'}),
                                # Stats Inner Flexbox 2
                                html.Div([
                                    # Stat Item 4
                                    html.Div([
                                        html.H4(id = 'common-count-1', style = {'fontWeight': 'bold'}),
                                        html.H5(id = 'common-title-1'),
                                        html.P(id = 'common-prob-1')
                                    ], style={'width':'33%'}),
                                    # Stat Item 5
                                    html.Div([
                                        html.H4(id = 'common-count-2', style = {'fontWeight': 'bold'}),
                                        html.H5(id = 'common-title-2'),
                                        html.P(id = 'common-prob-2')
                                    ], style={'width':'33%'}),
                                    # Stat Item 6
                                    html.Div([
                                        html.H4(id = 'common-count-3', style = {'fontWeight': 'bold'}),
                                        html.H5(id = 'common-title-3'),
                                        html.P(id = 'common-prob-3')
                                    ], style={'width':'33%'}),
                                ], style = {
                                    'display': 'flex',
                                    'justifyContent': 'space-between',
                                    'textAlign': 'center',
                                    'padding': '20px'
                                })
                            ])
                        ]
                    )
                ], style = {
                    'display': 'flex',
                    'flexDirection': 'column',
                    'alignItems': 'flex-start',
                    'width': '90%',
                    'margin': 'auto',
                })
            ]
        )
    ]
)

@app.callback(
    Output(component_id='state-choropleth', component_property='figure'),
    [Input(component_id='range-slider', component_property='value')])
def display_map(value):
    state_names = list(lat_long['State'])
    # Calculating automation percentages
    new_jobs_criteria = df[state_names][(df.Probability >= value[0]) & (df.Probability <=value[1])].sum()
    new_total = df[state_names].sum()
    new_percentage = ((new_jobs_criteria/new_total)*100).round(2)
    new_percentage = new_percentage.values.astype(str)
    lat_long['percentage'] = new_percentage

    # Finding the highest likely job
    in_range = df[(df['Probability'] >= value[0]) & (df['Probability'] <= value[1] )]
    lat_long['max_count'] = in_range[state_names].max().values.astype(str)
    lat_long['max_job'] = in_range.set_index('Occupation').drop(['SOC','Probability'],1).idxmax().values

    # Assigning a color

    data = [
        dict(
            lat=lat_long['Latitude'],
            lon=lat_long['Longitude'],
            mode='text',
            type='scattermapbox',
            text=lat_long['Abbr'],
            hoverinfo='text',
            hoverlabel= dict(
                bgcolor= '#303030',
                bordercolor='white',
                font=dict(
                    size=16
                ),
            ),
            hovertext= '  <b>' + lat_long['State'] + '</b><br>  <b>' + lat_long['percentage'] + '%</b> of jobs fall within the selected range.<br>  The most common job in this range includes <b>' + lat_long['max_count'] + ' ' + lat_long['max_job'] + '</b>  '
        )
    ]

    annotations = [dict(
        showarrow = False,
        text="<b>Percentage of Jobs in automation range</b>",
        x = 0.95,
		y = 0.95
    )]

    for i in enumerate(reversed(legend_range)):
        color = str(colors[(i[0]*5)])
        annotations.append(
			dict(
				arrowcolor = color,
				text = legend_range[i[0]],
				x = 0.95,
				y = 0.88-(i[0]/20),
				ax = -60,
				ay = 0,
				arrowwidth = 5,
				arrowhead = 0
			)
		)


    layout = dict(
        autosize = True,
        annotations = annotations,
        height = 500,
        hovermode = 'closest',
        margin=dict(
            l=0, r=0, b=0, t=0
        ),
        mapbox = dict(
            layers = [],
            accesstoken = mapbox_access_token,
            style = 'mapbox://styles/adi00014/cjv34p78t4mx91fnrtje22j91',
            center=dict(lat=38.5008195, lon=-95.680902),
            zoom=3.2
        )
    )

    my_color = str(colors[11])

    for i in state_names:
        mval = lat_long.loc[lat_long['State'] == i, 'percentage'].astype(float)/2
        mval = mval.astype(int).values
        my_color = str(colors[mval[0]])
        geo_layer = dict(
            sourcetype='geojson',
            source = 'https://raw.githubusercontent.com/aditya-14/plotly-map/master/'+i+'.geojson',
            type = 'fill',
            color = my_color
        )
        layout['mapbox']['layers'].append(geo_layer)
    
    fig = dict(data = data, layout = layout)
    return fig

@app.callback(
    Output(component_id='slider-text', component_property='children'),
    [Input(component_id='range-slider', component_property='value')])
def update_output(value):
    return 'Showing jobs between {0:.3g}'.format(value[0]*100) + '% and {0:.3g}'.format(value[1]*100) + '% chance of automation.'

@app.callback(
    [Output(component_id='total-jobs', component_property='children'),
     Output(component_id='range-jobs', component_property='children'),
     Output(component_id='top-state', component_property='children'),
     Output(component_id='common-count-1', component_property='children'),
     Output(component_id='common-title-1', component_property='children'),
     Output(component_id='common-prob-1', component_property='children'),
     Output(component_id='common-count-2', component_property='children'),
     Output(component_id='common-title-2', component_property='children'),
     Output(component_id='common-prob-2', component_property='children'),
     Output(component_id='common-count-3', component_property='children'),
     Output(component_id='common-title-3', component_property='children'),
     Output(component_id='common-prob-3', component_property='children'),],
    [Input(component_id='range-slider', component_property='value')])
def update_stats(value):

    state_names = list(lat_long['State'])
    # Total absolute value
    total_jobs = df[lat_long['State']].sum(axis=1).sum()    
    jobs_in_criteria = df[lat_long['State']][(df.Probability >= value[0]) & (df.Probability <=value[1])].sum().sum()
    percent_in_criteria = (jobs_in_criteria/total_jobs)*100

    # Max state
    in_range = df[(df['Probability'] >= value[0]) & (df['Probability'] <= value[1] )]
    new_jobs_criteria = df[state_names][(df.Probability >= value[0]) & (df.Probability <=value[1])].sum()
    new_total = df[state_names].sum()
    percentage_criteria = ((new_jobs_criteria/new_total)*100).round(2)
    top_state = percentage_criteria.nlargest(1)

    # Max jobs
    total_by_job = in_range.set_index('Occupation').drop(['SOC','Probability'],1).sum(axis=1)
    top_3 = total_by_job.nlargest(3)

    p1 = float(df['Probability'][df['Occupation'] == top_3.index[0]])*100
    p2 = float(df['Probability'][df['Occupation'] == top_3.index[1]])*100
    p3 = float(df['Probability'][df['Occupation'] == top_3.index[2]])*100

    return '{:,}'.format(total_jobs), '{:,}'.format(jobs_in_criteria) + ' ({0:.3g}%'.format(percent_in_criteria) + ')', top_state.index[0] + ' ({0:.3g}%'.format(top_state[0]) + ')', '{:,}'.format(top_3[0]), top_3.index[0], '{0:.3g}%'.format(p1) + ' chance of automation', '{:,}'.format(top_3[1]), top_3.index[1], '{0:.3g}%'.format(p2) + ' chance of automation', '{:,}'.format(top_3[2]), top_3.index[2], '{0:.3g}%'.format(p3) + ' chance of automation',


if __name__ == '__main__':
    app.run_server(debug=True)