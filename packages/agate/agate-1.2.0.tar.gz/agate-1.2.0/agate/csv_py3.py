#!/usr/bin/env python

"""
The classes and functions in this module serve as a replacement for Python 3's
core :mod:`csv` module on Python 3. These versions add several minor features.

If you are using Python 3, these classes and functions will automatically be
made available as part of the ``agate`` import. This means you can access them
by::

    from agate import DictReader

Or, if you want to use them as a drop-in replacement for :mod:`csv`::

    import agate as csv
"""

import csv

import six

class Reader(six.Iterator):
    """
    A wrapper around Python 3's builtin :func:`csv.reader`.
    """
    def __init__(self, f, **kwargs):
        self.reader = csv.reader(f, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.reader)

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num

class Writer(object):
    """
    A wrapper around Python 3's builtin :func:`csv.writer`.
    """
    def __init__(self, f, line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        self.writer = csv.writer(f, **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row.insert(0, 'line_number')
        else:
            row.insert(0, self.row_count)

        self.row_count += 1

    def writerow(self, row):
        if self.line_numbers:
            row = list(row)
            self._append_line_number(row)

        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = [i.replace('\r', '\n') if isinstance(i, six.string_types) else i for i in row]

        self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writer.writerow(row)

class DictReader(csv.DictReader):
    """
    A wrapper around Python 3's builtin :class:`csv.DictReader`.
    """
    pass

class DictWriter(csv.DictWriter):
    """
    A wrapper around Python 3's builtin :class:`csv.DictWriter`.
    """
    def __init__(self, f, fieldnames, line_numbers=False, **kwargs):
        self.row_count = 0
        self.line_numbers = line_numbers

        if 'lineterminator' not in kwargs:
            kwargs['lineterminator'] = '\n'

        if self.line_numbers:
            fieldnames.insert(0, 'line_number')

        csv.DictWriter.__init__(self, f, fieldnames, **kwargs)

    def _append_line_number(self, row):
        if self.row_count == 0:
            row['line_number'] = 'line_number'
        else:
            row['line_number'] = self.row_count

        self.row_count += 1

    def writerow(self, row):
        # Convert embedded Mac line endings to unix style line endings so they get quoted
        row = dict([(k, v.replace('\r', '\n')) if isinstance(v, six.string_types) else (k, v) for k, v in row.items()])

        if self.line_numbers:
            self._append_line_number(row)

        csv.DictWriter.writerow(self, row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def reader(*args, **kwargs):
    """
    A drop-in replacement for Python's :func:`csv.reader` that leverages
    :class:`.Reader`.
    """
    return Reader(*args, **kwargs)

def writer(*args, **kwargs):
    """
    A drop-in replacement for Python's :func:`csv.writer` that leverages
    :class:`.Writer`.
    """
    return Writer(*args, **kwargs)
