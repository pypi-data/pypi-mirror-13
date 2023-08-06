#!/usr/bin/env python

import yaml
import os

__author__ = 'lorenamesa'

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

def main(meetup_key, mailchimp_key):

    data = dict(
        meetup_key=meetup_key,
        mailchimp_key=mailchimp_key
    )

    with open("{0}/config.yml".format(BASE_DIR), 'w') as outfile:
        outfile.write(yaml.dump(data, default_flow_style=False))

if __name__ == "__main__":
    main()