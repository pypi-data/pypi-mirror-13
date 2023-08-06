#!/usr/bin/env python

import json
import requests
import yaml
from datetime import datetime, timedelta
import csv
import os

BASE_URL = 'https://api.meetup.com/'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

def date_within_num_days(utc_offset, utctimestamp, days=30):
    utctimestamp = (int(utctimestamp) + int(utc_offset)) / 1000.0
    margin = timedelta(days=days)
    return datetime.fromtimestamp(utctimestamp) - datetime.now() <= margin

def utc_timestamp_to_datetime(utc_offset, utctimestamp):
    utctimestamp = (int(utctimestamp) + int(utc_offset)) / 1000.0
    return datetime.fromtimestamp(utctimestamp)

def main(args):

    if not args.get('m_key'):

        with open("{0}/config.yml".format(BASE_DIR), 'r') as stream:
            doc = yaml.load(stream)

        MEETUP_KEY = doc['meetup_key']

    else:

        MEETUP_KEY = args.get('m_key')


    upcoming_events = BASE_URL + 'find/groups?category={0}&location={1}&key={2}' \
                                 '&text={3}&upcoming_events=true'.format(args.get('category'),
                                                                         args.get('location'),
                                                                         MEETUP_KEY,
                                                                         args.get('text'))

    response = requests.get(upcoming_events)
    data = json.loads(response.content)

    events = {}
    for d in data:
        if 'python' in d.get('description').lower() and d.get('next_event'):
            next_event = d.get('next_event')
            if date_within_num_days(next_event.get('utc_offset'), next_event.get('time')):
                date = utc_timestamp_to_datetime(next_event.get('utc_offset'), next_event.get('time'))
                events[d.get('name')] = {'id': next_event.get('id'),
                                         'date': date,
                                         'name': next_event.get('name')}

    event_ids = [event_data.get('id') for event, event_data in events.iteritems()]

    upcoming_events = BASE_URL + '2/events?key={0}&event_id={1}'.format(MEETUP_KEY, ','.join(event_ids))

    response = requests.get(upcoming_events)

    if response.status_code == 200:

        data = json.loads(response.content).get('results')

        for d in data:
            group_name = d.get('group').get('name')
            if events.get(group_name):
                events[group_name]['event_url'] = d.get('event_url')
                events[group_name]['group'] = d.get('group').get('name')
                events[group_name].pop('id')

        sorted_events = sorted(events.values(), key=lambda e: e.get('date'))
        for event in sorted_events:
            event['date'] = event.get('date').strftime("%m/%d/%y")

        with open('{0}/data/events.csv'.format(ROOT_DIR), 'w') as python_events:
            headers = sorted_events[0].keys()

            writer = csv.DictWriter(python_events, fieldnames=headers)
            writer.writeheader()

            for event in sorted_events:
                writer.writerow(event)

    else:

        print "MeetUp returned with response code: ", response.content
        raise SystemExit

if __name__ == "__main__":

    main()




