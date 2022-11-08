import datetime
from hashlib import md5

from flask import Flask
from flask import request

days_allowed_for_window_year = 182

app = Flask(__name__)

calendar_form = """
<form action="" method="get">
  <input type="date" name="day" value="{day}">
  <input type="submit" value="submit">
</form>
<form action="" method="get">
  <input type="date" name="interval-start" value="">
  <input type="date" name="interval-end" value="">
  <input type="submit" value="submit">
</form>
"""


@app.route("/days-at-home")
def index():
    day = request.args.get('day', str(datetime.date.today()))
    interval_start_p = request.args.get('interval-start', '')
    interval_end_p = request.args.get('interval-end', '')
    interval_start = None
    interval_end = None
    remove = request.args.get('remove', None)
    try:
        for interval in at_home:
            if interval.id == remove:
                at_home.remove(interval)
    except ValueError:
        pass
    try:
        interval_start = datetime.date.fromisoformat(interval_start_p)
        interval_end = datetime.date.fromisoformat(interval_end_p)
    except ValueError:
        pass
    if interval_start and interval_end and \
       interval_start < interval_end and \
       DateInterval(interval_start, interval_end) not in at_home:
        at_home.append(DateInterval(interval_start, interval_end))
    days_out = count_days(day)
    return calendar_form.format(day=day) + days_out


def count_days(day):
    today = datetime.date.today()
    out = "Was at home:"
    out += "<ul>"
    for interval in at_home:
        out += '<li>'
        out += str(interval)
        out += """
        <form method="get">
        <button type="submit" value="{id}" name="remove">Remove</button>
        </form>""".format(id=interval.id)
        out += '</li>'
    out += '</ul>'
    if day:
        try:
            today = datetime.date.fromisoformat(day)
        except ValueError:
            pass
    out += count_totals(today)
    return out


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
        hash_id = md5(self.start_date.isoformat().encode())
        hash_id.update(self.end_date.isoformat().encode())
        self.id = hash_id.hexdigest()

    def __lt__(self, other):
        return self.start_date < other.start_date

    def __eq__(self, other):
        return self.start_date == other.start_date and \
               self.end_date == self.end_date

    def __str__(self):
        return "from {} until {} ({} in total)".format(self.start_date,
                                                       self.end_date,
                                                       self.duration)

    def __contains__(self, date):
        return self.start_date <= date <= self.end_date


at_home = []


def count_totals(day):
    year_ago = day - datetime.timedelta(365)
    total_duration_window_year = 0
    for interval in at_home:
        if year_ago < interval.start_date:
            total_duration_window_year += interval.duration
        if year_ago in interval:
            partial_interval = DateInterval(year_ago, interval.end_date)
            total_duration_window_year += partial_interval.duration
    debug_out = "Total days at home (by %s):</p>" % day
    debug_out += "  for the last 12 months: %d (still in the swap: %d)" % (
        total_duration_window_year,
        days_allowed_for_window_year - total_duration_window_year)
    return debug_out


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
