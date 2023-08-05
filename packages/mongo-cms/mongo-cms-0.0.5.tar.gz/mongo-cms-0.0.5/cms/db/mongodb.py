#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import logging

from pymongo import MongoClient, DESCENDING, ASCENDING

from cms.model import Post, Image, Snippet, CMSData

logger = logging.getLogger(__name__)

class MongoDB(object):
    def __init__(self, host, database):
        self.__client = MongoClient(host)
        self.__db = self.__client[database]

        self.__posts = self.__db.posts
        self.__images = self.__db.images
        self.__snippets = self.__db.snippets

    def _find_one(self, query, type, collection):
        logger.debug('querying one %s: %s', type, query)

        result = collection.find_one(query)

        return type(**result) if result else None

    def _find_many(self, query, type, collection):
        logger.debug('querying many %s: %s', type, query)

        return [ type(**d) for d in collection.find(query).sort("date", DESCENDING) ]

    def _find_newest(self, type, collection):
        result = collection.find_one({'number': { '$exists': True }}, sort=[("number", -1)])
        return type(**result) if result else None

    def _get_next_number(self, type, collection):
        newest = self._find_newest(type, collection)
        return newest.number + 1 if newest else 0

    def _insert(self, obj, collection):
        if not isinstance(obj, CMSData): raise TypeError(obj)

        logger.debug('inserting %s to %s', obj, collection)

        obj.number = self._get_next_number(type(obj), collection)

        return collection.insert_one(obj.__attributes__())

    def _delete_many(self, query, collection):
        logger.debug('deleting many from %s: %s', collection, query)

        return collection.delete_many(query)

    def _delete_one(self, query, collection):
        logger.debug('deleting one from %s: %s', collection, query)

        return collection.delete_one(query)

    def insert_post(self, post):
        self._insert(post, self.__posts)

    def insert_image(self, image):
        self._insert(image, self.__images)

    def insert_snippet(self, snippet):
        self._insert(snippet, self.__snippets)

    def find_posts(self, query):
        return self._find_many(query, Post, self.__posts)

    def find_images(self, query):
        return self._find_many(query, Image, self.__images)

    def find_snippets(self, query):
        return self._find_many(query, Snippet, self.__snippets)

    def find_post(self, query):
        return self._find_one(query, Post, self.__posts)

    def find_image(self, query):
        return self._find_one(query, Image, self.__images)

    def find_snippet(self, query):
        return self._find_one(query, Snippet, self.__snippets)

    def delete_post(self, number):
        return self._delete_one({'number': number}, self.__posts)

    def delete_snippet(self, number):
        return self._delete_one({'number': number}, self.__snippets)

    def delete_image(self, value):
        try:
            return self._delete_one({'number': int(sha1)}, self.__images)
        except ValueError:
            return self._delete_one({'sha1': (sha1)}, self.__images)

    def delete_posts(self, query):
        return self._delete_many(query, self.__posts)

    def delete_images(self, query):
        return self._delete_many(query, self.__images)

    def delete_snippets(self, query):
        return self._delete_many(query, self.__snippets)

    def disconnect(self):
        return self.__client.close()

    def status(self):
        try:
            self.__client.server_info()
            return True
        except Exception as e:
            return False

class Query(object):
    def __init__(self):
        self._query = {}

    def __add__(self, d):
        if d is not None:
            if '$and' not in self._query: self._query['$and'] = []
            self._query['$and'].append(d)
        return self

    def __or__(self, d):
        if d is not None:
            if '$or' not in self._query: self._query['$or'] = []
            self._query['$or'].append(d)
        return self

    def query(self):
        return self._query

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
