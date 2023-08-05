"""Filters module.

This file contains all the usefull filters to apply on calendars.

"""

import sys


from icalretriever import calutils


class Filter(object):

    """An abstract filter."""

    def filter(self, cal):
        """Execute the filter.
        Args:
            cal: the calendar to filter

        Returns:
            (filtered calendar, number of skipped events)
        """
        raise NotImplementedError


class RemoveDays(Filter):

    """A filter that remove entire days of the week from calendar."""

    name = 'remove_days'

    def __init__(self, days_ignored):
        """Constructor.

        Args:
            days_ignored: list of days to ignore (0 is monday)

        """
        self.ignore = days_ignored

    def filter(self, cal):
        newcal = calutils.create()
        skipped = 0

        for elem in filter(lambda x: x.name == 'VEVENT', cal.walk()):
            date = elem.get('dtstart').dt

            if self.ignore is None or date.weekday() not in self.ignore:
                newcal.add_component(elem)
            else:
                skipped += 1

        return newcal, skipped


class RemoveNamedEvent(Filter):

    """A filter that remove events based on their name."""

    name = 'remove_name'

    def __init__(self, names_ignored):
        """Constructor.

        Args:
            days_ignored: list of days to ignore (0 is monday)

        """
        self.ignore = names_ignored

    def filter(self, cal):
        newcal = calutils.create()
        skipped = 0

        for elem in filter(lambda x: x.name == 'VEVENT', cal.walk()):
            summary = elem.get('summary')

            if summary not in self.ignore:
                newcal.add_component(elem)
            else:
                skipped += 1

        return newcal, skipped
