import datetime


class User:
    def __init__(self, user_id, days_allowed, day):
        self.days_allowed = days_allowed
        self.user_id = user_id
        self.day = datetime.date.today() if day is None else day
        self.intervals = []

    def add_interval(self, interval):
        self.intervals.append(interval)

    def remove_interval(self, remove_id):
        self.intervals[:] = [interval for interval in self.intervals if interval.id != remove_id]

    def get_intervals(self):
        return self.intervals
