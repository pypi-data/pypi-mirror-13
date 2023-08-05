import pandas
import datetime
from dateutil.relativedelta import relativedelta


def utc_now():
    """Returns the pandas.Timestamp for now with tz='UTC'

    Returns
    -------
    pandas.Timestamp
    """
    return utc_timestamp(datetime.datetime.now())


def utc_now_str():
    """The str format of the pandas.Timestamp for now with tz='UTC'

    Returns
    -------
    str
    """
    return utc_timestamp_str(datetime.datetime.now())


def utc_timestamp(timestamp):
    """Convert the timestamp to a pandas.Timestamp with tz='UTC'

    timestamp: datetime.datetime, str
        The datetime.date, or date string  to convert to a pandas.Timestamp

    Returns
    -------
    pandas.Timestamp

    Examples
    --------
    >>> utc_timestamp(datetime.datetime(2014, 4, 3, 12, 0))
    Timestamp('2014-04-03 12:00:00+0000', tz='UTC')
    """
    return pandas.Timestamp(timestamp, tz='UTC')


def utc_now_value():
    """Returns the value of the pandas.Timestamp for datetime.datetime.now()

    Returns
    -------
    int
    """
    return utc_now().value


def utc_timestamp_str(timestamp):
    """Returns the str format for the datetime.datetime.now() down to the
    second

    Parameters
    ----------
    timestamp: str, datetime.datetime
        The timestamp to convert to a str format

    Returns
    -------
    str
    """
    return utc_timestamp(timestamp).strftime('%d-%b-%y %H:%M:%S')


def timestamp_minute(timestamp):
    """Converts the timestamp to the top of the minute before, left side
    labelling

    Parameters
    ----------
    timestamp: pandas.Timestamp
        The candidate to convert to a pandas.Timestamp

    Returns
    -------
    pandas.Timestamp

    Examples
    --------
    >>> timestamp_minute(pandas.Timestamp('3-Apr-14 12:36:14'))
    Timestamp('2014-04-03 12:36:00')
    """
    return timestamp + relativedelta(second=0, microsecond=0)


def get_pnl_zero(timestamp):
    """Returns the last pandas.Timestamp with time 06:05 before timestamp

    Parameters
    ----------
    timestamp: datetime.datetime, pandas.Timestamp
        The timestamp to use as a basis for finding the pnl cutover before

    Returns
    -------
    datetime.datetime, pandas.Timestamp

    Examples
    --------
    >>> get_pnl_zero(datetime.datetime(2014, 4, 3, 12, 00))
    datetime.datetime(2014, 4, 3, 6, 5)
    >>> get_pnl_zero(pandas.Timestamp('3-Apr-14 12:00'))
    Timestamp('2014-04-03 06:05:00')
    """
    days = -1 if timestamp.time() < datetime.time(6, 5) else 0
    return timestamp + relativedelta(days=days, hour=6, minute=5, second=0, microsecond=0)


def get_pnl_zero_now():
    """Returns a pandas.Timestamp with tz='UTC' at the last 06:05 before the
    current datetime

    Returns
    -------
    pandas.Timestamp
    """
    timestamp = utc_now()
    return get_pnl_zero(timestamp)


def coerce_time(candidate):
    """Coerce the candidate into a datetime.time if possible using the
    methods applied by pandas.Timestamp

    Parameters
    ----------
    candidate: str, datetime, pandas.Timestamp
        The candidate to coerce into a datetime.time

    Returns
    -------
    datetime.time
    """
    if candidate is None:
        time = None
    elif isinstance(candidate, datetime.time):
        time = candidate
    else:
        try:
            time = pandas.Timestamp(candidate).time()
        except ValueError:
            raise ValueError(
                'Could not coerce time from candidate %s' % candidate)
    return time


def minutes_in_freq(freq):
    """Returns the number of minutes in the frequency freq

    Parameters
    ----------
    freq: str, pandas.tseries.offsets.Tick
        The frequency to convert into minutes

    Returns
    -------
    float

    Examples
    --------
    >>> minutes_in_freq('D')
    1440.0
    >>> minutes_in_freq(pandas.tseries.frequencies.to_offset('D'))
    1440.0
    >>> minutes_in_freq('30S')
    0.5000000000000001
    >>> minutes_in_freq(pandas.tseries.frequencies.to_offset('30S'))
    0.5000000000000001
    """
    freqs = dict(D=1440, H=60, T=1)
    result = freqs.get(
        freq, pandas.tseries.frequencies.to_offset(freq).nanos * 1e-9 / 60.)
    result = float(result)
    return result