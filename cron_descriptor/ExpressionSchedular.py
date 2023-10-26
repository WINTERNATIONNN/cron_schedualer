from __future__ import annotations

import calendar
from datetime import date, datetime, time
from datetime import timedelta as td
from datetime import timezone
from enum import IntEnum
from typing import Set, Tuple, Union, cast
from .GetText import GetText
from .CasingTypeEnum import CasingTypeEnum
from .DescriptionTypeEnum import DescriptionTypeEnum
from .ExpressionParser import ExpressionParser
from .Options import Options
from .StringBuilder import StringBuilder
from .Exception import FormatException, WrongArgumentException

UTC = timezone.utc

SpecItem = Union[int, Tuple[int, int]]

RANGES = [
    range(0, 60),
    range(0, 24),
    range(1, 32),
    range(1, 13),
    range(0, 8),
]
SYMBOLIC_DAYS = "SUN MON TUE WED THU FRI SAT".split()
SYMBOLIC_MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
DAYS_IN_MONTH = [-1, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


class ExpressionSchedular(object):

    LAST = -1000
    LAST_WEEKDAY = -1001
    _expression_parts = []
    _expression = ''
    _cur_parts = []
    _qt = datetime.now()
    _nt = datetime.__new__

    def __init__(self, expression, qt: datetime, options=None):
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
        
        
     

    def get_time_list(self,epr,min_stamp,max_stamp):
        """Returns the year or month of next schedule timestamp trigger by the given expression
        Args:
            epr: the expression whether year or month
        Returns:
            -1: no next schedule
            int: the value of year of month of next schedule

        """
        times = []
        if '*' == epr or epr == '':
            return [str(i) for i in range(min_stamp, max_stamp+1)]
        if ',' in epr:
            times = epr.split(',')
        else:
            times.append(epr)
        size = len(times)
        for i in range(0, size):
            time = str(times[i])
            if '-' in time:
                times.remove(time)
                i -= 1
                incre = 1
                if '/' in time:
                    range_time, incre = time.split('/')
                    start_time, end_time = map(int, range_time.split('-'))
                else:
                    start_time, end_time = map(int, time.split('-'))
                if start_time > end_time:
                    times.extend([str(i) for i in range(start_time, max_stamp+1, int(incre))])
                    times.extend([str(i) for i in range(min_stamp, end_time+1, int(incre))])
                else:
                    for i in range(start_time, end_time+1, int(incre)):
                        times.append(str(i))
                
            elif '/' in time:
                times.remove(time)
                i -= 1
                start_time, incre = time.split('/')
                if start_time == '*':
                    start_time = 0
                else:
                    start_time = int(start_time)
                incre = int(incre)
                times.extend([str(i) for i in range(start_time, max_stamp, incre)])
                    #print(i)
        times = [int(i) for i in times]
        times.sort()
        return times      

    def get_schedule_timetable(self):
        timetable = []
        yr_of_next = self.get_next_year_or_month(self._expression_parts[6], self._qt.year)
        month_of_next = self.get_next_year_or_month(self._expression_parts[4], self._qt.month)
        print(yr_of_next)
        print(month_of_next)
        day_of_next = self.get_next_date(yr_of_next, month_of_next)
        if yr_of_next == self._qt.year and month_of_next == self._qt.month and day_of_next == self._qt.day:
            secondlist = self.get_time_list(self._expression_parts[0],0,59)
            minutelist = self.get_time_list(self._expression_parts[1],0,59)
            hourlist = self.get_time_list(self._expression_parts[2],0,23)
            for hour in hourlist:
                for minute in minutelist:
                    print(time(int(hour), int(minute)))
                    timetable.append(time(int(hour), int(minute)))
                    #for second in secondlist:
                        #print(time(int(hour), int(minute), int(second)))
                       
            return timetable
        else:
            return []
        
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
                for i in range(start_ym, end_ym+1, int(incre)):
                    yms.append(i)
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
        firstd_of_month, lastd_of_month = calendar.monthrange(
            yr_of_next, month_of_next)
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
            # Using DOW ,-*?/LC#
            if '#' in DOW:
                # FIXME: havent dvelop yet
                weekday, number = DOW.split('#')
                if self._qt.weekday != int(weekday)-1:
                    next_date = -1
                earliest_date = max((number - 1)*7, 1)
                # Get the earliest date possible for the weekday
                # e.g. the second Tuesday possible for any month would be the 8th
                while calendar.weekday(yr_of_next, month_of_next, earliest_date) != int(weekday)-1:
                    earliest_date += 1
                next_date = earliest_date

                # monthcal = calendar.monthdatescalendar(yr_of_next,month_of_next)
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
                        break;
                    next_date += 1
            

        else:
            next_date = self._qt.day
        return next_date
