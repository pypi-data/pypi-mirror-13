#!/usr/bin/env python

import uuid
from setuptools import setup
import os
from pip.req import parse_requirements

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
reqs_file = os.path.join(BASE_DIR, 'requirements.txt')
install_reqs = parse_requirements(reqs_file, session=uuid.uuid1())

setup(
    name="pyladies-digest",
    version="0.31",
    author="Lorena Mesa",
    author_email="me@lorenamesa.com",
    description=("Command line tool to create a MailChimp template for PyLadies chapters"),
    license="MIT",
    keywords="pyladies email digest mailchimp",
    install_requires=["argparse", "requests", "pyyaml", "jinja2", "datetime", "beautifulsoup4"],
    url="https://github.com/lorenanicole/chicago-pyladies-digest",
    packages=['digest', 'data', 'templates'],
    include_package_data=True,
    package_data={'templates': ['*'], 'data': ['*']},
    long_description=read('README.md'),
    scripts=[
        'bin/pyladies-digest',
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7"
    ],
)