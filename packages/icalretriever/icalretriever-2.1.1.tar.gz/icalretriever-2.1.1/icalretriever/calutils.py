"""Calendar utilities module.

This module contains all utilities used to interract with the icalendar module.

"""

import sys

from dateutil import tz
from urllib.request import urlopen

from icalendar.cal import Calendar


# Consts for generated calendars
PRODID = 'MicroJoe ICalRetriever'
CALVERSION = '2.0'


def download(url):
    """Download an ICal file using HTTP and return it.

    Args:
        url: HTTP url of the file to download

    Returns:
        The retrieved calendar

    """
    return Calendar.from_ical(urlopen(url).read())


def create():
    """Create a new calendar and return it.

    Returns:
        A fresh empty calendar

    """
    newcal = Calendar()
    newcal.add('prodid', '-//{}//'.format(PRODID))
    newcal.add('version', CALVERSION)
    return newcal


def display(cal, file=sys.stderr):
    """Display events of a calendar, sorted by date.

    Args:
        cal: calendar to display

    """
    events = {}

    # Populate events
    for elem in filter(lambda x: x.name == 'VEVENT', cal.walk()):
        if elem.name == 'VEVENT':
            date = elem.get('dtstart').dt.astimezone(tz.tzlocal())
            name = elem.get('summary')
            events[date] = name

    # Display ordered elements
    for key in sorted(events):
        print("{} -> {}".format(key, events[key]),
              file=file)


def write(cal, file=None):
    """Write a calendar to an ICS file.

    Args:
        cal: calendar to write to the file
        file: file to write the calendar in

    """
    file.write(cal.to_ical().decode('utf-8'))

def get_events(cal):
    return filter(lambda x: x.name == 'VEVENT', cal.walk())

