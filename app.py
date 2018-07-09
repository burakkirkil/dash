import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.graph_objs import *
import pandas as pd
import os

# ####################################################
# APP & SERVER
# ####################################################

app = dash.Dash('streaming-wind-app')
server = app.server

# ####################################################
# MAIN
# ####################################################

quantity = 10

CSV_FILE_PATH = 'Data'
dataFiles = [f for f in os.listdir(CSV_FILE_PATH) if os.path.isfile(
    os.path.join(CSV_FILE_PATH, f)) and f.endswith(".csv")]

defaultDataFile = list(dataFiles)[0]

raw_data = pd.read_csv("./Data/{}".format(defaultDataFile), parse_dates=['ds'])


# ####################################################
# VIEW
# ####################################################

app.layout = html.Div([
    html.Div([
        html.H2("Demand Forecast"),
        html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/" +
                 "dash-logo-by-plotly-stripe-inverted.png"),
    ], className='banner'),
    html.Div([
        dcc.Dropdown(
            id='quantity-dropdown',
            options=[
                {'label': '10', 'value': '10'},
                {'label': '20', 'value': '20'},
                {'label': '50', 'value': '50'},
                {'label': '100', 'value': '100'}
            ],
            value='10'
        ),
        dcc.Dropdown(
            id='csv-dropdown',
            options=[{'label': name, 'value': name} for name in dataFiles],
            value=defaultDataFile
        ),
    ]),
    html.Div([
        'Data:',
        html.Span(id='csv-output-container'),
        'Quantity:',
        html.Span(id='quantity-output-container'),
    ]),
    html.Div([
        html.Div([
            html.H3("Demand Forecast Graph")
        ], className='Title'),
        html.Div([
            dcc.Graph(id='demand-forecast'),
        ], className='twelve columns wind-speed'),
        dcc.Interval(id='demand-forecast-update',
                     interval=1000, n_intervals=0),
    ], className='row wind-speed-row'),
], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "900px",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})


# ####################################################
# METHODS
# ####################################################

@app.callback(
    Output('quantity-output-container', 'children'),
    [Input('quantity-dropdown', 'value')])
def qunantity_update_output(value):
    global quantity
    quantity = value
    return value


@app.callback(
    Output('csv-output-container', 'children'),
    [Input('csv-dropdown', 'value')])
def csv_update_output(value):
    global raw_data
    raw_data = pd.read_csv("./Data/{}".format(value), parse_dates=['ds'])
    print(value)
    return value


@app.callback(Output('demand-forecast', 'figure'),
              [Input('demand-forecast-update', 'n_intervals')])
def gen_demand_forecast(interval):

    df = raw_data[interval:interval + int(float(quantity))]

    trace_upper = Scatter(
        x=df.ds,
        y=df['yhat_upper'],
        fill='none',
        fillcolor='rgba(0,176,246,0.2)',
        line=dict(color='rgba(0,176,246,0)'),
        showlegend=False,
        name='Upper',
    )

    trace_lower = Scatter(
        x=df.ds,
        y=df['yhat_lower'],
        fill='tonexty',
        fillcolor='rgba(0,176,246,0.2)',
        line=dict(color='rgba(0,176,246,0)'),
        showlegend=False,
        name='Lower',
    )

    trace = Scatter(
        x=df.ds,
        y=df['y'],
        name="y",
        mode='markers',
        marker=dict(size=6, color='rgb(231,107,243)'),
        opacity=0.8)

    estimated = Scatter(
        x=df.ds,
        y=df['yhat'],
        name="Estimated",
        line=dict(color='rgb(0,176,246)'),
        opacity=0.8)

    layout = Layout(
        yaxis=dict(
            range=[0, 600]
        ),
    )

    return Figure(data=[trace_upper, trace_lower, trace, estimated], layout=layout)


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/" +
                "737dc4ab11f7a1a8d6b5645d26f69133d97062ae/dash-wind-streaming.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


for css in external_css:
    app.css.append_css({"external_url": css})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/' +
        'e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

if __name__ == '__main__':
    app.run_server()
