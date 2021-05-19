import datetime

days_allowed_for_window_year = 182


class DateInterval(object):
    def __init__(self, start_date, end_date):
        if isinstance(start_date, str):
            self.start_date = datetime.date.fromisoformat(start_date)
        if isinstance(start_date, datetime.date):
            self.start_date = start_date
        if isinstance(end_date, str):
            self.end_date = datetime.date.fromisoformat(end_date)
        if isinstance(end_date, datetime.date):
            self.end_date = end_date
        self.duration = (self.end_date - self.start_date).days

    def __lt__(self, other):
        return self.start_date < other.start_date

    def __str__(self):
        return "from {0} until {1}".format(self.start_date, self.end_date)

    def __contains__(self, date):
        return self.start_date <= date <= self.end_date


at_home = [DateInterval('2020-08-02', '2020-09-12'),
           DateInterval('2020-12-12', '2021-04-11'),
           ]


def count_totals(day):
    year_ago = day - datetime.timedelta(365)
    total_duration_window_year = 0
    for interval in at_home:
        if year_ago < interval.start_date:
            total_duration_window_year += interval.duration
        if year_ago in interval:
            partial_interval = DateInterval(year_ago, interval.end_date)
            total_duration_window_year += partial_interval.duration
    print("Total days at home (by %s):" % day)
    print("  for the last 12 months: %d (still in the swap: %d)" %
          (total_duration_window_year, days_allowed_for_window_year - total_duration_window_year))


if __name__ == '__main__':
    today = datetime.date.today()
    count_totals(today)
