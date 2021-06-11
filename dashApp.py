import dash
from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.CardHeader import CardHeader
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_bootstrap_components as dbc
from numpy.lib.twodim_base import triu_indices_from
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from dataHandling import *
from dashPlots import *

external_stylesheets = [dbc.themes.SLATE]

print(dbc.themes.PULSE)

dFrames = load_data('.\data\\')
df = dFrames['deaths']
countries = df.index.unique(level=0).values
regions = df.loc[countries[0]].index.unique(level=0).values


def makeHeadTable():
    active_up_down = dFrames['active_diff'].loc[('World', 'Main')][-1] - dFrames['active_diff'].loc[('World', 'Main')][-2]
    confirmed_up_down = dFrames['confirmed_diff'].loc[('World', 'Main')][-1] - dFrames['confirmed_diff'].loc[('World', 'Main')][-2]
    recovered_up_down = dFrames['recovered_diff'].loc[('World', 'Main')][-1] - dFrames['recovered_diff'].loc[('World', 'Main')][-2]
    deaths_up_down = dFrames['deaths_diff'].loc[('World', 'Main')][-1] - dFrames['deaths_diff'].loc[('World', 'Main')][-2]

    clr_active = colorLookup['red'] if active_up_down > 0 else colorLookup['green']
    clr_confirmed = colorLookup['red'] if confirmed_up_down > 0 else colorLookup['green']
    clr_recovered = colorLookup['red'] if recovered_up_down > 0 else colorLookup['green']
    clr_deaths = colorLookup['red'] if deaths_up_down > 0 else colorLookup['green']

    str_active = "▲" if active_up_down > 0 else "▼"
    str_confirmed = "▲" if confirmed_up_down > 0 else "▼"
    str_recovered = "▲" if recovered_up_down > 0 else "▼"
    str_deaths = "▲" if deaths_up_down > 0 else "▼"

    return dbc.Row(
        dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th(),
                    html.Th('Active Cases', style={"text-align" : "center"}),
                    html.Th('Confirmed Cases', style={"text-align" : "center"}),
                    html.Th('Recovered', style={"text-align" : "center"}),
                    html.Th('Deceased', style={"text-align" : "center"})
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td('Total', style={"text-align" : "center", "font-weight" : "bold"}),
                    html.Td(f"{int(dFrames['active'].loc[('World', 'Main')]['Total', 'tot']):,}", style={"text-align" : "right"}),
                    html.Td(f"{int(dFrames['confirmed'].loc[('World', 'Main')]['Total', 'tot']):,}", style={"text-align" : "right"}),
                    html.Td(f"{int(dFrames['recovered'].loc[('World', 'Main')]['Total', 'tot']):,}", style={"text-align" : "right"}),
                    html.Td(f"{int(dFrames['deaths'].loc[('World', 'Main')]['Total', 'tot']):,}", style={"text-align" : "right"})
                ]),
                html.Tr([
                    html.Td('Yesterday', style={"text-align" : "center", "font-weight" : "bold"}),
                    html.Td(f"{int(dFrames['active_diff'].loc[('World', 'Main')][-1]):,}" + " " + str_active, style={"text-align" : "right", 'color' : clr_active}),
                    html.Td(f"{int(dFrames['confirmed_diff'].loc[('World', 'Main')][-1]):,}" + " " + str_confirmed, style={"text-align" : "right", 'color' : clr_confirmed}),
                    html.Td(f"{int(dFrames['recovered_diff'].loc[('World', 'Main')][-1]):,}" + " " + str_recovered, style={"text-align" : "right", 'color' : clr_recovered}),
                    html.Td(f"{int(dFrames['deaths_diff'].loc[('World', 'Main')][-1]):,}" + " " + str_deaths, style={"text-align" : "right", 'color' : clr_deaths})
                ])
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        ),
        id='top-head',
        #align='stretch',
    )

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets=external_stylesheets
)
server = app.server

app.layout = dbc.Container([

    dbc.Container([
        dbc.Row(
            dbc.Col(html.H1('COVID 19 Dashboard'))
        ),
        dbc.Row(
            dbc.Col(html.H5(children='Corona-Virus Worldwide'))
        ),
        dbc.Row(
            dbc.Col(
                makeHeadTable()
            )
        )
    ]),
    html.Br(),
    
    ### WORLDMAP ###
    dbc.Card([
            dbc.CardHeader('World Map'),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Tabs(id="tabs-world", active_tab='active', children=[
                            dbc.Tab(label='Active', tab_id='active'),
                            dbc.Tab(label='Confirmed', tab_id='confirmed'),
                            dbc.Tab(label='Recovered', tab_id='recovered'),
                            dbc.Tab(label='Dead', tab_id='deaths')
                        ])
                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Checklist(
                                options=[
                                    {"label": "Relative", "value": 0},
                                ],
                                value=[0],
                                id="sw-world-input",
                                switch=True,
                            ),
                        ]
                    )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader('Relative Values per Day or Absolute Values normalized to the highest recorded daily value'),
                            dbc.CardBody([
                                dcc.Graph(id='gr-world'),
                                html.Br(),
                                html.Br(),
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Slider(
                                            id = 'sl-date-world',
                                            min=0,
                                            max=len(dFrames['deaths']['Data'].columns.values)+1,
                                            step=5,
                                            value=len(dFrames['deaths']['Data'].columns.values)+1,
                                            marks=dict(zip(list(range(0, len(dFrames['deaths']['Data'].columns.values), 120))+[len(dFrames['deaths']['Data'].columns.values)+1], list(dFrames['deaths']['Data'].columns.values[::120])+['Total'])),
                                            included=False
                                        )
                                    ])
                                ]),
                            ])
                        ], color='primary', outline=False, inverse=True)
                    ])
                ], id='world-map'),
                html.Br(),
                dbc.Card([
                    dbc.CardBody(
                        dcc.Markdown(
'''#### Interactive World Map
Use the Slider to choose a date. Slide all the way to the right for Total numbers.
Hit the Toggle to switch between relative view where values are renormalized to the biggest daily value and absolute view where the data is normalized to the biggest value ever recorded.
Use relative mode to understand where the pandemic was strongest at any point in time. Use absolute mode to see developments over time in particular regions and countries.
Left click on a country to load the corresponding data in the plots below.'''
                        )
                    )
                ], outline=False, color='primary', inverse=True)

            ], id='world-map-wrapper'),
        ],
        color='primary', outline=True
        ),
    html.Br(),
    ### STATS PER COUNTRY ###
    dbc.Card([
        dbc.CardHeader('Time Series'),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4('Country'),
                        dcc.Dropdown(
                            id = 'dd-country',
                            options=[{'label':country,'value':country} for country in countries],
                            value=countries[0]
                        )
                    ])
                    
                ], width=3
                ),
                dbc.Col([
                    html.Div([
                        html.H4('Region'),
                        dcc.Dropdown(
                            id = 'dd-region',
                            options=[{'label':region,'value':region} for region in regions],
                            value='Main'
                        )
                    ])
                ], width=3
                ),
                dbc.Col([
                    html.Div([
                        html.H4('Average over # days'),
                        dcc.Slider(
                            id = 'sl-rate-average',
                            min=1,
                            max=14,
                            step=1,
                            value=1,
                            marks=dict(zip(range(1,14,2), range(1,14,2))),
                            included=False
                        )
                    ])
                ], style={'width': '30%', 'display': 'inline-block'}
                ),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Tabs(id="tabs", active_tab='active', children=[
                        dbc.Tab(label='Active', tab_id='active'),
                        dbc.Tab(label='Confirmed', tab_id='confirmed'),
                        dbc.Tab(label='Recovered', tab_id='recovered'),
                        dbc.Tab(label='Dead', tab_id='deaths'),
                    ]),
                ])
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Development over Time'),
                        dbc.CardBody([
                            dcc.Graph(id='gr-cum')
                        ])
                    ], color='primary', outline=False, inverse=True)
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Rate of Change Averaged over # days'),
                        dbc.CardBody([
                            dcc.Graph(id='gr-daily')
                        ])
                    ], color='primary', outline=False, inverse=True),
                ])
            ], id='graphs'),
        ]),
    ], color='primary', outline=True),


    ### LOGLOG - Deaths vs Confirmed CASES ###
    html.Br(),
    dbc.Card([
        dbc.CardHeader('# Deaths vs. # Confirmed Cases'),
        dbc.CardBody([
            dbc.Row(
                dbc.Col([
                    dcc.Graph(id='gr-death-confirmed',
                        figure=death_confirmed_plot(dFrames['deaths'][('Total', 'tot')].drop(['Canada', 'China', 'Australia']).drop('World'),
                        dFrames['confirmed'][('Total', 'tot')].drop(['Canada', 'China', 'Australia']).drop('World'))
                    ),
                ], width=11)
                
            ),
        ]
        )
    ], outline=True, color='primary')
], id='main-div')


app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)

# update Region List
@app.callback(Output('dd-region','options'),
              [Input('dd-country','value'), Input('tabs', 'active_tab')])
def update_regions(country, tabs):
    rgns = dFrames[tabs].loc[country].index.unique(level=0).values
    return [{'label':region,'value':region} for region in rgns]

# update cumulative graph
@app.callback(Output('gr-cum','figure'),
              [Input('dd-country','value'),
              Input('dd-region', 'value'),
              Input('tabs','active_tab')])
def update_cum_graph(country, region, tabs):

    data_color_dict = {
        'active' : '#0377fc',
        'confirmed': '#329da8',
        'recovered': '#32a86d',
        'deaths': '#a8326d'
    }

    layout_dict = {
        'confirmed': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#ebfffa'
        },
        'recovered': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#efffeb'
        },
        'deaths': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#fff2f2'
        },
        'active': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#ebf7ff'
        }
    }
    
    df = dFrames[tabs]
    df = df.loc[(country, region)]

    data = [go.Scatter(x=df['Data'].index.values, y=df['Data'],
            mode='lines',
            marker_color=data_color_dict.get(tabs,None),
            line_width=4)]

    layout_kwargs = layout_dict.get(tabs,None)
    layout = go.Layout(template = 'plotly_dark',
                       #title = 'Cumulative',
                       title_font_color = data_color_dict.get(tabs,None),
                       title_font_size = 20,
                       hovermode='x',
                       xaxis_title="Date",
                       yaxis_title="# Population",
                       xaxis = dict(
                        #tickfont_color = '#FFFFFF',
                        #linecolor = '#AAAAAA',
                        showgrid = False,
                        zeroline = False,
                        automargin=True,
                        showline=True,
                        mirror=True,
                        ticks='outside'),
                       yaxis = dict(
                        nticks = 10,
                        zeroline = False,
                        #linecolor = '#AAAAAA',
                        #tickfont_color = '#FFFFFF',
                        #gridcolor = '#AAAAAA',
                        automargin=True,
                        showline=True,
                        mirror=True,
                        ticks='outside'),
                        margin={"r":0,"t":0,"l":0,"b":0},
                        **layout_kwargs)

    return {
        'data': data,
        'layout': layout
    }


# update graphs from world map
@app.callback([Output('dd-country','value'), Output('dd-region', 'value'),  Output('tabs', 'active_tab')],
              [Input('gr-world', 'clickData')],
              [State('tabs-world', 'active_tab')])
def update_graphs_from_world(clickData, tabs):
    if clickData is not None:
        country, region = clickData['points'][0]['text'].split('\n')[0].split(',')
        country = country[2:-1].strip()
        region = region[2:-2]
        return country, region, tabs
    else:
        return countries[0], 'Main', 'active'

# update daily graph
@app.callback(Output('gr-daily','figure'),
              [Input('dd-country','value'),
              Input('dd-region', 'value'),
              Input('tabs','active_tab'),
              Input('sl-rate-average', 'value'),])
def update_daily_graph(country, region, tabs, slider):

    data_color_dict = {
        'active' : '#0377fc',
        'confirmed': '#329da8',
        'recovered': '#32a86d',
        'deaths': '#a8326d'
    }

    layout_dict = {
        'confirmed': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#ebfffa'
        },
        'recovered': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#efffeb'
        },
        'deaths': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#fff2f2'
        },
        'active': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#ebf7ff'
        }
    }
    
    df = dFrames[tabs+'_diff']
    df = df.loc[(country, region)]

    data = [go.Bar(x=df.index.values, y=df.rolling(slider, center=True, win_type='triang').sum()/slider,
            width=1, marker_color=data_color_dict.get(tabs,None),marker = dict(line=dict(width=0)))]

    layout_kwargs = layout_dict.get(tabs,None)
    layout = go.Layout(template = 'plotly_dark',
                       #title = 'Average Daily Rates',
                       title_font_color = data_color_dict.get(tabs,None),
                       title_font_size = 20,
                       hovermode='x',
                       xaxis_title="Date",
                       yaxis_title="# Population",
                       xaxis = dict(
                        #tickfont_color = '#000000',
                        #linecolor = 'black',
                        showgrid = False,
                        zeroline = False,
                        automargin=True,
                        showline=True,
                        mirror=True,
                        ticks='outside'
                        ),
                       yaxis = dict(
                        nticks = 10,
                        zeroline = False,
                        #tickfont_color = '#000000',
                        #gridcolor = '#555555',
                        #linecolor = 'black',
                        automargin=True,
                        showline=True,
                        mirror=True, 
                        ticks='outside'
                        ),
                        margin={"r":0,"t":0,"l":0,"b":0},
                        bargap=1,
                        **layout_kwargs)

    return {
        'data': data,
        'layout': layout
    }


# update World
@app.callback(Output('gr-world', 'figure'),
              [Input('tabs-world', 'active_tab'),
              Input('sl-date-world', 'drag_value'),
              Input('sw-world-input', 'value')])
def update_world(tabs, date, switch):
    
    data_color_dict = {
        'confirmed': '#329da8',
        'recovered': '#32a86d',
        'deaths': '#a8326d',
        'active' : '#0377fc'
    }


    df = dFrames[tabs]
    if date is None:
        date = len(df['Data'].columns.values) + 5

    if date >= len(df['Data'].columns.values):
        datsize = df['Total', 'tot'].drop('World')
        dateDisplay = 'Total'
        datnormal = np.max(datsize)
    else:
        datsize = df['Data'][df['Data'].columns.values[date]].drop('World')
        dateDisplay = str(df['Data'].columns.values[date])
        datnormal = np.max(datsize)

    datsize = datsize.fillna(0)
    datsize[datsize < 0] = 0

    if 0 not in switch:
        datnormal = np.amax(df['Data'].fillna(0).drop('World').to_numpy())
        print("Normalize World with: ", datnormal)


    data = [
        go.Scattergeo(
            lat=df[('Coords', 'Lat')].drop('World'),
            lon=df[('Coords', 'Lon')].drop('World'),
            marker = dict(
                color = data_color_dict.get(tabs,None),
                size = (datsize.fillna(0)/datnormal)*1e3,
                sizemode = 'area',
                sizemin = 3
            ),
            text= [str(datsize.index.values[i]) + "\n" + "#{:,}".format(int(datsize[i])) for i in range(len(datsize))]
        )
    ]
    #layout_kwargs = layout_dict.get(tabs,None)
    layout = go.Layout(
                    template = 'plotly_dark',
                    geo = dict(showocean=True, oceancolor='LightBlue', showland=True, landcolor="LightGreen", projection_type='natural earth'),
                    height=400, margin={"r":0,"t":0,"l":0,"b":0},
                    title={'text' :dateDisplay, 'xref' : 'paper', 'yref' : 'paper', 'x' : 0.05, 'y' : 0.95},
                    title_font_size = 25,
                    paper_bgcolor = 'rgba(0,0,0,0)'
                )

    return {
        'data': data,
        'layout': layout
    }




if __name__ == '__main__':
    #app.css.config.serve_locally = True
    app.run_server(host='0.0.0.0')