import pandas
import datetime
from dateutil import parser


def coerce_date(candidate, dayfirst=True):
    """Coerce the candidate into a datetime.date if possible using the
    methods employed by pandas

    Parameters
    ----------
    candidate: str, datetime.date, pandas.Timestamp
        The candidate to be coerced into a datetime.date
    dayfirst: bool
        If the candidate is a str then assume European style date format if
        True or American if False
    Returns
    -------
    datetime.date
    """
    if candidate is None:
        date = None
    elif isinstance(candidate, pandas.Timestamp):
        date = candidate.date()
    elif isinstance(candidate, datetime.date):
        date = candidate
    else:
        try:
            if isinstance(candidate, str):
                date = parser.parse(candidate, dayfirst=dayfirst).date()
            else:
                date = pandas.Timestamp(candidate).date()
        except ValueError:
            raise ValueError(
                'Could not coerce date from candidate %s' % candidate)
    return date