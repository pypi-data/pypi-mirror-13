#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import csv
from serializers import Conference
from datetime import datetime
import re
import urllib

__author__ = 'lorenamesa'

LANYARD_URL = 'http://lanyrd.com'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

def main(args):

    calls_q = "+".join(word for word in args.get('calls'))

    response = requests.get(LANYARD_URL + '/calls/?q={0}'.format(calls_q))
    soup = BeautifulSoup(response.content)

    cfps = soup.find_all('li', class_='call-item call-list-open')

    conferences = {}

    for cfp in cfps:
        links = cfp.find_all('a')
        call_closes_indx = cfp.get_text().find('Call closes on')
        call_closes = cfp.get_text()[call_closes_indx:]
        data = {'name': links[1].get_text().encode('utf-8'),
                'url': cfp.find_all('a')[1].attrs.get('href'),
                'cfp': True,
                'cfp_url': cfp.find_all('a')[0].attrs.get('href'),
                'cfp_deadline': call_closes,
                'location': cfp.find_all('a')[2].get_text() + ' ' + cfp.find_all('a')[3].get_text()}


        conferences[links[1].get_text()] = Conference(**data)

    topics_q = "+".join(word for word in args.get('topics'))

    response = requests.get(LANYARD_URL + '/topics/{0}/'.format(topics_q))
    soup = BeautifulSoup(response.content)

    upcoming_conf = soup.find_all('a', class_='summary url')

    for conf in upcoming_conf:
        data = {'name': conf.get_text().encode('utf-8'),
                'url': LANYARD_URL + conf.attrs.get('href'),
                'cfp': False}
        if data.get('name') not in conferences.keys():
            conferences[data.get('name')] = Conference(**data)

    for conf_name, conference in conferences.iteritems():
        lanyard_url = conference.url
        response = requests.get(lanyard_url)
        soup = BeautifulSoup(response.content)
        conf_url = soup.find('a', class_='icon url website')
        conference.url = conf_url.attrs.get('href')

        if soup.find('p', class_='date main-date date-range-day'):
            datestr = soup.find('p', class_='date main-date date-range-day').contents[1].attrs.get('title')
        else:
            datestr = soup.find('abbr', class_='dtstart').attrs.get('title')

        try:
            datestr = datetime.strptime(datestr, "%B %d, %Y")
        except ValueError as e:
            datestr = datetime.strptime(datestr, "%b. %d, %Y")

        conference.date = datestr

        if not conference.location:
            location = soup.find('p', class_='prominent-place').get_text()
            cleaned_location = re.sub(r'\s+', ' ', location)
            conference.location = cleaned_location

    sorted_conferences = sorted(conferences.values(), key=lambda c: c.date)

    for conf in sorted_conferences:
        conf.date = conf.date.strftime("%m/%d/%y")

    with open('{0}/data/conferences.csv'.format(ROOT_DIR), 'w') as list_conferences:
        headers = 'date,name,location,url,cfp,cfp_url,cfp_deadline,fa,fa_url,fa_deadline'.split(',')

        writer = csv.DictWriter(list_conferences, fieldnames=headers)
        writer.writeheader()

        for conf in sorted_conferences:
            writer.writerow(conf.__dict__)

if __name__ == "__main__":

    main()
