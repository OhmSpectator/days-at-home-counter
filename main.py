from hashlib import md5
import datetime

from flask import Flask, request, escape, render_template

days_allowed_for_window_year = 182

app = Flask(__name__, template_folder='templates')

head = """
<head>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">
  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-LtrjvnR4Twt/qOuYxE721u19sVFLVSA4hf/rRt6PrZTmiPltdZcI7q7PXQBYTKyf" crossorigin="anonymous"></script>
</head>
"""

@app.route("/days-at-home")
def index():
    day = escape(request.args.get('day', str(datetime.date.today())))
    interval_start_p = escape(request.args.get('interval-start', ''))
    interval_end_p = escape(request.args.get('interval-end', ''))
    interval_start = None
    interval_end = None
    remove = escape(request.args.get('remove', None))
    at_home[:] = [interval for interval in at_home if interval.id != remove]
    try:
        interval_start = datetime.date.fromisoformat(interval_start_p)
        interval_end = datetime.date.fromisoformat(interval_end_p)
    except ValueError:
        pass
    output = head
    output += render_template('calendar_form.html', day=day)
    output += count_days(day)
    if not interval_start or not interval_end:
        return output
    if interval_start > interval_end:
        return output
    for interval in at_home:
        if interval_start in interval:
            return output
        if interval_end in interval:
            return output
    interval_to_add = DateInterval(interval_start, interval_end)
    if interval_to_add not in at_home:
        at_home.append(DateInterval(interval_start, interval_end))
        output = head
        output += render_template('calendar_form.html', day=day)
        output += count_days(day)
    return output


def count_days(day):
    today = datetime.date.today()
    if day:
        try:
            today = datetime.date.fromisoformat(day)
        except ValueError:
            pass

    # get the Jinja2 template
    template = render_template('intervals_list.html', at_home=at_home, today=today)

    # render the template with the specified data
    out = template
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
        if start_date > end_date:
            raise ValueError
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

    def intersect(self, other):
        result_start = max(self.start_date, other.start_date)
        result_end = min(self.end_date, other.end_date)
        if result_start > result_end:
            return None
        return DateInterval(result_start, result_end)


at_home = []


def count_totals(day):
    year_ago = day - datetime.timedelta(365)
    year_interval = DateInterval(year_ago, day)
    total_duration_window_year = 0
    for interval in at_home:
        intersection = year_interval.intersect(interval)
        if intersection is not None:
            total_duration_window_year += intersection.duration
    debug_out = "Total days at home (by %s):</p>" % day
    debug_out += "  for the last 12 months: %d (still in the swap: %d)" % (
        total_duration_window_year,
        days_allowed_for_window_year - total_duration_window_year)
    return debug_out


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8082, debug=True)
