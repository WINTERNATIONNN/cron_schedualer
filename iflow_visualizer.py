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
TOTAL_MINUTES_PER_HOUR =60
FILE_PATH = 'test.json'
OUTPUT_PATH =''
cur_hour_list= [None]*TOTAL_MINUTES_PER_HOUR
idlist = [None]*TOTAL_MINUTES_PER_HOUR

def visualize_by_month(TOTAL_DAYS_PER_MONTH, iflow_by_month, qt):

    iflow_monthly_max = ((max(iflow_by_month)/10) + 2) * 10

    fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)

    bins = np.arange(TOTAL_DAYS_PER_MONTH+1)+0.5

    N, bins, patches = ax.hist(
        bins[:-1], bins, weights=iflow_by_month[1:], edgecolor="white")

    fracs = N / N.max()

    norm = colors.Normalize(fracs.min(), fracs.max())

    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)

    plt.ylabel('number of iflow')
    plt.xlabel('date')

    xticks = np.arange(1, TOTAL_DAYS_PER_MONTH+1)
    xlabels = [date(qt.year, qt.month, i).strftime("%m/%d")
               for i in range(1, TOTAL_DAYS_PER_MONTH+1)]
    ax.set(xlim=(0, TOTAL_DAYS_PER_MONTH+1), ylim=(0, ((N.max()/10) + 3) * 10))
    ax.set_xticks(xticks, labels=xlabels, fontsize=5)
    plt.savefig(os.path.join(OUTPUT_PATH,'figure_by_month.png'))
    plt.show()


def visualize_by_day(iflow_hourly_fequency):

    iflow_hourly_max = ((max(iflow_hourly_fequency)/10) + 1) * 10

    fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)
    fig.canvas.mpl_connect('pick_event', onpick)
    # N is the count in each bin, bins is the lower-limit of the bin
    N, bins, patches = ax.hist(
        iflow_hourly_fequency, bins=range(TOTAL_HOURS_PER_DAY+1), edgecolor="white",picker=True)

    # We'll color code by height, but you could use any scalar
    fracs = N / N.max()

    # we need to normalize the data to 0..1 for the full range of the colormap
    norm = colors.Normalize(fracs.min(), fracs.max())

    # Now, we'll loop through our objects and set the color of each accordingly
    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)

    plt.ylabel('number of iflow')
    plt.xlabel('time')

    xticks = np.arange(0, TOTAL_HOURS_PER_DAY)
    xlabels = [time(i, 0).strftime("%H:%M")
               for i in range(0, TOTAL_HOURS_PER_DAY)]
    ax.set(xlim=(0, TOTAL_HOURS_PER_DAY), ylim=(0, ((N.max()/10) + 3) * 10))
    ax.set_xticks(xticks, labels=xlabels,fontsize=10)
    plt.savefig(os.path.join(OUTPUT_PATH,'figure_by_day.png'))
    plt.show()

# def visualize_by_day_new(iflow_hourly_fequency):

#     # iflow_hourly_max = ((max(iflow_hourly_fequency)/10) + 1) * 10

#     fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)
#     # N is the count in each bin, bins is the lower-limit of the bin
#     N, bins, patches = ax.hist(
#         iflow_hourly_fequency, bins=range(TOTAL_HOURS_PER_DAY+1), edgecolor="white")

#     # We'll color code by height, but you could use any scalar
#     fracs = N / N.max()

#     # we need to normalize the data to 0..1 for the full range of the colormap
#     norm = colors.Normalize(fracs.min(), fracs.max())

#     # # Now, we'll loop through our objects and set the color of each accordingly
#     colormap = []
#     for thisfrac, thispatch in zip(fracs, patches):
#         color = plt.cm.viridis(norm(thisfrac))
#         thispatch.set_facecolor(color)
#         colormap.append(rgb2hex(color[0], color[1], color[2], color[3]))
      
#     plt.ylabel('number of iflow')
#     plt.xlabel('time')

#     xticks = np.arange(0, TOTAL_HOURS_PER_DAY)
#     xlabels = [time(i, 0).strftime("%H:%M")
#                for i in range(0, TOTAL_HOURS_PER_DAY)]

#     fig = go.Figure(data=[go.Histogram(x=iflow_hourly_fequency,
#                                     xbins=dict(start=0,end=24),
#                                     histfunc="count",
#                                     marker={'color': colormap})])
#    # fig.show()
#     fig.update_layout(bargap=0.2,
#                     xaxis = dict(
#                         tickmode = 'array',
#                         tickvals = xticks,
#                         ticktext = xlabels
#                     )
#     )
#     fig.show()

def get_color_map(freq,gap):
    fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)
 
    N, bins, patches = ax.hist(freq, bins=np.arange(0, TOTAL_MINUTES_PER_HOUR + gap, gap), edgecolor="white")
    fracs = N / N.max()
    norm = colors.Normalize(fracs.min(), fracs.max())
 
    colormap = []
    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        colormap.append(rgb2hex(color[0], color[1], color[2], color[3]))
    return colormap

# def visualize_by_hour_new(iflow_list,iflow_ids,cur_hour):
#     TIME_GAP = 1
#     cur_hour_list= [None]*TOTAL_MINUTES_PER_HOUR
#     iflow_min_freq = []
#     idlist = [None]*TOTAL_MINUTES_PER_HOUR
#     print(iflow_ids)
#     for iflow_id in iflow_ids:
        
#         if len(iflow_list[iflow_id][0]["timestamps"]) == 0:
#             continue
#         for stamp in iflow_list[iflow_id][0]["timestamps"]:
#             #print(iflow_id +": "+str(stamp.minute))
#             if stamp.hour == cur_hour:
#                 if cur_hour_list[stamp.minute] ==None:
#                     cur_hour_list[stamp.minute]= [iflow_id]
#                 else:
#                     cur_hour_list[stamp.minute].append(iflow_id)
#                 iflow_min_freq.append(stamp.minute)

#     for i in range(0,60):
#         for iflow_id in iflow_ids:
#             cur = cur_hour_list[i].count(iflow_id)
#             if(cur != 0):
#                 if idlist[i] == None:
#                     idlist[i] = [iflow_id + ": " + str(cur)]
#                 else:
#                     idlist[i].append(iflow_id + ": " + str(cur))
   
#     plt.ylabel('number of iflow')
#     plt.xlabel('time')

#     xticks = np.arange(0, TOTAL_MINUTES_PER_HOUR)
#     xlabels = [time(cur_hour,i, 0).strftime("%M:%S")
#                for i in range(0, TOTAL_MINUTES_PER_HOUR)]

#     fig = go.Figure(data=[go.Histogram(x=iflow_min_freq,
#                                     xbins=dict(start=0,end=TOTAL_MINUTES_PER_HOUR),
#                                     nbinsx=int(TOTAL_MINUTES_PER_HOUR/TIME_GAP),                                   
#                                     histfunc="count",customdata = idlist,                                  
#                                     marker={'color': get_color_map(iflow_min_freq,TIME_GAP)})])
#    # fig.show()
#     fig.update_traces(hovertemplate='On %{x} have %{customdata}')
#     fig.update_layout(bargap=0.2,
#                     xaxis = dict(
#                         tickmode = 'array',
#                         tickvals = xticks,
#                         ticktext = xlabels,
#                     )
#     )
#     fig.show()

def visualize_by_hour(iflow_list,iflow_ids,cur_hour):
    # def visualize_by_hour_new(iflow_list,iflow_ids,cur_hour):
    TIME_GAP = 1
    
    iflow_min_freq = []
    idlist = [None]*TOTAL_MINUTES_PER_HOUR
    for iflow_id in iflow_ids:
        
        if len(iflow_list[iflow_id][0]["timestamps"]) == 0:
            continue
        for stamp in iflow_list[iflow_id][0]["timestamps"]:
            #print(iflow_id +": "+str(stamp.minute))
            if stamp.hour == cur_hour:
                if cur_hour_list[stamp.minute] ==None:
                    cur_hour_list[stamp.minute]= [iflow_id]
                else:
                    cur_hour_list[stamp.minute].append(iflow_id)
                iflow_min_freq.append(stamp.minute)
    for i in range(0,60):
        for iflow_id in iflow_ids:
            cur = cur_hour_list[i].count(iflow_id)
           
                
            

    #print(idlist)
    iflow_hourly_max = ((max(iflow_min_freq)/10) + 1) * 10

    fig, ax = plt.subplots(figsize=(15, 3), tight_layout=True)
    fig.canvas.mpl_connect('pick_event', onpick)
    # N is the count in each bin, bins is the lower-limit of the bin
    N, bins, patches = ax.hist(
        iflow_min_freq, bins=range(TOTAL_MINUTES_PER_HOUR+1), edgecolor="white",picker=True)

    # We'll color code by height, but you could use any scalar
    fracs = N / N.max()

    # we need to normalize the data to 0..1 for the full range of the colormap
    norm = colors.Normalize(fracs.min(), fracs.max())

    # Now, we'll loop through our objects and set the color of each accordingly
    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)

    plt.ylabel('number of iflow')
    plt.xlabel('time')

    xticks = np.arange(0, TOTAL_MINUTES_PER_HOUR)
    xlabels = [time(cur_hour,i, 0).strftime("%M:%S")
               for i in range(0, TOTAL_MINUTES_PER_HOUR)]
    ax.set(xlim=(0, TOTAL_HOURS_PER_DAY), ylim=(0, ((N.max()/2)+1 ) * 2))
    ax.set_xticks(xticks, labels=xlabels,fontsize=5,rotation = 90)
    plt.savefig(os.path.join(OUTPUT_PATH,'figure_by_hour.png'))
    plt.show()


def get_iflow_by_month(LAST_DAY_OF_MONTH, iflow_list,qt):

    iflow_by_month = [0]*(1+LAST_DAY_OF_MONTH)
    for iflow_id in iflow_list:
        expre = iflow_list[iflow_id][0]["value"]
        if expre != "fireNow=true":
            for i in range(1, LAST_DAY_OF_MONTH+1):
                sched = ExpressionSchedular(expre, qt=datetime.date(qt.year, qt.month, i))
                st = sched.get_schedule_timetable()
                if len(st) > 0:
                    iflow_by_month[i] += len(st)
    return iflow_by_month


def get_iflow_hourly_fequency(iflow_list,qt):
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
    iflow_hourly_fequency = pd.DataFrame({"iflow_id":id_list,"time":time_list})

    return time_list

def get_iflow_by_hour(iflow_list,qt):
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

def onpick(event):
    bar = event.artist
    left = int(bar.get_x())
    right = int(left + bar.get_width())
    print(left)
    print(right)
    idlist = []
    df = pd.DataFrame({"id":[],"count":[]})
    for i in range(left,right):
        if cur_hour_list[i] is not None:
            idlist = list(set(cur_hour_list[i]))
            for id in idlist:
                if id in df["id"].values:
                    df.loc[df["id"] == id, "count"] += cur_hour_list[i].count(id)
                else:
                    df.loc[len(df.index)] = [id,cur_hour_list[i].count(id)]
                idcount = [cur_hour_list[i].count(j) for j in idlist]
    print(df)
    plt.table(cellText=df.values, colLabels=df.columns, loc='bottom')
    plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--visualize_type', choices=["hour","month","day"], default=None,required=True)
    parser.add_argument('--input_file_path', type=str, default=None)
    parser.add_argument('--output_file_path', type=str, default=".")
    parser.add_argument('--year', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD
    parser.add_argument('--month', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD
    parser.add_argument('--day', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD
    parser.add_argument('--hour', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD

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
        qt = qt.replace(year = args.year)
    if args.month is not None:
        qt = qt.replace(month = args.month)
    if args.day is not None:
        qt = qt.replace(day = args.day)
    if args.hour is not None:
        qt = qt.replace(hour = args.hour)
    
        
    
    _, LAST_DAY_OF_MONTH = calendar.monthrange(qt.year, qt.month)
    iflow_list = []
    
    visualize_type = args.visualize_type
  
    with open(FILE_PATH, "r") as file:
        iflow_list = json.load(file)

    if visualize_type == 'month':
        
        visualize_by_month(LAST_DAY_OF_MONTH, get_iflow_by_month(LAST_DAY_OF_MONTH, iflow_list,qt),qt)
    elif visualize_type == 'day':
        #visualize_by_day_new(get_iflow_hourly_fequency(iflow_list,qt))
        visualize_by_day(get_iflow_hourly_fequency(iflow_list,qt))
    elif visualize_type == 'hour':
        #visualize_by_hour_new(iflow_list,get_iflow_by_hour(iflow_list,qt)[qt.hour],qt.hour)
        visualize_by_hour(iflow_list,get_iflow_by_hour(iflow_list,qt)[qt.hour],qt.hour)