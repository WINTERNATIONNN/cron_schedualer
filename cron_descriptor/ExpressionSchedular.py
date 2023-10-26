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
        yr_of_next = self.get_next_year_or_month(self._expression_parts[6],self._qt.year)
        print("year:" + str(yr_of_next))
        month_of_next = self.get_next_year_or_month(self._expression_parts[4],self._qt.month)
        print("month"+str(month_of_next))
        day_of_next = self.get_next_date(yr_of_next,month_of_next)
        print("day: "+str(day_of_next))
        self._nt = date(yr_of_next, month_of_next,day_of_next)

    def get_next_schedule_time(self):
        return self._nt

    def get_nearest_weekday(self,yr_of_next, month_of_next, epr_date, firstd_of_month, lastd_of_month):
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
      
        if '*' in epr_ym or epr_ym == '':
            return qt_ym
        elif ',' in epr_ym:
            yrs = epr_ym.split(',')
            for yr in yrs:
                if yr >= qt_ym:
                    return qt_ym
            return -1
        elif '-' in epr_ym:
            start_ym, end_ym = epr_ym.split('-')
            if int(start_ym) <= qt_ym and int(end_ym) >= qt_ym:
                return qt_ym
            elif  int(start_ym) > qt_ym:
                return start_ym
            elif  int(end_ym) < qt_ym:
                return -1
        elif '/' in epr_ym:
            start_ym, incre = epr_ym.split("/")
            if start_ym > qt_ym:
                return -1
            else:
                return start_ym+incre*(qt_ym-start_ym)/incre  # FIXME round up

    
    def get_next_date(self, yr_of_next, month_of_next):
        DOM = self._expression_parts[3]
        DOW = self._expression_parts[5]
        epr_month = self._expression_parts[4]
        next_date = -1
        firstd_of_month, lastd_of_month = calendar.monthrange(yr_of_next, month_of_next)
        if DOW == '*' and DOM != '*':
            # Using DOM ,-*?/ W L
            #firstd_of_month, lastd_of_month = calendar.monthrange(yr_of_next, month_of_next)
            if 'L' in DOM:
                next_date = lastd_of_month
            elif 'W' in DOM:
                epr_date = DOM.removesuffix('W')
                next_date = self.get_nearest_weekday(yr_of_next, month_of_next, epr_date,firstd_of_month, lastd_of_month)
            else:
                next_date = self.get_next_year_or_month(DOM,self._qt.day)     
                 
        elif DOM == '*' and DOW != '*':
            # Using DOW ,-*?/LC#
            if '#' in DOW:
                #FIXME: havent dvelop yet
                weekday,number = DOW.split('#')
                if self._qt.weekday != weekday:
                    next_date = -1
                earliest_date = max((number -1)*7,1)
                #Get the earliest date possible for the weekday
                #e.g. the second Tuesday possible for any month would be the 8th
                while calendar.weekday(yr_of_next,month_of_next,earliest_date) != weekday:
                    earliest_date += 1
                next_date = earliest_date

                #monthcal = calendar.monthdatescalendar(yr_of_next,month_of_next)
            elif 'L' in DOW:
                weekday = DOW.removesuffix('L')
                next_date = lastd_of_month
                while calendar.weekday(yr_of_next,month_of_next,next_date) != weekday:
                    next_date-=1
            else:
                
                next_weekday = self.get_next_year_or_month(DOW,calendar.weekday(yr_of_next,month_of_next,self._qt.day))
                print(next_weekday)
                print(calendar.weekday(yr_of_next,month_of_next,self._qt.day))
                if int(next_weekday)-1 == calendar.weekday(yr_of_next,month_of_next,self._qt.day):
                    next_date = self._qt.day
        else:
            next_date = self._qt.day
        return next_date
                
