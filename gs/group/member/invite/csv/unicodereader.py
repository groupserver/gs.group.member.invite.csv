# -*- coding: utf-8 -*-
# <http://docs.python.org/2.7/library/csv.html#csv.DictReader>
from __future__ import absolute_import, unicode_literals
from codecs import getreader
from csv import (DictReader, Sniffer, Error as CSVError)
from chardet.universaldetector import UniversalDetector
from gs.core import to_unicode_or_bust


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeDictReader(object):
    '''A variant of the :class:`csv.DictReader` class that handles Unicode

:param file f: The CSV file to process.
:param list cols: The column-names of the CSV, as strings in a list.
:param string dialect: The CSV dialect. If ``None`` then the dialect will be guessed.
:param string encoding: The encoding of the file. If ``None`` the encoding will be guessed. If
                        guessing fails then UTF-8 will be assumed.'''
    def __init__(self, f, cols, dialect=None, encoding=None, **kwds):
        e = self.guess_encoding(f) if encoding is None else encoding
        d = self.guess_dialect(f) if dialect is None else dialect
        f = UTF8Recoder(f, e)
        self.reader = DictReader(f, cols, dialect=d, **kwds)

    @staticmethod
    def guess_encoding(f):
        detector = UniversalDetector()
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        f.seek(0)  # The above read moves the file-cursor in the CSV file.
        detector.close()
        retval = detector.result['encoding'] if detector.result['encoding'] else 'utf-8'
        return retval

    @staticmethod
    def guess_dialect(f):
        # Taken from the Python standard docs, with thanks to Piers Goodhew <piers@u-h-p.com>
        # <https://docs.python.org/2/library/csv.html#csv.Sniffer>
        s = Sniffer()
        try:
            retval = s.sniff(f.read(1024), [',', '\t', ])  # 1024 taken from the Python docs
        except CSVError:
            retval = 'excel'
        finally:
            f.seek(0)  # The above f.read moves the file-cursor in the CSV file.
        return retval

    def next(self):
        row = self.reader.next()
        retval = {to_unicode_or_bust(k): to_unicode_or_bust(v) for k, v in row.items()}
        return retval

    def __iter__(self):
        return self
