from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash
import plotly.subplots
import plotly.graph_objs as go
import numpy as np
from NuRadioReco.utilities import units, fft
import NuRadioMC.SignalGen.askaryan
from app import app

app.title = 'Radio Signal Simulator'

app.layout = html.Div([
    html.Div([
        html.Div('Neutrino Settings', className='panel-heading'),
        html.Div([
            html.Div([
                html.Div('Energy'),
                dcc.Slider(
                    id='energy-slider',
                    min=16,
                    max=20,
                    step=.25,
                    value=18,
                    marks={
                        16: '10PeV',
                        17: '100PeV',
                        18: '1EeV',
                        19: '10EeV',
                        20: '100EeV'
                    }
                )
            ], className='input-group'),
            html.Div([
                html.Div('Viewing angle'),
                dcc.Slider(
                    id='viewing-angle-slider',
                    min=-10,
                    max=10,
                    step=1,
                    value=2,
                    marks={
                        -10: '-10°',
                        -5: '-5°',
                        -2: '-2°',
                        0: '0°',
                        2: '2°',
                        5: '5°',
                        10: '10°'
                    }
                )
            ], className='input-group'),
            html.Div([
                html.Div('Shower Type'),
                dcc.RadioItems(
                    id='shower-type-radio-items',
                    options=[
                        {'label': 'Hadronic', 'value': 'HAD'},
                        {'label': 'Electro-Magnetic', 'value': 'EM'}
                    ],
                    value='HAD',
                    labelStyle={'padding':'5px'}
                )
            ], className='input-group'),
            html.Div([
                html.Div('Shower Model'),
                dcc.Dropdown(
                    id='shower-model-dropdown',
                    options=[
                        {'label': 'ARZ2020', 'value': 'ARZ2020'},
                        {'label': 'ARZ2019', 'value': 'ARZ2019'},
                        {'label': 'Alvarez2012', 'value': 'Alvarez2012'},
                        {'label': 'Alvarez2009', 'value': 'Alvarez2009'},
                        {'label': 'Alvarez2000', 'value': 'Alvarez2000'},
                        {'label': 'ZHS1992', 'value': 'ZHS1991'}
                    ],
                    multi=False,
                    value='ARZ2020'
                )
            ], className='input-group')
        ], className='panel-body')
    ], className='panel panel-default', style={'flex':'1'}),
    html.Div([
        html.Div('Electric Field', className='panel-heading'),
        html.Div([
            dcc.Graph(id='electric-field-plot')
        ], className='panel-body')
    ], className='panel panel-default', style={'flex':'4'})
], style={'display': 'flex'})


@app.callback(
    Output('electric-field-plot', 'figure'),
    [Input('energy-slider', 'value'),
    Input('viewing-angle-slider', 'value'),
    Input('shower-type-radio-items', 'value'),
    Input('shower-model-dropdown', 'value')]
)
def update_electric_field_plot(log_energy, viewing_angle, shower_type, model):

    viewing_angle = viewing_angle * units.deg
    energy = np.power(10., log_energy)
    samples = 512
    sampling_rate = 1.*units.GHz
    ior = 1.78
    cherenkov_angle = np.arccos(1./ior)
    distance = 1.*units.km
    model = 'ARZ2019'
    efield_trace = NuRadioMC.SignalGen.askaryan.get_time_trace(
        energy,
        cherenkov_angle + viewing_angle,
        samples,
        1./sampling_rate,
        shower_type,
        ior,
        distance,
        model
    )
    times = np.arange(samples) / sampling_rate
    freqs = np.fft.rfftfreq(samples, 1./sampling_rate)

    fig = plotly.subplots.make_subplots(rows=1, cols=2,
        shared_xaxes=False, shared_yaxes=False,
        vertical_spacing=0.01, subplot_titles=['Time Trace', 'Spectrum'])
    fig.append_trace(go.Scatter(
        x=times/units.ns,
        y=efield_trace/(units.mV/units.m)
    ),1,1)
    fig.append_trace(go.Scatter(
        x=freqs/units.MHz,
        y=np.abs(fft.time2freq(efield_trace, sampling_rate))/(units.mV/units.m/units.GHz)
    ),1,2)

    return fig

app.run_server(debug=False, port=8080)
