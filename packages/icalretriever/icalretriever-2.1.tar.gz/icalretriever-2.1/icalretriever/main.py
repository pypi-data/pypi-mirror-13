import sys
import argparse
import yaml

from icalretriever.parse import retrieve_filter_write
from icalretriever import filters


def main():
    parser = argparse.ArgumentParser(description='Retrieve ICal files.')

    parser.add_argument('config', help="YAML configuration file")

    args = parser.parse_args()
    config = args.config

    data = yaml.load(open(config, 'r'))

    for cal in data['calendars']:
        filtered_days = []
        filtered_names = []

        if 'filters' in cal:
            for filt in cal['filters']:
                if filt['name'] == filters.RemoveDays.name:
                    [filtered_days.append(x) for x in filt['args']]
                elif filt['name'] == filters.RemoveNamedEvent.name:
                    [filtered_names.append(x) for x in filt['args']]


        myFilters = []
        myFilters.append(filters.RemoveDays(filtered_days))
        myFilters.append(filters.RemoveNamedEvent(filtered_names))

        retrieve_filter_write(cal['url'], myFilters, cal['file'])
