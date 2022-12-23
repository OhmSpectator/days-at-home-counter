import datetime
from hashlib import md5


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
        if start_date > end_date:
            raise ValueError
        self.duration = (self.end_date - self.start_date).days + 1
        hash_id = md5(self.start_date.isoformat().encode())
        hash_id.update(self.end_date.isoformat().encode())
        self.id = hash_id.hexdigest()

    def __lt__(self, other):
        return self.start_date < other.start_date

    def __eq__(self, other):
        return self.start_date == other.start_date and \
               self.end_date == self.end_date

    def __str__(self):
        return f'{self.start_date} - {self.end_date} ({self.duration} in total)'

    def __contains__(self, date):
        return self.start_date <= date <= self.end_date

    def intersect(self, other):
        result_start = max(self.start_date, other.start_date)
        result_end = min(self.end_date, other.end_date)
        if result_start > result_end:
            return None
        return DateInterval(result_start, result_end)
