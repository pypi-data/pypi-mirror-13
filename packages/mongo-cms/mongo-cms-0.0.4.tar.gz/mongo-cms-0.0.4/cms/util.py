#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import hashlib, datetime, sys, tempfile, os
from subprocess import call

def hash_string(s):
    return hashlib.sha1(s.encode("UTF-8")).hexdigest()[:10]

def hash_file(path):
    # http://pythoncentral.io/hashing-files-with-python
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

DATE_FMT = '%Y-%m-%d %H:%M:%S'

def parse_date(date):
    if isinstance(date, str):
        return datetime.datetime.strptime(string, DATE_FMT)
    elif isinstance(date, datetime.datetime):
        return date

def serialize_date(date):
    if not isinstance(date, datetime.datetime):
        raise TypeError(date)
    return date.strftime(DATE_FMT)

def deserialize_date(date):
    if not isinstance(date, str):
        raise TypeError(date)
    return datetime.datetime.strptime(date, DATE_FMT)

def now():
    return datetime.datetime.now()

def parse_tags(lst):
    if not isinstance(lst, list): raise ValueError(lst)
    return [ str(x) for x in lst ]

def multiline_input(style):
    EDITOR = os.environ.get('EDITOR','vim') #that easy!

    initial_message = "" # if you want to set up the file somehow
    content = ""

    suffix = '.md' if style.startswith('m') else '.html'

    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(initial_message.encode())
        tmp.flush()
        call([EDITOR, tmp.name])
        content = tmp.read().decode()

    return content

def editor_input(extension):
    EDITOR = os.environ.get('EDITOR','vim') #that easy!

    content = ""

    with tempfile.NamedTemporaryFile(suffix=extension) as tmp:
        call([EDITOR, tmp.name])
        content = tmp.read().decode()

    return content.strip()

def date_range(date):
    if not date: return None, None

    start_of_day = datetime.datetime(year=date.year, month=date.month, day=date.day,
            hour=0, minute=0, second=0, microsecond=1)
    end_of_day = datetime.datetime(year=date.year, month=date.month, day=date.day,
            hour=23, minute=59, second=59, microsecond=999)

    return start_of_day, end_of_day

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
