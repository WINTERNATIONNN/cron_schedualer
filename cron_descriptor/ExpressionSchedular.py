from __future__ import annotations

import calendar
from datetime import date, datetime, time
from datetime import timezone
from enum import IntEnum
from typing import Set, Tuple, Union, cast
from .ExpressionParser import ExpressionParser
from .Options import Options

SpecItem = Union[int, Tuple[int, int]]

MIN_STAMP_FOR_SECOND_N_MINUTE = 0
MAX_STAMP_FOR_SECOND_N_MINUTE = 59
MIN_STAMP_FOR_HOUR = 0
MAX_STAMP_FOR_HOUR = 24


class ExpressionSchedular(object):

    _expression_parts = []
    _expression = ''
    _cur_parts = []
    _qt = datetime.now()
    _nt = datetime.__new__

    def __init__(self, expression, qt: date, options=None):
        """Initializes a new instance of the ExpressionDescriptor

        Args:
            expression: The cron expression string
            options: Options to control the output description
        Raises:
            WrongArgumentException: if kwarg is unknown

        """
        if options is None:
            options = Options()
        self._expression = expression
        self._options = options
        self._expression_parts = []
        self._qt = qt  # query time

        parser = ExpressionParser(self._expression, self._options)
        self._expression_parts = parser.parse()


    def get_schedule_timetable(self):
        timetable = []
        yr_of_next = self.get_next_year_or_month(self._expression_parts[6], self._qt.year)
        month_of_next = self.get_next_year_or_month(self._expression_parts[4], self._qt.month)
        day_of_next = self.get_next_date(yr_of_next, month_of_next)
        if yr_of_next == self._qt.year and month_of_next == self._qt.month and day_of_next == self._qt.day:
            secondlist = self.get_time_list(self._expression_parts[0], 0, 59)
            if self._expression_parts[0] =='':
                secondlist = []
            
            minutelist = self.get_time_list(self._expression_parts[1], 0, 59)
            hourlist = self.get_time_list(self._expression_parts[2], 0, 23)
            for hour in hourlist:
                for minute in minutelist:
                    #print(time(int(hour), int(minute)))
                    if len(secondlist) == 0 :

                        timetable.append(time(int(hour), int(minute),0))
                    for second in secondlist:
                        timetable.append(time(int(hour), int(minute),int(second)))
                    # print(time(int(hour), int(minute), int(second)))

            return timetable
        else:
            return []

    def get_time_list(self, epr, min_stamp, max_stamp):
        """Returns the list of timestamp (hour, minute, second) trigger by the given expression

        Args:
            epr: the expression of (hour, minute, second)
        Returns:
            None: no running schedule
            list: list of timestamp

        """
        times = []
        
        if '*' == epr or epr == '':
        #if '*' and '' means it is scheduled to run every (hour/minute/second) within the given time
            return [str(i) for i in range(min_stamp, max_stamp+1)]
        if ',' in epr:
        #Seperate the step
            times = epr.split(',')
        else:
            times.append(epr)
        size = len(times)
        for i in range(0, size):
            time = str(times[i])
            #For each step see if it has predefine range schedule to run in 
            if '-' in time:
                times.remove(time)
                i -= 1
                incre = 1
                if '/' in time:
                #For the step designated interval 
                    range_time, incre = time.split('/')
                    start_time, end_time = map(int, range_time.split('-'))
                else:
                    start_time, end_time = map(int, time.split('-'))
                if start_time > end_time:
                    #if it has reversed interval, seperate as two part to calculate the timestamp
                    #e.g in <minutes> field 45-15 -> 0-15,45-59
                    times.extend([str(i) for i in range(start_time, max_stamp+1, int(incre))])
                    times.extend([str(i) for i in range(min_stamp, end_time+1, int(incre))])
                else:
                    times.extend([str(i) for i in range(start_time, end_time+1, int(incre))])
            elif '/' in time:
                times.remove(time)
                i -= 1
                start_time, incre = time.split('/')
                if start_time == '*':
                    start_time = 0
                else:
                    start_time = int(start_time)
                incre = int(incre)
                times.extend([str(i)
                             for i in range(start_time, max_stamp, incre)])
                # print(i)
        times = [int(i) for i in times]
        times.sort()
        return times

    def get_nearest_weekday(self, yr_of_next, month_of_next, epr_date, firstd_of_month, lastd_of_month):
        """Returns the nearest weekday of the given epr_date. This is the helper method for using special symbol 'W' in DOM

        Args:
            yr_of_next: the year of next schedule timestamp trigger
            month_of_next: the month of next schedule timestamp trigger
            epr_date: the day of the month of next schedule timestamp trigger
            firstd_of_month: the first day of the month of next schedule timestamp trigger
            lastd_of_month: the last day of the month of next schedule timestamp trigger

        Returns:
            The nearest weekday of the given epr_date.

        """
        if calendar.weekday(yr_of_next, month_of_next, epr_date) not in set((5, 6)):
            return epr_date
        if epr_date == firstd_of_month:
            # If it is the first day of the month, count forward
            while calendar.weekday(yr_of_next, month_of_next, epr_date) in set((5, 6)):
                epr_date += 1
            return epr_date
        elif epr_date == lastd_of_month:
            while calendar.weekday(yr_of_next, month_of_next, epr_date) in set((5, 6)):
                epr_date -= 1
            return epr_date
        else:
            forward_date = epr_date
            backward_date = epr_date
            while calendar.weekday(yr_of_next, month_of_next, forward_date) in set((5, 6)) and calendar.weekday(yr_of_next, month_of_next, forward_date) in set((5, 6)):
                forward_date += 1
                backward_date -= 1
                if calendar.weekday(yr_of_next, month_of_next, forward_date) not in set((5, 6)):
                    return forward_date
                elif calendar.weekday(yr_of_next, month_of_next, backward_date) not in set((5, 6)):
                    return backward_date

    def get_next_year_or_month(self, epr, qt_ym):
        """Returns the year or month of next schedule timestamp trigger by the given expression

        Args:
            epr: the expression whether year or month
        Returns:
            -1: no next schedule
            int: the value of year of month of next schedule

        """
        epr_ym = epr
        # cur_yr = datetime.now().year #current year
        yms = []
        if '*' in epr_ym or epr_ym == '':
            return qt_ym
        if ',' in epr_ym:
            yms = epr_ym.split(',')
        else:
            yms.append(epr_ym)
        size = len(yms)
        for i in range(0, size):
            ym = yms[i]
            if '-' in ym:
                yms.remove(ym)
                incre = 1
                if '/' in ym:
                    range_year, incre = ym.split('/')
                    start_ym, end_ym = map(int, range_year.split('-'))
                else:
                    start_ym, end_ym = map(int, ym.split('-'))
                yms.extend([i for i in range(start_ym, end_ym+1, int(incre))])                    
            elif '/' in ym:
                yms.remove(ym)
                start_ym, incre = map(int, ym.split('/'))
                for i in range(start_ym, qt_ym+1, incre):
                    yms.append(i)

        yms.sort()
        for ym in yms:
            if int(ym) >= int(qt_ym):
                return ym
        return yms[0]

    def get_next_date(self, yr_of_next, month_of_next):
        """Returns the day of next schedule timestamp trigger by the given expression

        Args:
            yr_of_next: the year of next schedule
            month_of_next: the month of next schedule
        Returns:
            -1: no next schedule
            int: the value of day of next schedule

        """
        DOM = self._expression_parts[3]
        DOW = self._expression_parts[5]
        epr_month = self._expression_parts[4]
        next_date = -1
        firstd_of_month = 1
        _, lastd_of_month = calendar.monthrange(
            int(yr_of_next), int(month_of_next))
        if DOW == '*' and DOM != '*':
            # Using DOM ,-*?/ W L
            # firstd_of_month, lastd_of_month = calendar.monthrange(yr_of_next, month_of_next)
            if 'L' in DOM:
                next_date = lastd_of_month
            elif 'W' in DOM:
                epr_date = DOM.removesuffix('W')
                next_date = self.get_nearest_weekday(
                    yr_of_next, month_of_next, epr_date, firstd_of_month, lastd_of_month)
            else:
                next_date = self.get_next_year_or_month(DOM, self._qt.day)

        elif DOM == '*' and DOW != '*':
            # Using Day-Of-Week
            if '#' in DOW:
                weekday, number = DOW.split('#')
                if self._qt.weekday != int(weekday)-1:
                    next_date = -1
                earliest_date = max((number - 1)*7, 1)
                # Get the earliest date possible for the weekday
                # e.g. the second Tuesday possible for any month would be the 8th
                while calendar.weekday(yr_of_next, month_of_next, earliest_date) != int(weekday)-1:
                    earliest_date += 1
                next_date = earliest_date
            elif 'L' in DOW:
                weekday = DOW.removesuffix('L')
                next_date = lastd_of_month
                while calendar.weekday(yr_of_next, month_of_next, next_date) != int(weekday)-1:
                    next_date -= 1
            else:
                # Get the next weekday in the schedule
                next_weekday = self.get_next_year_or_month(
                    DOW, int(calendar.weekday(yr_of_next, month_of_next, self._qt.day))+1)

                next_date = self._qt.day
                while next_date <= lastd_of_month:
                    if calendar.weekday(yr_of_next, month_of_next, next_date) == int(next_weekday)-1:
                        break
                    next_date += 1
        else:
            next_date = self._qt.day
        return next_date
