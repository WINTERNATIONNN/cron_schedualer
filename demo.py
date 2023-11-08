import calendar
from io import StringIO
import json
from dash import Dash, html, dcc, Input, Output, callback,no_update,dash_table # type: ignore
from datetime import time, datetime, date # type: ignore
import datetime
import os
import sys
from matplotlib import colors
from cron_descriptor import ExpressionSchedular
import json
import calendar
import argparse
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
from colormap import rgb2hex # type: ignore




TOTAL_HOURS_PER_DAY = 24
TOTAL_MINUTES_PER_HOUR =60
FILE_PATH = 'test.json'
OUTPUT_PATH =''
cur_hour_list= [None]*TOTAL_MINUTES_PER_HOUR
idlist = [None]*TOTAL_MINUTES_PER_HOUR
date_object = date.today()
hour_df = []
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

def visualize_by_month(TOTAL_DAYS_PER_MONTH, iflow_daily_frequency, qt):

    
    xticks = np.arange(1, TOTAL_DAYS_PER_MONTH+1)
    xlabels = [date(qt.year, qt.month, i).strftime("%m/%d")
               for i in range(1, TOTAL_DAYS_PER_MONTH+1)]
   

    fig = go.Figure(data=[go.Histogram(x=iflow_daily_frequency,
                                       xbins=dict(start=1, end=TOTAL_DAYS_PER_MONTH+1),
                                       histfunc="count",
                                       marker={'color': get_color_map(iflow_daily_frequency, 1, TOTAL_DAYS_PER_MONTH+1,1)})])

    #fig = px.histogram(x=iflow_daily_frequency, marginal='rug')
    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,
                          title = dict(text = 'Date')
                      ),
                      yaxis=dict(
                          title = dict(text = 'Number of iFlows'),
                          tickformat = "d"
                      ),
                      hoverlabel_align='right'
                      )
    return fig

def visualize_by_day_new(iflow_hourly_fequency):

    xticks = np.arange(0, TOTAL_HOURS_PER_DAY)
    xlabels = [time(i, 0).strftime("%H:%M")
               for i in range(0, TOTAL_HOURS_PER_DAY)]

    fig = go.Figure(data=[go.Histogram(x=iflow_hourly_fequency,
                                       xbins=dict(start=0, end=24,size=1),
                                       histfunc="count",
                                       marker={'color': get_color_map(iflow_hourly_fequency, 1, TOTAL_HOURS_PER_DAY,0)})])

    
    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,
                          title = dict(text = 'Hours')
                      ),
                      yaxis=dict(
                          title = dict(text = 'Number of iFlows'),
                          tickformat = "d"
                      ),
                      hoverlabel_align='right'
                      )
    return fig


def get_color_map(freq, gap, total,min):
    fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)

    N, bins, patches = ax.hist(freq, bins=np.arange(
        min, total+ gap, gap), edgecolor="white")
    fracs = N / N.max()
    norm = colors.Normalize(fracs.min(), fracs.max())
    
    colormap = []
    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        colormap.append(rgb2hex(color[0], color[1], color[2], color[3]))
    
    return colormap


def visualize_by_hour_new(iflow_list, iflow_ids, cur_hour):
    global hour_df
    TIME_GAP = 1
    cur_hour_list = [None]*TOTAL_MINUTES_PER_HOUR
    iflow_min_freq = []

    for iflow_id in iflow_ids:

        if len(iflow_list[iflow_id][0]["timestamps"]) == 0:
            continue
        for stamp in iflow_list[iflow_id][0]["timestamps"]:
            # print(iflow_timestamp)
            if stamp.hour == cur_hour:
                if cur_hour_list[stamp.minute] == None:
                    cur_hour_list[stamp.minute] = [iflow_id]
                else:
                    cur_hour_list[stamp.minute].append(iflow_id)
                iflow_min_freq.append(float(stamp.minute+float(stamp.second/60)))

    xticks = np.arange(0, TOTAL_MINUTES_PER_HOUR,TIME_GAP)
    xlabels = [time(cur_hour, i, 0).strftime("%M:%S")
               for i in range(0, TOTAL_MINUTES_PER_HOUR,TIME_GAP)]

    hour_df = [get_idlist(i, i + TIME_GAP, cur_hour_list)
                   for i in range(0, TOTAL_MINUTES_PER_HOUR, TIME_GAP)]

    # fig = go.Figure(data=[go.Histogram(x=iflow_min_freq,
    #                                    xbins=dict(
    #                                        start=0, end=TOTAL_MINUTES_PER_HOUR),
    #                                    nbinsx=int(
    #                                        TOTAL_MINUTES_PER_HOUR/TIME_GAP),
    #                                 #    customdata=custom_data,
    #                                 #    hovertemplate="%{customdata}",
    #                                    histfunc="count",
    #                                    marker={'color': get_color_map(iflow_min_freq, TIME_GAP, TOTAL_MINUTES_PER_HOUR,0)})])
    # df = pd.DataFrame({'iflow_id':cur_hour_list})
    counts, bins = np.histogram(iflow_min_freq, bins=range(0, 60+1, TIME_GAP))
    # print(len(counts))
    # print(len(bins[:-1]))
    # df = pd.DataFrame({'x':bins[:-1], 'y':counts})
    
    fig = px.histogram(x=iflow_min_freq,nbins=60, range_y=[0,(1+counts.max()/5)*5],marginal='rug',color_discrete_sequence=px.colors.qualitative.Prism)
   # fig.show()
    # fig.update_traces(xbins_size=dict(start=0, end=TOTAL_MINUTES_PER_HOUR))
    # fig.update_traces(xbins=dict( # bins used for histogram
    #     start=0.0,
    #     end=1400.0,
    #     size=40
    # ))
    
    fig.update_traces(xbins=dict(start=0, end=TOTAL_MINUTES_PER_HOUR), selector=dict(type='histogram'))
    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,                
                          title = dict(text = 'Minutes')
                      ),
                      yaxis=dict(
                          title = dict(text = 'Number of iFlows'),
                          tickformat = "d",
                          
                       
                      ),
                      hoverlabel_align='right',
                     
                      )
    return fig


def get_idlist(left, right, cur_hour_list):
    global hour_df
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
                idcount = [cur_hour_list[i].count(j) for j in idlist]
    # hour_df =df
    return df


def get_iflow_daily_frequency(LAST_DAY_OF_MONTH, iflow_list, qt):

    iflow_by_month = []
    for iflow_id in iflow_list:
        expre = iflow_list[iflow_id][0]["value"]
        if expre != "fireNow=true":
            for i in range(1, LAST_DAY_OF_MONTH+1):
                sched = ExpressionSchedular(
                    expre, qt=datetime.date(qt.year, qt.month, i))
                st = sched.get_schedule_timetable()
                for j in range(0, len(st)):
                    iflow_by_month.append(i)
    return iflow_by_month


def get_iflow_hourly_fequency(iflow_list, qt):
    # iflow_by_month = [0]*(1+LAST_DAY_OF_MONTH)

    id_list = []
    time_list = []
    for iflow_id in iflow_list:
        expre = iflow_list[iflow_id][0]["value"]
        if expre != "fireNow=true":
            sched = ExpressionSchedular(expre, qt)
            iflow_list[iflow_id][0]["timestamps"] = sched.get_schedule_timetable()
            for stamp in iflow_list[iflow_id][0]["timestamps"]:
                id_list.append(iflow_id)
                time_list.append(stamp.hour+float(stamp.minute/60))
    iflow_hourly_fequency = pd.DataFrame(
        {"iflow_id": id_list, "time": time_list})

    return time_list


def get_iflow_by_hour(iflow_list, qt):
    iflow_by_hour = dict.fromkeys(list(range(TOTAL_HOURS_PER_DAY)))
    for iflow_id in iflow_list:
        expre = iflow_list[iflow_id][0]["value"]
        if expre != "fireNow=true":
            sched = ExpressionSchedular(expre, qt)
            iflow_list[iflow_id][0]["timestamps"] = sched.get_schedule_timetable()
            for stamp in iflow_list[iflow_id][0]["timestamps"]:
                if iflow_by_hour[stamp.hour] is None:
                    iflow_by_hour[stamp.hour] = []
                if iflow_by_hour[stamp.hour].count(iflow_id) == 0:
                    iflow_by_hour[stamp.hour].append(iflow_id)
    return iflow_by_hour

@callback(
    Output('iflow_by_month', 'figure'),
   # Output('iflow_by_day', 'figure'),
    Input('my-date-picker-single', 'date'))
def update_month_figure(date_value):
    if date_value is None:
        return no_update
    string_prefix = 'You have selected: '
    if date_value is not None:
        global date_object
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%B %d, %Y')
        
        _, LAST_DAY_OF_MONTH = calendar.monthrange(date_object.year, date_object.month)
        return visualize_by_month(LAST_DAY_OF_MONTH, get_iflow_daily_frequency(LAST_DAY_OF_MONTH, iflow_list, date_object), date_object)
    #,visualize_by_day_new(get_iflow_hourly_fequency(iflow_list, date_object))

@callback(
    Output('iflow_by_day', 'figure'),
    Input('iflow_by_month', 'clickData'))
def display_day(clickData):
    # print(clickData)
    # if clickData is not None:
    #     print(clickData)
    global date_object
    
    if clickData is None:
        return no_update
    if clickData is not None:
        date_object = date(date_object.year,date_object.month,clickData['points'][0]['binNumber']+1)
    
    return visualize_by_day_new(get_iflow_hourly_fequency(iflow_list, date_object))


@callback(
    Output('iflow_by_hour', 'figure'),
    Input('iflow_by_day', 'clickData'))
def display_hour(clickData):
    global date_object
    if clickData is None:
        return no_update
    cur_hour = 0
    if clickData is not None:
        cur_hour =clickData['points'][0]['binNumber']
    
    return visualize_by_hour_new(iflow_list, get_iflow_by_hour(iflow_list, date_object)[cur_hour], cur_hour)

@callback(
    Output('dtable', "data"),
    Input('iflow_by_hour', 'clickData'),
)
def update_table(clickData):
    if clickData is None:
        return no_update
    bin = clickData['points'][0]['binNumber']
    
    return hour_df[bin].to_dict('records')
    # print(clickData['points'][0]['customdata'][0])
    # dfstr = clickData['points'][0]['customdata'].replace('<br>', '\n')
    # return  pd.read_csv(StringIO(dfstr), sep='\s+')

if __name__ == '__main__':
    FILE_PATH = 'test.json'
    iflow_list = []

    

    with open(FILE_PATH, "r") as file:
        iflow_list = json.load(file)

    app = Dash(__name__)
    dtable = dash_table.DataTable(data=[], page_size=10)
    app.layout = html.Div([
        html.Div([
            html.A(id='output-container-date-picker-single',children="Select a date: "),
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
           
            dash_table.DataTable(data=[], page_size=10, id='dtable')
            
        ], style={'display': 'inline-block'}),
        # html.Div([
        #     dcc.Markdown(id = 'dtable',children="")
           
        # ], )
        
        # html.Div(className='row', children=[
        #     html.Div([
        #         dcc.Markdown("""
        #             **Click Data**

        #             Click on points in the graph.
        #         """),
        #         html.Pre(id='click-data', style=styles['pre']),
        #     ], className='three columns')
        # ])
        # html.Div([
        #     dcc.Graph(id='iflow_by_month'),
        #     dcc.Graph(id='iflow_by_day'),
        # ], style={'display': 'inline-block', 'width': '100%'}),

    ],style={'text-align': 'center'})
    app.run_server(debug=True)

    # if visualize_type == 'month':

    #     visualize_by_month(LAST_DAY_OF_MONTH, get_iflow_daily_frequency(
    #         LAST_DAY_OF_MONTH, iflow_list, qt), qt)
    # elif visualize_type == 'day':
    #     visualize_by_day_new(get_iflow_hourly_fequency(iflow_list, qt))
    #     # visualize_by_day(get_iflow_hourly_fequency(iflow_list,qt))
    # elif visualize_type == 'hour':
    #     visualize_by_hour_new(iflow_list, get_iflow_by_hour(
    #         iflow_list, qt)[qt.hour], qt.hour)
