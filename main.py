from hashlib import md5
import uuid
import datetime

from flask import Flask, request, escape, render_template, make_response


app = Flask(__name__, template_folder='templates')
at_home = {}


def _verify_intervals(start, end, stored_intervals):
    if not start or not end:
        return False
    if start > end:
        return False
    for interval in stored_intervals:
        if start in interval:
            return False
        if end in interval:
            return False
        if start < interval.start_date and end > interval.end_date:
            return False
    return True


@app.route("/days-at-home", methods=['GET', 'POST'])
def index():
    user_id = request.args.get('uuid')
    if user_id is None:
        user_id = request.cookies.get('uuid')
    if user_id is None:
        user_id = str(uuid.uuid4())
    user_id = escape(user_id)
    response = make_response()
    response.set_cookie('uuid', user_id)
    days_allowed_str = request.form.get('days_allowed', None)
    try:
        days_allowed = int(escape(days_allowed_str)) if days_allowed_str else None
    except ValueError:
        days_allowed = None
    day = request.form.get('day', None)
    if day is not None:
        try:
            day = datetime.date.fromisoformat(escape(day))
        except ValueError:
            day = datetime.date.today()
    if at_home.get(user_id) is None:
        at_home[user_id] = User(user_id, 182, day)
    if days_allowed:
        at_home[user_id].days_allowed = days_allowed
    if day is not None:
        at_home[user_id].day = day
    else:
        day = at_home[user_id].day
    remove_id_str = request.form.get('remove', None)
    remove_id = escape(remove_id_str) if remove_id_str else None
    if remove_id is not None:
        at_home[user_id].remove_interval(remove_id)
    interval_start_p = escape(request.form.get('interval-start', ''))
    interval_end_p = escape(request.form.get('interval-end', ''))
    interval_start = None
    interval_end = None
    try:
        interval_start = datetime.date.fromisoformat(interval_start_p)
        interval_end = datetime.date.fromisoformat(interval_end_p)
    except ValueError:
        pass
    response.response = create_page(user_id, day, at_home[user_id].days_allowed)
    if not _verify_intervals(interval_start, interval_end, at_home[user_id].get_intervals()):
        return response
    interval_to_add = DateInterval(interval_start, interval_end)
    if interval_to_add not in at_home[user_id].get_intervals():
        at_home[user_id].add_interval(DateInterval(interval_start, interval_end))
        response.response = create_page(user_id, day, at_home[user_id].days_allowed)
    return response


def create_page(user_id, day, days_allowed):
    total_days = count_totals(user_id, day)
    intervals = at_home[user_id].get_intervals()
    return render_template('index.html', uuid=user_id, day=day, days_allowed=days_allowed,
                           intervals=intervals,
                           total_duration=total_days)


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



class User(object):
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



def count_totals(user_id, day):
    year_ago = day - datetime.timedelta(365)
    year_interval = DateInterval(year_ago, day)
    total_duration_window_year = 0
    for interval in at_home[user_id].get_intervals():
        intersection = year_interval.intersect(interval)
        if intersection is not None:
            total_duration_window_year += intersection.duration
    return total_duration_window_year


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
