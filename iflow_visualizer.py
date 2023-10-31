from datetime import time, datetime, date
from matplotlib import colors
from cron_descriptor import ExpressionSchedular
import datetime
import json
import calendar
import argparse
import matplotlib.pyplot as plt
import numpy as np

TOTAL_HOURS_PER_DAY = 24
FILE_PATH = 'test.json'


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

    plt.show()


def visualize_by_day(iflow_hourly_fequency):

    iflow_hourly_max = ((max(iflow_hourly_fequency)/10) + 1) * 10

    fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)
    # N is the count in each bin, bins is the lower-limit of the bin
    N, bins, patches = ax.hist(
        iflow_hourly_fequency, bins=range(TOTAL_HOURS_PER_DAY+1), edgecolor="white")

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
    ax.set_xticks(xticks, labels=xlabels,fontsize=8)

    plt.show()


def visualize_by_hour(iflow_list,iflow_ids,cur_hour):
    # Declaring a figure "gnt"
    fig, gnt = plt.subplots(figsize=(8, 3))

    # Setting ticks on y-axis
    y_ticks = [int(i*10+15) for i in range(0, len(iflow_ids))]

    # Setting Y-axis limits
    gnt.set_ylim(0, len(iflow_ids)*10+15)

    # Setting X-axis limits
    gnt.set_xlim(0, 60)

    # Setting labels for x-axis and y-axis
    gnt.set_xlabel('Time Stamp')
    gnt.set_ylabel('iFlow')

    gnt.set_yticks(y_ticks)
    # Labelling tickes of y-axis
    gnt.set_yticklabels(iflow_ids)

    # Setting graph attribute
    gnt.grid(True)
 
    LENGTH_PER_JOB = 0.2
    # Declaring a bar in schedule
    index = 0
    for iflow_id in iflow_ids:

        cur_hour_list = []
        if len(iflow_list[iflow_id][0]["timestamps"]) == 0:
            continue
        for stamp in iflow_list[iflow_id][0]["timestamps"]:
            # print(iflow_timestamp)
            if stamp.hour == cur_hour:
                cur_hour_list.append(
                    (float(stamp.minute + stamp.second/60), float(LENGTH_PER_JOB)))
        gnt.broken_barh(cur_hour_list, ((index+1)*10, 9),
                        facecolors=('tab:red'))
        index += 1

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
    iflow_hourly_fequency = []
    for iflow_id in iflow_list:
        expre = iflow_list[iflow_id][0]["value"]
        if expre != "fireNow=true":
            sched = ExpressionSchedular(expre, qt)
            iflow_list[iflow_id][0]["timestamps"] = sched.get_schedule_timetable()
            for stamp in iflow_list[iflow_id][0]["timestamps"]:
                iflow_hourly_fequency.append(stamp.hour)
                # if iflow_by_hour[stamp.hour] is None:
                #     iflow_by_hour[stamp.hour] = []
                # if iflow_by_hour[stamp.hour].count(iflow_id) == 0:
                #     iflow_by_hour[stamp.hour].append(iflow_id)
    return iflow_hourly_fequency

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

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--visualize_type', choices=["hour","month","day"], default=None,required=True)
    parser.add_argument('--filename', type=str, default=None)
    parser.add_argument('--year', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD
    parser.add_argument('--month', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD
    parser.add_argument('--day', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD
    parser.add_argument('--hour', type=int, default=None, help ='If None, default set to current year') #YYYY-MM-DD

    args = parser.parse_args()
    
    qt = datetime.datetime.now()
    if args.year is not None:
        qt = qt.replace(year = args.year)
    if args.month is not None:
        qt = qt.replace(month = args.month)
    if args.day is not None:
        qt = qt.replace(day = args.day)
    if args.hour is not None:
        qt = qt.replace(hour = args.hour)
        print(qt.hour)
        
    
    _, LAST_DAY_OF_MONTH = calendar.monthrange(qt.year, qt.month)
    iflow_list = []

    # visualize_type= 'day'
    # qt.replace(day = 2)
    
    visualize_type = args.visualize_type
  
    with open(FILE_PATH, "r") as file:
        iflow_list = json.load(file)

    if visualize_type == 'month':
        
        visualize_by_month(LAST_DAY_OF_MONTH, get_iflow_by_month(LAST_DAY_OF_MONTH, iflow_list,qt),qt)
    elif visualize_type == 'day':
        visualize_by_day(get_iflow_hourly_fequency(iflow_list,qt))
    elif visualize_type == 'hour':
        visualize_by_hour(iflow_list,get_iflow_by_hour(iflow_list,qt)[qt.hour],qt.hour)
    

