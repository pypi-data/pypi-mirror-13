#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import datetime, logging

from cms.model import Post, Image, Snippet
from cms.db.mongodb import MongoDB, Query

import cms.util as util

logger = logging.getLogger(__name__)

# TODO abstract duplicate lines

class CMS(object):
    def __init__(self, mongos, database):
        self.__db = MongoDB(mongos, database)

    def get_image(self, identifier):
        if isinstance(sha1, int):
            return self.__db.find_image({'number': identifier})
        else:
            return self.__db.find_image({'sha1': identifier})

    def get_images(self, start_date=datetime.datetime.now() - datetime.timedelta(days=1),
                         stop_date=datetime.datetime.now(),
                         tags=[],
                         sha1s=[]):
        q = Query()

        if start_date is not None: q += { 'date': {'$gt': start_date} }
        if stop_date is not None: q += { 'date': {'$lt': stop_date} }
        if len(tags) > 0: q += {'$or': [ { 'tags.name': t } for t in tags ]}
        if len(sha1s) > 0: q += {'$or': [ { 'sha1': h } for h in sha1s ]}

        return self.__db.find_images(q.query())

    def get_post(self, number):
        return self.__db.find_post({'number': number})

    def get_posts(self, start_date=datetime.datetime.now() - datetime.timedelta(days=1),
                        stop_date=datetime.datetime.now(),
                        tags=[]):
        q = Query()

        if start_date is not None: q += { 'date': {'$gt': start_date} }
        if stop_date is not None: q += { 'date': {'$lt': stop_date} }
        if len(tags) > 0: q += {'$or': [ { 'tags': t } for t in tags ]}

        return self.__db.find_posts(q.query())

    def get_snippet(self, number):
        return self.__db.find_snippet({'number': number})

    def get_snippets(self, start_date=datetime.datetime.now() - datetime.timedelta(days=1),
                           stop_date=datetime.datetime.now(),
                           languages = [],
                           tags=[]):
        q = Query()

        if start_date is not None: q += { 'date': {'$gt': start_date} }
        if stop_date is not None: q += { 'date': {'$lt': stop_date} }
        if len(languages) > 0: q += {'$or': [ { 'language': l } for l in languages ]}
        if len(tags) > 0: q += {'$or': [ { 'tags': t } for t in tags ]}

        return self.__db.find_snippets(q.query())

    def get_posts_for_date(self, date=datetime.datetime.now(), tags=[]):
        start_date, stop_date = util.date_range(date)
        return self.get_posts(start_date=start_date, stop_date=stop_date, tags=tags)

    def get_snippets_for_date(self, date=datetime.datetime.now(), tags=[]):
        start_date, stop_date = util.date_range(date)
        return self.get_snippets(start_date=start_date, stop_date=stop_date, tags=tags)

    def add_post(self, title, content, tags):
        return self.__db.insert_post(Post(title=title, content=content, tags=tags))

    def add_snippet(self, title, extension, content, tags):
        return self.__db.insert_snippet(Snippet(title=title, extension=extension, content=content, tags=tags))

    def add_image(self, title, data, sha1, tags):
        return self.__db.insert_image(Image(title=title, sha1=sha1, content=data, tags=tags))

    def drop_post(self, number):
        return self.__db.delete_post(number)

    def drop_posts(self):
        return self.__db.delete_posts({})

    def drop_snippet(self, number):
        return self.__db.delete_snippet(number)

    def drop_snippets(self):
        return self.__db.delete_snippets({})

    def disconnect(self):
        return self.__db.disconnect()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
