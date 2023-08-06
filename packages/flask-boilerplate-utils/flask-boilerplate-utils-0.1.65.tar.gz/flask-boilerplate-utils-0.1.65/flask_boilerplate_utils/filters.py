from datetime import datetime

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

def timesince(dt, default="Just now."):
    """
    Returns a string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    now = datetime.now()
    diff = now - dt
    
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        period = round(period)
        if period >= 1:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default

def local_date(datestamp):
    """
    Returns a babel formatted local date
    """
    from flask.ext.babel import format_date

    if datestamp:
        return format_date(datestamp)

def percent_escape(string):
    """
    Returns an escaped string using percentage symbols
    Used for URL encodes
    """
    return quote(string, '')

def local_date_time(datestamp):
    """
    Returns a babel formatted local date and time
    """
    from flask.ext.babel import format_datetime

    if datestamp:
        return format_datetime(datestamp)

