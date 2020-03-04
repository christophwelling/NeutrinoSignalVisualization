from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash
import plotly.subplots
import plotly.graph_objs as go
import numpy as np
import json
from NuRadioReco.utilities import units, fft
import NuRadioReco.detector.antennapattern
from app import app

antennapattern_provider = NuRadioReco.detector.antennapattern.AntennaPatternProvider()

layout = html.Div([
    html.Div([
        html.Div([
            html.Div('Detector Settings', className='panel-heading'),
            html.Div([
                html.Div([
                    html.Div('Antenna Type'),
                    dcc.RadioItems(
                        id='antenna-type-radio-items',
                        options=[
                            {'label': 'Bicone', 'value': 'bicone_v8_InfFirn'},
                            {'label': 'LPDA', 'value': 'createLPDA_100MHz_InfFirn'},
                            {'label': 'RNO V-pol', 'value': 'greenland_vpol_InfFirn'},
                            {'label': 'RNO H-pol', 'value': 'fourslot_InfFirn'}
                        ],
                        value='bicone_v8_InfFirn',
                        labelStyle={'padding': '0 5px'}
                    )
                ], className='input-group')
            ], className='panel-body')
        ], className='panel panel-default')
    ], style={'flex': '1'}),
    html.Div([
        html.Div([
            html.Div('Voltage', className='panel-heading'),
            html.Div([
                dcc.Graph(id='voltage-plots')
            ], className='panel-body')
        ], className='panel panel-default')
    ],style={'flex': '4'})
], style={'display': 'flex'})

@app.callback(
    Output('voltage-plots', 'figure'),
    [Input('efield-trace-storage', 'children'),
    Input('antenna-type-radio-items', 'value')]
)
def update_voltage_plot(electric_field, antenna_type):
    samples = 512
    sampling_rate = 1.*units.GHz
    electric_field = json.loads(electric_field)
    if electric_field is None:
        return {}
    antenna_pattern = antennapattern_provider.load_antenna_pattern(antenna_type)
    freqs = np.fft.rfftfreq(samples, 1./sampling_rate)
    times = np.arange(samples) / sampling_rate
    zenith = 0.*units.deg
    azimuth = 90.

    antenna_response =antenna_pattern.get_antenna_response_vectorized(freqs, zenith, azimuth, 90.*units.deg, 0., 0., 0.)
    channel_spectrum = antenna_response['theta'] * fft.time2freq(electric_field['theta'], sampling_rate) + antenna_response['phi'] * fft.time2freq(electric_field['phi'], sampling_rate)
    channel_trace = fft.freq2time(channel_spectrum, sampling_rate)
    fig = plotly.subplots.make_subplots(rows=1, cols=2,
        shared_xaxes=False, shared_yaxes=False,
        vertical_spacing=0.01, subplot_titles=['Time Trace', 'Spectrum'])
    fig.append_trace(go.Scatter(
        x=times/units.ns,
        y=channel_trace/units.mV,
        name='U (t)'
    ),1,1)
    fig.append_trace(go.Scatter(
        x=freqs/units.MHz,
        y=np.abs(channel_spectrum)/(units.mV/units.GHz),
        name='U (f)'
    ), 1, 2)
    return fig
