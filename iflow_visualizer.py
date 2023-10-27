# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('--visualize_type', type=str,default = None)
# parser.add_argument('--filename', type=str,default = None)
# parser.add_argument('--date', type=str,default = None)

# args = parser.parse_args()
import matplotlib.pyplot as plt
import numpy as np
from datetime import time, datetime
import json
from matplotlib import colors
from cron_descriptor import ExpressionSchedular
import datetime
from datetime import date
import json

TOTAL_HOURS_PER_DAY = 24
FILE_PATH = 'test.json'

iflow_timestamps = []
iflow_expression = []
iflow_hourly_fequency = []
iflow_by_hour = dict.fromkeys(list(range(TOTAL_HOURS_PER_DAY)))

with open(FILE_PATH,"r") as file:
    iflow_expression = json.loads(file.read())["iflow_list"]

for iflow in iflow_expression:
    sched = ExpressionSchedular(iflow["cron"], qt=datetime.datetime.now())
    iflow_timestamps.append([i for i in sched.get_schedule_timetable()])
    for iflow_timestamp in iflow_timestamps:
        # print(iflow_timestamp)
        for stamp in iflow_timestamp:
            iflow_hourly_fequency.append(stamp.hour)
            if iflow_by_hour[stamp.hour] is None:
                iflow_by_hour[stamp.hour] = []
            iflow_by_hour[stamp.hour].append(iflow['iflow'])


plt.style.use('_mpl-gallery')
iflow_hourly_max = ((max(iflow_hourly_fequency)/10) + 1) * 10

fig, ax = plt.subplots(figsize=(12, 3), tight_layout=True)
# N is the count in each bin, bins is the lower-limit of the bin
N, bins, patches = ax.hist(iflow_hourly_fequency, bins=range(25), edgecolor="white")

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
xlabels = [time(i, 0).strftime("%H:%M") for i in range(0, TOTAL_HOURS_PER_DAY)]
ax.set(xlim=(0, 24), ylim=(0, ((N.max()/10) + 3) * 10))
ax.set_xticks(xticks, labels=xlabels)

plt.show()
