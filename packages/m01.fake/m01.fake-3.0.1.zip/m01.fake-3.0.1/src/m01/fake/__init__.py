##############################################################################
#
# Copyright (c) 2015 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests
$Id:$
"""
__docformat__ = 'restructuredtext'

import re
import doctest
import pprint as pp

import bson
import bson.son
import pymongo.cursor
from bson.py3compat import string_type

from m01.fake.collection import FakeCollection
from m01.fake.database import FakeDatabase
from m01.fake.cursor import FakeCursor
from m01.fake.client import FakeMongoClient

###############################################################################
#
# test helper methods
#
###############################################################################

# SON to dict converter
def dictify(data):
    """Recursive replace SON items with dict in the given data structure.

    Compared to the SON.to_dict method, this method will also handle tuples
    and keep them intact.

    """
    if isinstance(data, bson.son.SON):
        data = dict(data)
    if isinstance(data, dict):
        d = {}
        for k, v in data.items():
            # replace nested SON items
            d[k] = dictify(v)
    elif isinstance(data, (tuple, list)):
        d = []
        for v in data:
            # replace nested SON items
            d.append(dictify(v))
        if isinstance(data, tuple):
            # keep tuples intact
            d = tuple(d)
    else:
        d = data
    return d


def pprint(data):
    """Can pprint a bson.son.SON instance like a dict"""
    pp.pprint(dictify(data))


class RENormalizer(doctest.OutputChecker):
    """Normalizer which can convert text based on regex patterns"""

    def __init__(self, patterns):
        self.patterns = patterns
        self.transformers = list(map(self._cook, patterns))

    def __add__(self, other):
        if not isinstance(other, RENormalizing):
            return NotImplemented
        return RENormalizing(self.transformers + other.transformers)

    def _cook(self, pattern):
        if callable(pattern):
            return pattern
        regexp, replacement = pattern
        return lambda text: regexp.sub(replacement, text)

    def addPattern(self, pattern):
        patterns = list(self.patterns)
        patterns.append(pattern)
        self.transformers = map(self._cook, patterns)
        self.patterns = patterns

    def __call__(self, data):
        """Recursive normalize a SON instance, dict or text"""
        if not isinstance(data, string_type):
            data = pp.pformat(dictify(data))
        for normalizer in self.transformers:
            data = normalizer(dictify(data))
        return data

    def check_output(self, want, got, optionflags):
        if got == want:
            return True

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        return doctest.OutputChecker.check_output(self, want, got, optionflags)

    def output_difference(self, example, got, optionflags):

        want = example.want

        # If want is empty, use original outputter. This is useful
        # when setting up tests for the first time.  In that case, we
        # generally use the differencer to display output, which we evaluate
        # by hand.
        if not want.strip():
            return doctest.OutputChecker.output_difference(
                self, example, got, optionflags)

        # Dang, this isn't as easy to override as we might wish
        original = want

        for transformer in self.transformers:
            want = transformer(want)
            got = transformer(got)

        # temporarily hack example with normalized want:
        example.want = want
        result = doctest.OutputChecker.output_difference(
            self, example, got, optionflags)
        example.want = original

        return result

    def pprint(self, data):
        """Pretty print data"""
        if isinstance(data, (pymongo.cursor.Cursor, FakeCursor)):
            for item in data:
                print(self(item))
        else:
            print(self(data))


# see testing.txt for a sample usage
reNormalizer = RENormalizer([
    # python 3 unicode removed the "u".
    (re.compile("u('.*?')"), r"\1"),
    (re.compile('u(".*?")'), r"\1"),
    # dates
    (re.compile(u"(\d\d\d\d)-(\d\d)-(\d\d)[tT](\d\d):(\d\d):(\d\d)"),
                r"NNNN-NN-NNTNN:NN:NN"),
    (re.compile(u"(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d)"),
                r"NNNN-NN-NN NN:NN:NN"),
    (re.compile("ObjectId\(\'[a-zA-Z0-9]+\'\)"), r"ObjectId('...')"),
    (re.compile("Timestamp\([a-zA-Z0-9, ]+\)"), r"Timestamp('...')"),
    (re.compile("datetime\([a-z0-9, ]+\)"), "datetime(...)"),
    # replace pymongo FixedOffset with UTC
    (re.compile("tzinfo=<bson.tz_util.FixedOffset[a-zA-Z0-9 ]+>\)"),
                "tzinfo=UTC)"),
    (re.compile("object at 0x[a-zA-Z0-9]+"), "object at ..."),
    # remove Fake from class name
    (re.compile('FakeMongoClient'), 'MongoClient'),
    (re.compile('FakeDatabase'), 'Database'),
    (re.compile('FakeCollection'), 'Collection'),
    # mongo client attrs
    (re.compile(', document_class=dict'), ''),
    (re.compile(', tz_aware=True'), ''),
    (re.compile(', tz_aware=False'), ''),
    (re.compile(', connect=True'), ''),
    (re.compile(', connect=False'), ''),
    # class representation
    (re.compile("MongoClient(host=['127.0.0.1:27017'])"),
        "MongoClient(host=['localhost:45017'])"),
    (re.compile("MongoClient('localhost', 27017)"),
        "MongoClient(host=['localhost:27017'])"),
    (re.compile("45017"), "27017"),
    (re.compile("localhost"), "127.0.0.1"),
   ])


def getObjectId(secs=0):
    """Knows how to generate similar ObjectId based on integer (counter)

    Note: this method can get used if you need to define similar ObjectId
    in a non persistent environment if need to bootstrap mongo containers.
    """
    return bson.ObjectId(("%08x" % secs) + "0" * 16)


# single shared MongoClient instance
fakeMongoClient = FakeMongoClient()
