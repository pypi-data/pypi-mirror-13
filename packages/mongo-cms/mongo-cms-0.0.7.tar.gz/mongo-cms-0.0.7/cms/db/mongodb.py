#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import logging, re

from pymongo import MongoClient, DESCENDING, ASCENDING

import cms.model
from cms.model import CMSData

logger = logging.getLogger(__name__)

class MongoDB(object):
    def __init__(self, host, database):
        self.__client = MongoClient(host)
        self.__db = self.__client[database]

        self._posts = self.__db.posts
        self._images = self.__db.images
        self._snippets = self.__db.snippets

    def _find_one(self, query, type, collection):
        logger.debug('querying one %s: %s', type, query)

        result = collection.find_one(query)

        return type(**result) if result else None

    def _find_many(self, query, type, collection):
        logger.debug('querying many %s: %s', type, query)

        return [ type(**d) for d in collection.find(query).sort("date", DESCENDING) ]

    def _insert_one(self, obj, collection):
        if not isinstance(obj, CMSData): raise TypeError(obj)

        logger.debug('inserting %s to %s', obj, collection)

        obj.number = self._get_next_number(type(obj), collection)

        return collection.insert_one(obj.__attributes__())

    def _insert_many(self, objects, collection):
        logger.debug('inserting %s to %s', obj, collection)

        for obj in objects:
            yield self._insert_one(obj, collection)

    def _delete_one(self, query, collection):
        logger.debug('deleting one from %s: %s', collection, query)

        return collection.delete_one(query)

    def _delete_many(self, query, collection):
        logger.debug('deleting many from %s: %s', collection, query)

        return collection.delete_many(query)

    def _find_newest(self, type, collection):
        result = collection.find_one({'number': { '$exists': True }}, sort=[("number", -1)])
        return type(**result) if result else None

    def _get_next_number(self, type, collection):
        newest = self._find_newest(type, collection)
        return newest.number + 1 if newest else 0

    def __db_function__(self, method, data):
        data_name = data.rstrip('s')
        many = data.endswith('s')

        function_name = '_%s_%s' % (method, 'many' if many else 'one')
        collection_name = '_%ss' % data_name

        collection = object.__getattribute__(self, collection_name)
        function = object.__getattribute__(self, function_name)

        if method == 'insert':
            return lambda obj: function(obj, collection)
        elif method == 'find':
            data_type = getattr(cms.model, data_name.title())
            return lambda query: function(query, data_type, collection)
        elif method == 'delete':
            return lambda query: function(query, collection)

        raise AttributeError(method)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            match = re.match(r'(insert|find|delete)_([a-z]+)', name)
            if match:
                try:
                    return self.__db_function__(*(match.groups()))
                except Exception as new_exception:
                    logger.exception(new_exception)
                    logger.warning('matched the following groups: %s', match.groups())
            raise e

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
