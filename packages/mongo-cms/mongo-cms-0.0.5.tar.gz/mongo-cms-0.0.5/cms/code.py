#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

"""

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

class CodeSnippet(object):
    def __init__(self, string):
        self.content = string

    def __str__(self):
        return self.content.strip()

    def html(self, extension):
        try:
            lexer = get_lexer_for_filename(extension)
            return highlight(self.content.strip(), PythonLexer(), HtmlFormatter()).strip()
        except ClassNotFound:
            return self.content

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
