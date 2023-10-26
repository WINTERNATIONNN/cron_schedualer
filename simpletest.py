import calendar
import datetime
import 


def get_nearest_weekday(yr_of_next, month_of_next, epr_date, firstd_of_month, lastd_of_month):
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
    return -1

if __name__ == "__main__":
    print("hi")
    print(get_nearest_weekday(2023,10,29,1,31))
    it = datetime.datetime.now()
    print(it.day)