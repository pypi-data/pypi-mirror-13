#!/usr/bin/env python3
# coding: utf-8

"""ICalRetriever, a simple ICal tool.

This program retrieve a calendar from HTTP, filter it by removing some events
of it (often weekend events) and write it down to a file.

It was designed in order to be run by cron to update the calendar over the day
and to provide it to a WebDAV server so it can be accessed by many CalDAV
compatible devices, such as computers (with Thunderbird/Lightning) and Android
devices (using DAVdroid software).

"""

import sys

from icalretriever import calutils


def retrieve_filter_write(url, filters, output):
    """Retrieve a calendar, ignore some days of it and write it to a file.

    This function will print out some informational messages.

    Args:
        url: HTTP url of the calendar
        filters: list of filters to apply
        output: filename of the output file to write

    """
    # Download ical
    print("Downloading ICal file {}...".format(url),
          file=sys.stderr)
    c = calutils.download(url)

    # Filter and display warning if skipped events
    newcal = c
    skipped_all = 0
    print("Walking into calendar and filtering...", file=sys.stderr)
    for f in filters:
        newcal, skipped = f.filter(newcal)
        skipped_all += skipped

    if skipped > 0:
        print("/!\\ {} events skipped from filters".format(skipped),
              file=sys.stderr)

    # Display filtered calendar
    print("Content of calendar file:",
          file=sys.stderr)
    calutils.display(newcal)

    # Write calendar to file
    output_name = output if output is not None else 'stdout'

    print("Writing calendar to {}...".format(output_name),
          file=sys.stderr)

    if output is not None:
        with open(output, 'w') as f:
            calutils.write(newcal, f)
    else:
        calutils.write(newcal, sys.stdout)
