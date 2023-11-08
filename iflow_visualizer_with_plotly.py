from datetime import time, datetime, date
import os
import sys
from matplotlib import colors
from cron_descriptor import ExpressionSchedular
import datetime
import json
import calendar
import argparse
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from colormap import rgb2hex
TOTAL_HOURS_PER_DAY = 24
TOTAL_MINUTES_PER_HOUR = 60
FILE_PATH = 'test.json'
OUTPUT_PATH = ''


def visualize_by_month(TOTAL_DAYS_PER_MONTH, iflow_daily_frequency, qt):

    
    xticks = np.arange(1, TOTAL_DAYS_PER_MONTH+1)
    xlabels = [date(qt.year, qt.month, i).strftime("%m/%d")
               for i in range(1, TOTAL_DAYS_PER_MONTH+1)]
   

    fig = go.Figure(data=[go.Histogram(x=iflow_daily_frequency,
                                       xbins=dict(start=1, end=TOTAL_DAYS_PER_MONTH+1),
                                       histfunc="count",
                                       marker={'color': get_color_map(iflow_daily_frequency, 1, TOTAL_DAYS_PER_MONTH+1,1)})])
   # fig.show()
    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,
                          title = dict(text = 'Time')
                      ),
                      yaxis=dict(
                          title = dict(text = 'Number of iFlows'),
                          tickformat = "d"
                      ),
                      hoverlabel_align='right'
                      )
    fig.show()
    

def visualize_by_day_new(iflow_hourly_fequency):

    xticks = np.arange(0, TOTAL_HOURS_PER_DAY)
    xlabels = [time(i, 0).strftime("%H:%M")
               for i in range(0, TOTAL_HOURS_PER_DAY)]

    fig = go.Figure(data=[go.Histogram(x=iflow_hourly_fequency,
                                       xbins=dict(start=0, end=24),
                                       histfunc="count",
                                       marker={'color': get_color_map(iflow_hourly_fequency, 1, TOTAL_HOURS_PER_DAY,0)})])
   # fig.show()
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
    fig.show()


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
                iflow_min_freq.append(stamp.minute)

    xticks = np.arange(0, TOTAL_MINUTES_PER_HOUR,TIME_GAP)
    xlabels = [time(cur_hour, i, 0).strftime("%M:%S")
               for i in range(0, TOTAL_MINUTES_PER_HOUR,TIME_GAP)]

    custom_data = [get_idlist(i, i + TIME_GAP, cur_hour_list)
                   for i in range(0, TOTAL_MINUTES_PER_HOUR, TIME_GAP)]

    fig = go.Figure(data=[go.Histogram(x=iflow_min_freq,
                                       xbins=dict(
                                           start=0, end=TOTAL_MINUTES_PER_HOUR),
                                       nbinsx=int(
                                           TOTAL_MINUTES_PER_HOUR/TIME_GAP),
                                       customdata=custom_data,
                                       hovertemplate="%{customdata}",
                                       histfunc="count",
                                       marker={'color': get_color_map(iflow_min_freq, TIME_GAP, TOTAL_MINUTES_PER_HOUR,0)})])
   # fig.show()
    fig.update_layout(bargap=0.2,
                      xaxis=dict(
                          tickmode='array',
                          tickvals=xticks,
                          ticktext=xlabels,
                          title = dict(text = 'Time')
                      ),
                      yaxis=dict(
                          title = dict(text = 'Number of iFlows'),
                          tickformat = "d",
                          dtick = 1
                      ),
                      hoverlabel_align='right'
                      )
    fig.show()


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
                idcount = [cur_hour_list[i].count(j) for j in idlist]

    return df.to_string().replace('\n', '<br>')

# def update_text(fig):
#     fig.add_annotation(props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
#         bar = event.artist
#     left = int(bar.get_x())
#     right = int(left + bar.get_width())

#     ax = plt.gca()
#     for txt in ax.texts:
#         txt.set_visible(False)
#     props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
#     ax.text(0.05, 0.95, df, transform=ax.transAxes, fontsize=14,
#         verticalalignment='top', bbox=props)


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


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--visualize_type', choices=["hour", "month", "day"], default=None, required=True)
    parser.add_argument('--input_file_path', type=str, default=None)
    parser.add_argument('--output_file_path', type=str, default=".")
    parser.add_argument('--year', type=int, default=None,
                        help='If None, default set to current year')  # YYYY-MM-DD
    parser.add_argument('--month', type=int, default=None,
                        help='If None, default set to current year')  # YYYY-MM-DD
    parser.add_argument('--day', type=int, default=None,
                        help='If None, default set to current year')  # YYYY-MM-DD
    parser.add_argument('--hour', type=int, default=None,
                        help='If None, default set to current year')  # YYYY-MM-DD

    args = parser.parse_args()
    if not os.path.exists(args.input_file_path):
        print("Input file path does not exist. Please provide a valid file path.")
        sys.exit()
    if not os.path.exists(args.output_file_path):
        print("Output file path does not exist. Please provide a valid file path.")
        sys.exit()

    FILE_PATH = args.input_file_path
    qt = datetime.datetime.now()
    if args.year is not None:
        qt = qt.replace(year=args.year)
    if args.month is not None:
        qt = qt.replace(month=args.month)
    if args.day is not None:
        qt = qt.replace(day=args.day)
    if args.hour is not None:
        qt = qt.replace(hour=args.hour)

    _, LAST_DAY_OF_MONTH = calendar.monthrange(qt.year, qt.month)
    iflow_list = []

    visualize_type = args.visualize_type

    with open(FILE_PATH, "r") as file:
        iflow_list = json.load(file)

    if visualize_type == 'month':

        visualize_by_month(LAST_DAY_OF_MONTH, get_iflow_daily_frequency(
            LAST_DAY_OF_MONTH, iflow_list, qt), qt)
    elif visualize_type == 'day':
        visualize_by_day_new(get_iflow_hourly_fequency(iflow_list, qt))
        # visualize_by_day(get_iflow_hourly_fequency(iflow_list,qt))
    elif visualize_type == 'hour':
        visualize_by_hour_new(iflow_list, get_iflow_by_hour(
            iflow_list, qt)[qt.hour], qt.hour)
        # visualize_by_hour(iflow_list,get_iflow_by_hour(iflow_list,qt)[qt.hour],qt.hour)
