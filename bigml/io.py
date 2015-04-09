# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 BigML, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""Python 2/3 compatibility for I/O functions.

:author: jao <jao@bigml.com>
:date: Wed Apr 08, 2015 17:52

"""

import sys, csv

PY3 = sys.version > '3'

class UnicodeReader:
    def __init__(self, filename, dialect=csv.excel,
                 encoding="utf-8", **kw):
        self.filename = filename
        self.dialect = dialect
        self.encoding = encoding
        self.kw = kw

    def __enter__(self):
        if PY3:
            self.f = open(self.filename, 'rt',
                          encoding=self.encoding, newline='')
        else:
            self.f = open(self.filename, 'rb')
        self.reader = csv.reader(self.f, dialect=self.dialect,
                                 **self.kw)
        return self

    def __exit__(self, type, value, traceback):
        self.f.close()

    def next(self):
        row = next(self.reader)
        if PY3:
            return row
        return [s.decode("utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, filename, dialect=csv.excel,
                 encoding="utf-8", **kw):
        self.filename = filename
        self.dialect = dialect
        self.encoding = encoding
        self.kw = kw

    def open_writer(self):
        if PY3:
            self.f = open(self.filename, 'wt',
                          encoding=self.encoding, newline='')
        else:
            self.f = open(self.filename, 'wb')
        self.writer = csv.writer(self.f, dialect=self.dialect, **self.kw)
        return self

    def close_writer(self):
        self.f.close()

    def __enter__(self):
        return self.open_writer()

    def __exit__(self, type, value, traceback):
        self.close_writer()

    def writerow(self, row):
        if not PY3:
            row = [(s if not isinstance(s,basestring) else
                    s.encode(self.encoding)) for s in row]
        self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
