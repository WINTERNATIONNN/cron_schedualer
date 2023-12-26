import calendar
from io import StringIO
import json
import os
import cpi_scheduler_dump
from dash import Dash, html, dcc, Input, Output, ctx,callback, no_update, dash_table  # type: ignore
from datetime import time, datetime, date  # type: ignore
import datetime # type: ignore
from matplotlib import colors
from cron_descriptor import ExpressionSchedular
import json
import calendar
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore
from colormap import rgb2hex  # type: ignore



TOTAL_HOURS_PER_DAY = 24
TOTAL_MINUTES_PER_HOUR = 60
FILE_PATH = ''
OUTPUT_PATH = ''
idlist = [None]*TOTAL_MINUTES_PER_HOUR
date_object = date.today()
hour_df = []
cur_hour = 0

def visualize_by_month(TOTAL_DAYS_PER_MONTH, iflow_daily_frequency, qt):
    """Returns the fig of iflow counts distribution throughout the month

    Args:
        TOTAL_DAYS_PER_MONTH: The number of days of given month
        iflow_daily_frequency:: The frequency of day timestamp with given iflow list
        qt: User input datetime

    """
    xticks = np.arange(1, TOTAL_DAYS_PER_MONTH+1)
    xlabels = [date(qt.year, qt.month, i).strftime("%m/%d")
               for i in range(1, TOTAL_DAYS_PER_MONTH+1)]

    fig = go.Figure(data=[go.Histogram(x=iflow_daily_frequency,
                                       xbins=dict(
                                           start=1, end=TOTAL_DAYS_PER_MONTH+1),
                                       histfunc="count",
                                       marker={'color': get_color_map(iflow_daily_frequency, 1, TOTAL_DAYS_PER_MONTH+1, 1)})])

    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,
                          title=dict(text='Date')
                      ),
                      yaxis=dict(
                          title=dict(text='Number of iFlows'),
                          tickformat="d"
                      ),
                      hoverlabel_align='right'
                      )
    return fig


def visualize_by_day(iflow_hourly_fequency):
    """Returns the fig of iflow counts distribution throughout the day

    Args:
        iflow_hourly_fequency: The list of he frequency of hour timestamp with given iflow list

    """
    xticks = np.arange(0, TOTAL_HOURS_PER_DAY)
    xlabels = [time(i, 0).strftime("%H:%M")
               for i in range(0, TOTAL_HOURS_PER_DAY)]

    fig = go.Figure(data=[go.Histogram(x=iflow_hourly_fequency,
                                       xbins=dict(start=0, end=24, size=1),
                                       histfunc="count",
                                       marker={'color': get_color_map(iflow_hourly_fequency, 1, TOTAL_HOURS_PER_DAY, 0)})])

    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,
                          title=dict(text='Hours')
                      ),
                      yaxis=dict(
                          title=dict(text='Number of iFlows'),
                          tickformat="d"
                      ),
                      hoverlabel_align='right'
                      )
    return fig


def visualize_by_hour(iflow_min_freq, iflow_ids, cur_hour):
    """Returns the fig of iflow counts distribution throughout the hour

    Args:
        iflow_min_freq: The list of frequency of minute timestamp with given iflow list
        iflow_ids: The list of iflow ids that run within the hour
        cur_hour: The number of current hour

    """
    global hour_df
    TIME_GAP = 1

    xticks = np.arange(0, TOTAL_MINUTES_PER_HOUR, TIME_GAP)
    xlabels = [time(cur_hour, i, 0).strftime("%M:%S")
               for i in range(0, TOTAL_MINUTES_PER_HOUR, TIME_GAP)]

    #hour_df stores the iflow ids and counts within each time gap  (aka.bins)
    #print(get_stamplist(iflow_ids,cur_hour))
    hour_df = [get_idlist(i, i + TIME_GAP, iflow_ids)
               for i in range(0, TOTAL_MINUTES_PER_HOUR, TIME_GAP)]

    counts, bins = np.histogram(iflow_min_freq, bins=range(0, 60+1, TIME_GAP))

    fig = px.histogram(x=iflow_min_freq, nbins=60, range_y=[
                       0, (1+counts.max()/5)*5], marginal='rug', color_discrete_sequence=px.colors.qualitative.Prism)

    fig.update_traces(xbins=dict(
        start=0, end=TOTAL_MINUTES_PER_HOUR), selector=dict(type='histogram'))
    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,
                          title=dict(text='Minutes')
                      ),
                      yaxis=dict(
                          title=dict(text='Number of iFlows'),
                          tickformat="d"
                      ),
                      hoverlabel_align='right',
                      )
    return fig


def get_color_map(freq, xbin_size, xbin_end, xbin_start):
    """Return the color map for a given histogram distribution

    Args: 
        freq: The frequency map for histogram
        xbin_size: The bin size of histogram
        xbin_start: The start of xbin
        xbin_end: The end of xbin
        

    """
    fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)

    N, bins, patches = ax.hist(freq, bins=np.arange(
        xbin_start, xbin_end + xbin_size, xbin_size), edgecolor="white")
    fracs = N / N.max()
    norm = colors.Normalize(fracs.min(), fracs.max())

    colormap = []
    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        colormap.append(rgb2hex(color[0], color[1], color[2], color[3]))

    return colormap

def get_idlist(left, right, cur_hour_list):
    idlist = []
    df = pd.DataFrame({"id": [], "count": []})
    for i in range(left, right):
        if cur_hour_list[i] is not None:
            idlist = list(set(cur_hour_list[i]))
            for id in idlist:
                if id in df["id"].values:
                    df.loc[df["id"] == id,
                           "count"] += cur_hour_list[i].count(id)
                else:
                    df.loc[len(df.index)] = [id, cur_hour_list[i].count(id)]
                
    return df


def get_iflow_by_hour(iflow_list, qt, query_range):
    iflow_by_hour = dict.fromkeys(list(range(TOTAL_MINUTES_PER_HOUR)))
    for iflow_id in iflow_list:
        expre = iflow_list[iflow_id][0]["value"]
        if expre != "fireNow=true":
            sched = ExpressionSchedular(expre, qt)
            iflow_list[iflow_id][0]["timestamps"] = sched.get_schedule_timetable()
            for stamp in iflow_list[iflow_id][0]["timestamps"]:
                if stamp.hour == query_range:
                    if iflow_by_hour[stamp.minute] is None:
                        iflow_by_hour[stamp.minute] = []

                    iflow_by_hour[stamp.minute].append(iflow_id)

    return iflow_by_hour


def get_iflow_freq(iflow_list, qt, TYPE, query_range):
    cur_list = []
    for iflow_id in iflow_list:
        expre = iflow_list[iflow_id][0]["value"]
        if expre != "fireNow=true":
            if TYPE == 'MONTH':
                # get the iflow frequency list bin by day
                for i in range(1, query_range+1):
                    sched = ExpressionSchedular(
                        expre, qt=datetime.date(qt.year, qt.month, i))
                    st = sched.get_schedule_timetable()
                    for j in range(0, len(st)):
                        cur_list.append(i)
            elif TYPE == 'DAY':
                # get the iflow frequency list bin by hour
                sched = ExpressionSchedular(expre, qt)
                iflow_list[iflow_id][0]["timestamps"] = sched.get_schedule_timetable()
                for stamp in iflow_list[iflow_id][0]["timestamps"]:
                    cur_list.append(stamp.hour)
            elif TYPE == 'HOUR':
                # get the iflow frequency list bin by minutes
                sched = ExpressionSchedular(expre, qt)
                iflow_list[iflow_id][0]["timestamps"] = sched.get_schedule_timetable()
                for stamp in iflow_list[iflow_id][0]["timestamps"]:
                    if stamp.hour == query_range:
                        cur_list.append(
                            float(stamp.minute+float(stamp.second/60)))

    return cur_list

def get_stamplist(iflow_ids, query_range, query_date):
    #stamplist = dict()
    cur_df = pd.DataFrame({"id": [], "count": [], "description":[], "timestamp": []})
    temp_df = get_idlist(0,60,iflow_ids)
    for iflow_id in temp_df["id"].values:
        cur_list = []
        for stamp in iflow_list[iflow_id][0]["timestamps"]:
            if stamp.hour == query_range:
                cur_list.append(stamp.strftime("%H:%M:%S"))
        cur_df.loc[len(cur_df.index)] =[iflow_id, len(cur_list),iflow_list[iflow_id][0]["description"], ','.join(cur_list)]
        #cur_df.loc[len(cur_df.index)] =[iflow_id, len(cur_list),"tt", ','.join(cur_list)]
    #print(cur_df)
    FILE_NAME = query_date.strftime("%Y-%m-%d")+'_' + str(query_range) + '.csv'
    cur_df.to_csv(OUTPUT_PATH+ FILE_NAME, index = False)
    


@callback(
    Output('iflow_by_month', 'figure'),
    Input('my-date-picker-single', 'date'))
def update_month_figure(date_value):
    if date_value is None:
        return no_update

    if date_value is not None:
        global date_object
        date_object = date.fromisoformat(date_value)

        _, LAST_DAY_OF_MONTH = calendar.monthrange(
            date_object.year, date_object.month)
        return visualize_by_month(LAST_DAY_OF_MONTH, get_iflow_freq(iflow_list, date_object, "MONTH", LAST_DAY_OF_MONTH), date_object)


@callback(
    Output('iflow_by_day', 'figure'),
    Input('iflow_by_month', 'clickData'))
def display_day(clickData):
    global date_object

    if clickData is None:
        return no_update
    if clickData is not None:
        date_object = date(date_object.year, date_object.month,
                           clickData['points'][0]['binNumber']+1)

    return visualize_by_day(get_iflow_freq(iflow_list, date_object, "DAY", 31))


@callback(
    Output('iflow_by_hour', 'figure'),
    Input('iflow_by_day', 'clickData'))
def display_hour(clickData):
    global date_object
    global cur_hour
    if clickData is None:
        return no_update
    cur_hour = 0
    if clickData is not None:
        cur_hour = clickData['points'][0]['binNumber']

    return visualize_by_hour(get_iflow_freq(iflow_list, date_object, "HOUR", cur_hour), get_iflow_by_hour(iflow_list, date_object, cur_hour), cur_hour)


@callback(
    Output('dtable', "data"),
    Input('iflow_by_hour', 'clickData'),
)
def update_table(clickData):
    if clickData is None:
        return no_update
    bin = clickData['points'][0]['binNumber']
    return hour_df[bin].to_dict('records')

@callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-nclicks-1', 'n_clicks')
)
def byclicks(btn1):
    global cur_hour
    global date_object
    msg = ''
    if "btn-nclicks-1" == ctx.triggered_id:
        get_stamplist(get_iflow_by_hour(iflow_list, date_object, cur_hour),cur_hour, date_object)
        msg = "Successfully Export"
    return html.Div(msg)

if __name__ == '__main__':
    cpi_scheduler_dump.main()
    FILE_PATH = 'scheluer_dumps.json'
    iflow_list = []
    if not os.path.exists(FILE_PATH):
        print("File does not exist.")
        exit(1)
        
    with open(FILE_PATH, "r") as file:
        iflow_list = json.load(file)

    app = Dash(__name__)
    dtable = dash_table.DataTable(data=[], page_size=10)
    app.layout = html.Div([
        html.Div([
            html.A(id='output-container-date-picker-single',
                   children="Select a date: "),
            dcc.DatePickerSingle(
                id='my-date-picker-single',
                initial_visible_month=date.today(),
                date=date.today()
            ),], style={'display': 'inline-block', 'width': '100%', 'text-align': 'center'}),

        html.Div([
            dcc.Graph(id='iflow_by_month'),


        ], style={'display': 'inline-block', 'width': '100%'}),
        html.Div([
            dcc.Graph(id='iflow_by_day'),


        ], style={'display': 'inline-block', 'width': '100%'}),
        html.Div([
            dcc.Graph(id='iflow_by_hour'),


        ], style={'display': 'inline-block', 'width': '100%'}),
        html.Div([

            dash_table.DataTable(data=[], page_size=10, id='dtable'),
            html.Button('Export to file', id='btn-nclicks-1', n_clicks=0),
            html.Div(id='container-button-timestamp')

        ], style={'display': 'inline-block'}),
       


    ], style={'text-align': 'center'})
    app.run_server(debug=True)
