#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

import json

from simple_model import Model, Attribute, AttributeList

import cms.util as util

class CMSData(Model):
    __allow_missing__ = True
    version = Attribute(str, fallback='1')
    date = Attribute(util.parse_date, fallback=util.now)
    tags = AttributeList(str, fallback=[])
    number = Attribute(int, nullable=True)
    title = Attribute(str)

class Post(CMSData):
    content = Attribute(str)

class Image(CMSData):
    content = Attribute(bin)
    sha1 = Attribute(util.hash_file)

class Snippet(CMSData):
    extension = Attribute(str)
    content = Attribute(str)

def serialize(model):
    return json.dumps(model.__attributes__(), default=util.serialize_date)

# def deserialize(obj):
#     try:
#         return json.dumps(obj)
#     except TypeError as e:
#         try:
#             return util.deserialize_date(obj)
#         except TypeError:
#             if not isinstance(obj, CMSData):
#                 raise e
#
#             return obj.__attributes__()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
