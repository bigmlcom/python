# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2019 BigML, Inc
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
:date: Wed Apr 08, 2015-2019 17:52

"""

import csv

from bigml.util import PY3


class UnicodeReader(object):
    """Adapter to handle Python 2 to 3 conversion when reading files

    """
    def __init__(self, filename, dialect=csv.excel,
                 encoding="utf-8", **kwargs):
        """Constructor method for the reader

        """
        self.filename = filename
        self.dialect = dialect
        self.encoding = encoding
        self.kwargs = kwargs
        self.file_handler = None
        self.reader = None

    def open_reader(self):
        """Opening the file

        """
        if self.filename.__class__.__name__ == 'UTF8Recoder':
            self.file_handler = self.filename
        elif PY3:
            self.file_handler = open(self.filename, 'rt',
                                     encoding=self.encoding, newline='')
        else:
            self.file_handler = open(self.filename, 'rb')
        self.reader = csv.reader(self.file_handler, dialect=self.dialect,
                                 **self.kwargs)
        return self

    def __enter__(self):
        """Opening files

        """
        return self.open_reader()

    def __exit__(self, ftype, value, traceback):
        """Closing on exit

        """
        self.close_reader()

    def next(self):
        """Reading records

        """
        row = next(self.reader)
        if PY3:
            return row
        return [s.decode(self.encoding) for s in row]

    def __iter__(self):
        """Iterator

        """
        return self

    def close_reader(self):
        """Closing the file

        """
        if not self.filename.__class__.__name__ == 'UTF8Recoder':
            self.file_handler.close()


class UnicodeWriter(object):
    """Adapter to handle Python 2 to 3 conversion when writing to files

    """
    def __init__(self, filename, dialect=csv.excel,
                 encoding="utf-8", **kwargs):
        """Constructor method for the writer

        """
        self.filename = filename
        self.dialect = dialect
        self.encoding = encoding
        self.kwargs = kwargs
        self.file_handler = None
        self.writer = None

    def open_writer(self):
        """Opening the file

        """
        if PY3:
            self.file_handler = open(self.filename, 'wt',
                                     encoding=self.encoding, newline='')
        else:
            self.file_handler = open(self.filename, 'wb')
        self.writer = csv.writer(self.file_handler, dialect=self.dialect,
                                 **self.kwargs)
        return self

    def close_writer(self):
        """Closing the file

        """
        self.file_handler.close()

    def __enter__(self):
        """Opening the file

        """
        return self.open_writer()

    def __exit__(self, ftype, value, traceback):
        """Closing on exit

        """
        self.close_writer()

    def writerow(self, row):
        """Writer emulating CSV writerow

        """
        if not PY3:
            row = [(s if not isinstance(s, basestring) else
                    s.encode(self.encoding)) for s in row]
        self.writer.writerow(row)

    def writerows(self, rows):
        """Writer emulating CSV writerows

        """
        for row in rows:
            self.writerow(row)
