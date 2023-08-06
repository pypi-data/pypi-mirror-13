from pytz import timezone, utc
from datetime import datetime, timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar
import pandas as pd

class EasyDate():

    ######################################################
    # setup and manipulate reference date local and utc
    ######################################################

    # initialise to current UTC time
    def __init__(self,
                 date_time='now', # 'now', datetime object or string 'YYYY-MM-DD HH:MM:SS'
                 local=True, # is the date_time input in your local timezone?
                 local_timezone='Australia/Brisbane' # pytz timezone
                 ):

        self.init_time = datetime.utcnow().replace(tzinfo=utc)
        self.time_object_utc = self.init_time
        self.time_object_local = self.init_time
        self.set_reference_point(date_time=date_time, local=local, local_timezone=local_timezone)
        self.range_start = None
        self.range_end = None
        self.sequence_range_start = None
        self.sequence_range_end = None

    def __str__(self):
        utc_output = self.time_object_utc.strftime('%Y-%m-%d %H:%M:%S')
        local_output = self.time_object_local.strftime('%Y-%m-%d %H:%M:%S')
        return "EasyDate object: {local_time} local time, {utc_time} utc".format(local_time=local_output, utc_time=utc_output)

    # set up objects
    def set_reference_point(self,
                            date_time='now', # 'now', datetime object or string 'YYYY-MM-DD HH:MM:SS'
                            local=True, # is the date_time input in your local timezone?
                            local_timezone='Australia/Brisbane' # pytz timezone
                            ):

        # if current time is requested, get this as utc
        if date_time == 'now':
            date_time = datetime.utcnow().replace(tzinfo=utc)
            local = False

        date_time = self.parse_datetime_input(date_time)
        date_time = self.parse_input_timezone(date_time, local=local, local_timezone=local_timezone)
        self.time_object_utc = date_time[0]
        self.time_object_local = date_time[1]


    # move reference backward or forward in time in increments
    def move_reference_point(self,
                             period="day", # unit to move time by: minutes, hours, days, weeks, fortnights, months, quarters or years
                             n_periods=1, # the number of units to move by
                             local=True, # move from the local or utc reference?
                             return_string=False # return string
                             ):

        # move time point
        if period == "minute":
            self.time_object_utc = self.time_object_utc + relativedelta(minutes=n_periods)
        elif period == "hour":
            self.time_object_utc = self.time_object_utc + relativedelta(hours=n_periods)
        elif period == "day":
            self.time_object_utc = self.time_object_utc + relativedelta(days=n_periods)
        elif period == "week":
            self.time_object_utc = self.time_object_utc + relativedelta(weeks=n_periods)
        elif period == "fortnight":
            self.time_object_utc = self.time_object_utc + relativedelta(weeks=(2 * n_periods))
        elif period == "month":
            self.time_object_utc = self.time_object_utc + relativedelta(months=n_periods)
        elif period == "quarter":
            self.time_object_utc = self.time_object_utc + relativedelta(months=(4 * n_periods))
        elif period == "year":
            self.time_object_utc = self.time_object_utc + relativedelta(years=n_periods)
        else:
            print "you have entered and invalid time period"
            return None

        # update local time object
        self.time_object_local = self.time_object_utc.astimezone(self.local_timezone)

        if return_string:
            return self.time_object_utc.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None

    # get start and end time for a time range up to the reference point
    def get_range(self,
                  # date_time='current', # date_time to get range for, default to self.time_object_local
                  period='day', # unit to get the range for: minutes, hours, days, weeks, fortnights, months, quarters or years
                  n_periods=1, # the number of units to cover
                  return_string=True, # return strings or objects
                  local=True # for local timezone or utc
                  ):

        # get reference date
        date_time = self.time_object_local if local is True else self.time_object_utc

        # end time of reference point
        if period == "month":
            range_end_day = calendar.monthrange(date_time.year, date_time.month)[1]
        else:
            range_end_day = date_time.day

        range_end = datetime(date_time.year, date_time.month, range_end_day) \
                + relativedelta(days=1) \
                - relativedelta(microseconds=1)

        # adjustment to account for months with < 31 days
        # if range_end.month == 2:
        #     adjustment = relativedelta(days=3)
        # elif range_end.day == 30:
        #     adjustment = relativedelta(days=1)
        # else:
        #     adjustment = relativedelta(days=0)

        # start time of range
        if period == "day":
            range_start = range_end - relativedelta(days=n_periods)
        elif period == "week":
            range_start = range_end - relativedelta(weeks=n_periods)
        elif period == "fortnight":
            range_start = range_end - relativedelta(weeks=(2 * n_periods))
        elif period == "month":
            n_periods -= 1
            range_start_month = (range_end - relativedelta(months=n_periods)).month
            range_start_year = (range_end - relativedelta(months=n_periods)).year
            range_start = datetime(range_start_year, range_start_month, 1)
        elif period == "quarter":
            n_periods -= 1
            range_start_month = (range_end - relativedelta(months=(3*n_periods))).month
            range_start_year = (range_end - relativedelta(months=(3*n_periods))).year
            range_start = datetime(range_start_year, range_start_month, 1)
        elif period == "year":
            range_start = range_end - relativedelta(years=n_periods)
        else:
            print "you entered an invalid time period"
            return None

        # adjust start
        range_start = range_start + relativedelta(microseconds=1)

        # save internally
        self.range_start = range_start
        self.range_end = range_end

        # return object or string result
        if return_string is True:
            return (range_start.strftime('%Y-%m-%d %H:%M:%S'), range_end.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            return (range_start, range_end)

    # move reference to next week, month or quarter end
    def move_reference_to_next(self,
                               next_time='friday', # One of any weekday name, month, quarter, half or year
                               local=True
                               ):

        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        # utc or local
        date_time = self.time_object_local if local is True else self.time_object_utc

        # get end of current day
        day_end = self.get_range(period='day', local=local)[1]

        # reset reference point to end of current day (to set end of day time)
        self.set_reference_point(date_time=day_end, local=local)

        # move reference to targets
        if next_time == 'month':

            # calculate difference in days to end of month
            current_day = date_time.day
            month_end_day = calendar.monthrange(date_time.year, date_time.month)[1]
            move = month_end_day - current_day

            # move reference time to end of month
            self.move_reference_point(period='day', n_periods=move, local=local)

        elif next_time in weekdays:

            # calculate difference in days to next friday
            move = self.days_to_day_number(target_day=next_time, current_date_time=date_time)

            # move reference time to next friday
            self.move_reference_point(period='day', n_periods=move, local=local)

        # unfinished - add quarter, half and year
        else:
            print "You chose an invalid option for the next time to move to"

        return None

    # output strings for reference date/time
    def return_string(self, format='datetime', local=True):
        result = self.time_object_local if local is True else self.time_object_utc
        return result.strftime('%Y-%m-%d %H:%M:%S') if format == 'datetime' else result.strftime('%Y-%m-%d')


    # ######################################################
    # # derive date ranges and construct sequential reference tables
    # ######################################################

    # generate a sequence of dates (start and end) for a specified period and returns pandas data frame
    def generate_sequence(self,
                          period='month', # time frequency
                          n_periods=30, # number of rows returned
                          local=True, # for local time or utc
                          week_end='friday', # end day for week-based frequencies
                          offset=0 # how far to move the reference time from the front of the results time series
                          ):

        # store reference time
        reference = self.time_object_utc

        # apply reference offset
        self.move_reference_point(period=period, n_periods=offset, local=local)

        # for week-based frequencies move to end day
        if period in ['week', 'fortnight']:
            self.move_reference_to_next(next_time=week_end, local=True)

        # create results table
        result = pd.DataFrame(columns=['start', 'end'])

        # iterate time and add records to table
        for n in xrange(n_periods):

            # account for inconsistent number of days in months, not applicable to other periods with equal item counts
            if period == 'month':
                self.move_reference_to_next(next_time=period, local=True)

            # get the start/end of the period
            self.get_range(period=period, n_periods=1)

            # save sequence range start and end
            if n is 0:
                self.sequence_range_end = self.range_end.strftime('%Y-%m-%d %H:%M:%S')

            if n is (n_periods - 1):
                self.sequence_range_start = self.range_start.strftime('%Y-%m-%d %H:%M:%S')

            # add rows to dataframe
            result.loc[n] = [self.range_start.strftime('%Y-%m-%d %H:%M:%S'), self.range_end.strftime('%Y-%m-%d %H:%M:%S')]

            # move reference point
            self.move_reference_point(period=period, n_periods=-1, local=local)

        # restore reference time
        self.set_reference_point(date_time=reference, local=False)

        return result

    ######################################################
    # class helper functions
    ######################################################

    # check type of input and return date object
    def parse_datetime_input(self, input):

        # try to coerce to datetime object or return error
        try:
            if isinstance(input, datetime):
                return input
            else:
                return datetime(int(input[:4]),
                                int(input[5:7]),
                                int(input[8:10]),
                                int(input[11:13]),
                                int(input[14:16]),
                                int(input[17:19]))
        except ValueError:
            print "input argument to parse filter must be in form 'YYYY-MM-DD HH:MM:SS' or a datetime object"

    # returns the utc and local datetime objects for a given datetime input
    def parse_input_timezone(self, input, local=True, local_timezone='Australia/Brisbane'):

        # set local timezone
        self.local_timezone = timezone(local_timezone)

        # ! important
        # Unfortunately using the tzinfo argument of the standard datetime constructors does not work with pytz for many timezones
        # http://pytz.sourceforge.net/

        # return utc and local datetime objects
        if local is False:
            return (input.replace(tzinfo=utc), input.replace(tzinfo=utc).astimezone(self.local_timezone))
        else:
            return (self.local_timezone.localize(input).astimezone(utc), self.local_timezone.localize(input))

    # function to calculate days to a target day name (proxy by weekday number) from the current day
    def days_to_day_number(self, target_day='friday', current_date_time=datetime.now()):

        # The datetime date.weekday method represents Monday through Sunday as 0 through 6
        days_by_number = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
        target = days_by_number[target_day]
        current = current_date_time.weekday()

        # find days to next target weekday
        if target >= current:
            return target - current
        else:
            return (target + 7) - current


######################################################
# dev/test
######################################################

# ed = EasyDate()
# print ed
#
# ed.get_range(period='month')
#
# ed.move_reference_to_next(next_time='month')
# print ed
#
# ed.move_reference_point(period='month', n_periods=-1)
# print ed
# ed.get_range(period='month')
#
# ed.time_object_local - relativedelta(months=2)
#
# calendar.monthrange(ed.time_object_local.year, ed.time_object_local.month)[1]


# # time range generator for time periods
# def time_range_generator(time_period='day', n_periods=30):
#     ed = EasyDate()
#
#     # if month or week move to the next week/month end
#     if time_period == 'week':
#         ed.move_reference_to_next(next_time='friday')
#
#     # generate outputs
#     n_iter = 0
#     while n_iter < n_periods:
#         ed.move_reference_point(period=time_period, n_periods=-1)
#         yield ed.get_range(period=time_period)
#         n_iter += 1
#
#
# trg = time_range_generator(time_period='month')
# next(trg)
#
# ed = EasyDate()
# ed.move_reference_point(period='week', n_periods=1)
# ed.move_reference_to_next(next_time='friday')
# print ed


