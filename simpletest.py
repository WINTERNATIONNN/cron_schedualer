import calendar
import datetime



def get_time_list(epr,min_stamp,max_stamp):
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
            print(time)
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
        
if __name__ == "__main__":
    #print("hi")
    print(get_time_list("*",0,59))
